#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query module - Phone number lookup (PhoneManager)

Responsibility: Single/batch lookup first_seen, dup_count, sources (read-only)
Reuses: Recorder DB path/get_conn/phone format logic

CLI test:
python3 -c "from modules.query import Query; q=Query(); print(q.lookup_single('13800138000'))"

Returns:
lookup_single: {'phone': str, 'first_seen': str|None, 'dup_count': int, 'sources': list[str]}
lookup_batch: {'results': list[dict], 'processed': int, 'file': str}
"""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd

class Query:
    def __init__(self, db_path: str = '../database/data.db'):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            # Graceful handle for CLI test, no raise during dev
            self.db_path = None

    @contextmanager
    def get_conn(self):
        if not self.db_path or not self.db_path.exists():
            yield None
            return
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _format_phone(self, phone: str) -> str:
        "Format: remove +86/space/-, keep 11+ digits"
        formatted = phone.replace('+86', '').replace(' ', '').replace('-', '')
        return formatted if len(formatted) >= 11 and formatted.isdigit() else ''

    def lookup_single(self, phone: str) -> Dict[str, Optional[str] | int | List[str]]:
        "Single lookup"
        formatted = self._format_phone(phone)
        if not formatted:
            return {'phone': phone, 'first_seen': None, 'dup_count': 0, 'sources': []}

        with self.get_conn() as conn:
            if not conn:
                return {'phone': formatted, 'first_seen': None, 'dup_count': 0, 'sources': []}
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    MIN(created_at) as first_seen,
                    COUNT(*) as dup_count,
                    GROUP_CONCAT(DISTINCT source) as sources
                FROM numbers 
                WHERE number = ?
            ''', (formatted,))
            result = cursor.fetchone()

        if result and result[2]:
            return {
                'phone': formatted,
                'first_seen': result[0],
                'dup_count': result[1],
                'sources': result[2].split(',') if result[2] else []
            }
        return {'phone': formatted, 'first_seen': None, 'dup_count': 0, 'sources': []}

    def lookup_batch(self, file_path: str) -> Dict[str, List[Dict] | int | str]:
        "Batch lookup"
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {'results': [], 'processed': 0, 'file': str(file_path)}

        suffix = path_obj.suffix.lower()
        if suffix not in ['.xlsx', '.csv']:
            return {'results': [], 'processed': 0, 'file': str(file_path)}

        try:
            if suffix == '.xlsx':
                df = pd.read_excel(path_obj)
            else:
                df = pd.read_csv(path_obj)

            if 'number' not in df.columns or df.empty or df['number'].dropna().empty:
                return {'results': [], 'processed': 0, 'file': str(file_path)}

            numbers = df['number'].dropna().astype(str).str.strip().tolist()
            results = [self.lookup_single(num) for num in numbers if num]

            return {
                'results': results,
                'processed': len(numbers),
                'file': str(file_path)
            }
        except Exception:
            return {'results': [], 'processed': 0, 'file': str(file_path)}

if __name__ == '__main__':
    q = Query()
    print(q.lookup_single('13800138000'))
