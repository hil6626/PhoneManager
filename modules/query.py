#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query module - Phone number lookup (PhoneManager)

Responsibility: Single/batch lookup first_seen, dup_count, sources (read-only)
DB config param
"""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
import json

def load_config() -> Dict:
    config_path = Path(__file__).parent.parent / 'config' / 'config.json'
    try:
        with open(config_path) as f:
            return json.load(f)
    except:
        return {'database': {'path': '../database/data.db'}}

class Query:
    def __init__(self, db_path: str = None):
        self.config = load_config()
        self.db_path = Path(db_path or self.config['database']['path']).absolute()
    
    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def lookup_single(self, phone: str) -> Dict[str, Any]:
        clean_phone = ''.join(filter(str.isdigit, phone))
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT number, source, created_at, 
                       (SELECT COUNT(*) FROM numbers n2 WHERE n2.number = n1.number) as dup_count
                FROM numbers n1 WHERE number = ? ORDER BY created_at
            ''', (clean_phone,))
            rows = cur.fetchall()
        if not rows:
            return {'error': 'Not found', 'dup_count': 0}
        return {
            'number': rows[0][0],
            'sources': [r[1] for r in rows],
            'first_seen': rows[0][2],
            'dup_count': rows[0][3],
            'all_records': len(rows)
        }

    def lookup_batch(self, file_path: str) -> Dict[str, List[Dict]]:
        fp = Path(file_path)
        if not fp.exists():
            return {'error': 'File not found'}
        if file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        results = []
        for _, row in df.iterrows():
            phone = str(row.get('number', ''))
            if phone:
                results.append(self.lookup_single(phone))
        return {'results': results}
