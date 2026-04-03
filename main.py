#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhoneManager 主入口 (GUI启动)
参考 docs/01-05: 加载config, 启动主窗口, import modules/ui
职责: 单一入口, 异常捕获, 日志初始化 (<200行), 批量导入 + 查询按钮
"""

import sys
import json
import logging
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QFileDialog)
from PyQt5.QtCore import Qt
from modules.recorder import Recorder
from modules.query import Query

def load_config(config_path: str = 'config/config.json') -> dict:
    """加载配置, 必填检查"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise ValueError(f"配置缺失: {config_path}")

def setup_logging(config: dict):
    """日志setup"""
    log_config = config['logging']
    Path(log_config['path']).parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_config['path'], encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PhoneManager")
    
    try:
        config = load_config()
        setup_logging(config)
        logging.info("PhoneManager 启动 (批量导入 + 查询 ready)")
        
        window = QWidget()
        window.setWindowTitle(config['app']['title'])
        layout = QVBoxLayout()
        
        label = QLabel("PhoneManager v1.0 - 批量电话管理\\n批量导入/查询号码按钮测试")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: blue;")
        layout.addWidget(label)
        
        btn_batch = QPushButton("批量导入 (xlsx/csv)")
        layout.addWidget(btn_batch)
        
        btn_query = QPushButton("查询号码 (xlsx/csv)")
        layout.addWidget(btn_query)
        
        def on_batch_import():
            file_path, _ = QFileDialog.getOpenFileName(
                window, "选择号码文件", "", "Excel/CSV (*.xlsx *.csv)"
            )
            if file_path:
                try:
                    r = Recorder()
                    result = r.add_batch(file_path)
                    msg = (f"导入完成!\\n"
                           f"新增: {result.get('new_count', 0)}\\n"
                           f"重复: {result.get('dup_count', 0)}\\n"
                           f"重复号码数: {len(result.get('dup_numbers', []))}\\n"
                           f"文件: {result.get('file', 'N/A')}")
                    QMessageBox.information(window, "批量结果", msg)
                except Exception as e:
                    QMessageBox.warning(window, "错误", f"导入失败: {str(e)}")
        
        btn_batch.clicked.connect(on_batch_import)
        
        def on_query_lookup():
            file_path, _ = QFileDialog.getOpenFileName(
                window, "选择查询文件", "", "Excel/CSV (*.xlsx *.csv)"
            )
            if file_path:
                try:
                    q = Query()
                    result = q.lookup_batch(file_path)
                    processed = result.get('processed', 0)
                    dups = sum(1 for r in result.get('results', []) if r.get('dup_count', 0) > 0)
                    msg = (f"查询完成!\\n"
                           f"处理: {processed}\\n"
                           f"有记录: {dups}\\n"
                           f"文件: {result.get('file', 'N/A')}")
                    QMessageBox.information(window, "查询结果", msg)
                except Exception as e:
                    QMessageBox.warning(window, "错误", f"查询失败: {str(e)}")
        
        btn_query.clicked.connect(on_query_lookup)
        
        window.setLayout(layout)
        window.resize(500, 350)
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"启动失败: {e}")
        QMessageBox.critical(None, "错误", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
