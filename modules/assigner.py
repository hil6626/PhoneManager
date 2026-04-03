#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assigner module - Batch phone assignment to groups (update source)
"""

import sqlite3
import json
import pandas as pd
from typing import Dict, Any
from pathlib import Path
from contextlib import contextmanager
from modules.query import Query

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'config.json'
    try:
        with open(config_path) as f:
            return json.load(f)
    except:
        return {'database': {'path': '../database/data.db'}}

class Assigner:
    def __init__(self, db_path: str = None):
        self.config = load_config()
        self.db_path = Path(db_path or self.config['database']['path']).absolute()
        self.query = Query(str(self.db_path))
        self._init_db()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
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

    def assign_single(self, number: str, group: str) -> Dict[str, int]:
        clean_num = ''.join(filter(str.isdigit, number))
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute('UPDATE numbers SET source = ? WHERE number = ?', (group, clean_num))
            success = cur.rowcount
            conn.commit()
        return {'success': success, 'fail': 1 - success}

    def assign_batch(self, group: str, file_path: str) -> Dict[str, int]:
        fp = Path(file_path)
        if not fp.exists():
            return {'assigned': 0, 'not_found': 0}
        
        if file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        numbers = df['number'].dropna().astype(str).tolist()
        assigned = 0
        not_found = 0
        
        with self._get_conn() as conn:
            cur = conn.cursor()
            for num in numbers:
                clean_num = ''.join(filter(str.isdigit, num))
                cur.execute('UPDATE numbers SET source = ? WHERE number = ?', (group, clean_num))
                if cur.rowcount:
                    assigned += 1
                else:
                    not_found += 1
            conn.commit()
        
        return {'assigned': assigned, 'not_found': not_found}
