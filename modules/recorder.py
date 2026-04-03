#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recorder 模块 - 电话号码去重核心 (PhoneManager)

职责:
- 单条/批量录入号码，自动去重检测
- 记录批次、来源、时间，SQLite data.db 持久化
- 返回统计: 新增数/重复数/重复号码列表

部署顺序:
1. Stub 创建 (当前)
2. add_single_number 实现 (数据库插入+去重查重)
3. add_batch 实现 (pandas读取Excel/CSV + 批量去重)
4. 测试 + GUI集成 (main.py调用)

防护规则:
- 号码格式: 统一去除 +86/空格/-, 11-13位纯数字
- 数据库: data.db 自动建表 (numbers表: id|number UNIQUE|source|batch_id|created_at)
- 异常: 文件不存在/格式错返回空统计
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import pandas as pd
from tqdm import tqdm

class Recorder:
    def __init__(self, db_path: str = '../database/data.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """自动建表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                batch_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assign TEXT DEFAULT NULL
            )
        ''')
        conn.commit()
        # 兼容旧表添加assign列
        cursor.execute("PRAGMA table_info(numbers)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'assign' not in columns:
            cursor.execute('ALTER TABLE numbers ADD COLUMN assign TEXT DEFAULT NULL')
        conn.commit()
        conn.close()

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def add_single_number(self, number: str, source: str) -> Dict[str, int | List[str]]:
        """
        单条录入 + 去重检测 (完整实现)
        
        Args:
            number (str): 电话号码 e.g. "13800138000" or "+86 13800138000"
            source (str): 文档来源 e.g. "test_doc.xlsx"
            
        Returns:
            Dict: {"new_count": 1 or 0, "dup_count": 0 or 1, "dup_numbers": [] or [number]}
        """
        formatted_number = number.replace('+86', '').replace(' ', '').replace('-', '')
        if len(formatted_number) < 11 or not formatted_number.isdigit():
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': []}
        
        dup_numbers = []
        with self.get_conn() as conn:
            cursor = conn.cursor()
            # 检查重复
            cursor.execute('SELECT number FROM numbers WHERE number = ?', (formatted_number,))
            if cursor.fetchone():
                cursor.execute('SELECT number FROM numbers WHERE number = ?', (formatted_number,))
                dup_numbers = [row[0] for row in cursor.fetchall()]
                conn.commit()
                return {'new_count': 0, 'dup_count': 1, 'dup_numbers': dup_numbers}
            
            # 新增插入
            batch_id = f"{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cursor.execute(
                'INSERT INTO numbers (number, source, batch_id) VALUES (?, ?, ?)',
                (formatted_number, source, batch_id)
            )
            conn.commit()
        
        return {'new_count': 1, 'dup_count': 0, 'dup_numbers': []}

def add_batch(self, file_path: str) -> Dict[str, int | List[str] | str]:
        """
        批量导入 Excel/CSV + 去重
        
        Args:
            file_path (str): "data.xlsx" or "data.csv"
            
        Returns:
            同单条格式，但统计总数
            {'new_count': int, 'dup_count': int, 'dup_numbers': list[str], 'file': str}
            
        示例:
        >>> r.add_batch("phones.xlsx")
        {'new_count': 85, 'dup_count': 15, 'dup_numbers': ['13800138000'], 'file': 'phones.xlsx'}
        """
        if not file_path:
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': file_path}
            
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
        
        suffix = file_path_obj.suffix.lower()
        if suffix not in ['.xlsx', '.csv']:
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
        
        try:
            if file_path_obj.stat().st_size == 0:
                return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
        except (OSError, PermissionError) as e:
            print(f"File access error: {e}")
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
        
        try:
            if suffix == '.xlsx':
                df = pd.read_excel(file_path_obj)
            else:
                df = pd.read_csv(file_path_obj)
            
            if 'number' not in df.columns or df.empty or df['number'].dropna().empty:
                return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
            
            numbers = df['number'].dropna().astype(str).str.strip().tolist()
            print(f"Processing {len(numbers)} numbers from {file_path}")
            
            new_count = 0
            dup_count = 0
            dup_numbers = []
            
            for num_raw in tqdm(numbers, desc="Batch import"):
                if not num_raw:
                    continue
                result = self.add_single_number(num_raw, str(file_path_obj))
                new_count += result.get('new_count', 0)
                dup_count += result.get('dup_count', 0)
                dup_numbers.extend(result.get('dup_numbers', []))
            
            return {
                'new_count': new_count,
                'dup_count': dup_count,
                'dup_numbers': list(set(dup_numbers)),  # unique
                'file': str(file_path_obj)
            }
        except Exception as e:
            print(f"Batch import error: {e}")
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}

