#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recorder 模块 - 电话号码去重核心 (PhoneManager)
v1.0: add_single_number + add_batch 完整
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
        formatted_number = number.replace('+86', '').replace(' ', '').replace('-', '')
        if len(formatted_number) < 11 or not formatted_number.isdigit():
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': []}
        
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT number FROM numbers WHERE number = ?', (formatted_number,))
            if cursor.fetchone():
                return {'new_count': 0, 'dup_count': 1, 'dup_numbers': [formatted_number]}
            
            batch_id = f"{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cursor.execute(
                'INSERT INTO numbers (number, source, batch_id) VALUES (?, ?, ?)',
                (formatted_number, source, batch_id)
            )
            conn.commit()
        
        return {'new_count': 1, 'dup_count': 0, 'dup_numbers': []}

    def add_batch(self, file_path: str) -> Dict[str, int | List[str] | str]:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
        
        suffix = file_path_obj.suffix.lower()
        if suffix not in ['.xlsx', '.csv']:
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
        
        try:
            if suffix == '.xlsx':
                df = pd.read_excel(file_path_obj)
            else:
                df = pd.read_csv(file_path_obj)
            
            if 'number' not in df.columns:
                return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path)}
            
            numbers = df['number'].dropna().astype(str).str.strip().tolist()
            
            new_count = 0
            dup_count = 0
            dup_numbers = []
            
            for num_raw in tqdm(numbers, desc="Importing"):
                if num_raw:
                    result = self.add_single_number(num_raw, str(file_path_obj.name))
                    new_count += result['new_count']
                    dup_count += result['dup_count']
                    dup_numbers.extend(result['dup_numbers'])
            
            return {
                'new_count': new_count,
                'dup_count': dup_count,
                'dup_numbers': list(set(dup_numbers)),
                'file': str(file_path_obj)
            }
        except Exception as e:
            return {'new_count': 0, 'dup_count': 0, 'dup_numbers': [], 'file': str(file_path), 'error': str(e)}

if __name__ == '__main__':
    r = Recorder()
    print(r.add_single_number('13800138000', 'test'))

