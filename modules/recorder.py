#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recorder module - batch/single phone dedup recorder
"""

import sqlite3
import json
import re
import pandas as pd
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from tqdm import tqdm

def load_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent / 'config' / 'config.json'
    try:
        with open(config_path) as f:
            return json.load(f)
    except:
        return {'database': {'path': '../database/data.db'}}

class Recorder:
    def __init__(self, db_path: str = None):
        self.config = load_config()
        self.db_path = Path(db_path or self.config['database']['path']).absolute()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS numbers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    batch_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def _clean_number(self, number: str) -> str:
        number = re.sub(r'[^\d]', '', str(number))
        if number.startswith('86'):
            number = number[2:]
        if len(number) in (11, 13):
            return number
        raise ValueError(f'Invalid number: {number}')

    def add_single_number(self, number: str, source: str) -> Dict[str, int]:
        try:
            clean_num = self._clean_number(number)
        except ValueError:
            return {'new_count': 0, 'dup_count': 0}
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute('SELECT 1 FROM numbers WHERE number = ?', (clean_num,))
            if cur.fetchone():
                conn.commit()
                return {'new_count': 0, 'dup_count': 1}
            cur.execute('INSERT INTO numbers (number, source) VALUES (?, ?)', (clean_num, source))
            conn.commit()
            return {'new_count': 1, 'dup_count': 0}

    def add_batch(self, file_path: str) -> Dict[str, Any]:
        fp = Path(file_path)
        if not fp.exists():
            return {'error': f'File not found: {file_path}'}
        
        dups = []
        new_count = 0
        
        if file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        numbers = df['number'].dropna().astype(str).tolist()
        
        with self._get_conn() as conn:
            cur = conn.cursor()
            existing = set(row[0] for row in cur.execute('SELECT number FROM numbers').fetchall())
            
            for num in tqdm(numbers, desc='Importing'):
                try:
                    clean_num = self._clean_number(num)
                    if clean_num in existing:
                        dups.append(clean_num)
                    else:
                        cur.execute('INSERT INTO numbers (number, source) VALUES (?, ?)', (clean_num, fp.stem))
                        new_count += 1
                        existing.add(clean_num)
                except ValueError:
                    pass
            
            conn.commit()
        
        return {
            'new_count': new_count,
            'dup_count': len(dups),
            'dup_numbers': dups[:10],  # first 10
            'file': file_path
        }
