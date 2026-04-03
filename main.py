#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhoneManager 主入口 (GUI启动)
v1.1: +批量分配按钮
"""

import sys
import json
import logging
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt
from modules.recorder import Recorder
from modules.query import Query
from modules.assigner import Assigner

def load_config(config_path: str = 'config/config.json') -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"配置缺失: {config_path}")

def setup_logging(config: dict):
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
        logging.info("PhoneManager v1.1 启动 (导入/查询/分配)")
        
        window = QWidget()
        window.setWindowTitle(config['app']['title'])
        layout = QVBoxLayout()
        
        label = QLabel("PhoneManager v1.1 - 号码管理系统\\n导入/查询/分配全功能")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: blue; padding: 10px;")
        layout.addWidget(label)
        
        btn_import = QPushButton("1. 批量导入号码")
        layout.addWidget(btn_import)
        
        btn_query = QPushButton("2. 批量查询重复")
        layout.addWidget(btn_query)
        
        btn_assign = QPushButton("3. 批量分配 (默认sales)")
        layout.addWidget(btn_assign)
        
        def on_import():
            file_path, _ = QFileDialog.getOpenFileName(window, "选择导入文件", "", "Excel/CSV (*.xlsx *.csv)")
            if file_path:
                try:
                    r = Recorder()
                    result = r.add_batch(file_path)
                    msg = f"导入完成!\\n新增: {result.get('new_count', 0)}\\n重复: {result.get('dup_count', 0)}\\n重复号码: {len(result.get('dup_numbers', []))}\\n文件: {result.get('file', 'N/A')}"
                    QMessageBox.information(window, "导入结果", msg)
                except Exception as e:
                    QMessageBox.warning(window, "错误", str(e))
        
        btn_import.clicked.connect(on_import)
        
        def on_query():
            file_path, _ = QFileDialog.getOpenFileName(window, "选择查询文件", "", "Excel/CSV (*.xlsx *.csv)")
            if file_path:
                try:
                    q = Query()
                    result = q.lookup_batch(file_path)
                    processed = result.get('processed', 0)
                    dups = sum(1 for r in result.get('results', []) if r.get('dup_count', 0) > 0)
                    msg = f"查询完成!\\n处理: {processed}\\n有记录: {dups}\\n文件: {result.get('file', 'N/A')}"
                    QMessageBox.information(window, "查询结果", msg)
                except Exception as e:
                    QMessageBox.warning(window, "错误", str(e))
        
        btn_query.clicked.connect(on_query)
        
        def on_assign():
            file_path, _ = QFileDialog.getOpenFileName(window, "选择分配文件 (number列)", "", "Excel/CSV (*.xlsx *.csv)")
            if file_path:
                try:
                    a = Assigner()
                    result = a.assign_batch(file_path, 'sales')
                    msg = f"分配完成!\\n成功: {result.get('success', 0)}\\n失败: {result.get('fail', 0)}\\n文件: {result.get('file', 'N/A')}"
                    QMessageBox.information(window, "分配结果", msg)
                except Exception as e:
                    QMessageBox.warning(window, "错误", str(e))
        
        btn_assign.clicked.connect(on_assign)
        
        layout.addStretch()
        window.setLayout(layout)
        window.resize(500, 450)
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"启动失败: {e}")
        QMessageBox.critical(None, "错误", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()

