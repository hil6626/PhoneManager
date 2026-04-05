#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assigner 模块 - 号码分配 (PhoneManager)

职责: 单条/批量将号码分配到类型(sales/marketing), 更新 numbers.assign JSON字段
复用: Recorder DB/get_conn/format logic

示例:
>>> from assigner import Assigner
>>> a = Assigner()
>>> print(a.assign_single('13800138000', 'sales'))
{'success': 1, 'fail': 0, 'phone': '13800138000'}
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List
from pathlib import Path
import pandas as pd

class Assigner:
    def __init__(self, db_path: str = '../database/data.db'):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            print(f"DB不存在: {self.db_path}")
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
        formatted = phone.replace('+86', '').replace(' ', '').replace('-', '')
        return formatted if len(formatted) >= 11 and formatted.isdigit() else ''

    def _valid_type(self, type_str: str) -> bool:
        return type_str in ['sales', 'marketing']

    def assign_single(self, phone: str, type_: str = 'sales') -> Dict[str, int | str]:
        """
        单条分配: UPDATE numbers assign=JSON(type, assigned_at)
        Returns: {'success':1/0, 'fail':0/1, 'phone':str, 'error':str|None}
        """
        formatted = self._format_phone(phone)
        if not formatted:
            return {'success': 0, 'fail': 1, 'phone': phone, 'error': '无效号码'}
        if not self._valid_type(type_):
            return {'success': 0, 'fail': 1, 'phone': formatted, 'error': '无效类型'}

        with self.get_conn() as conn:
            if not conn:
                return {'success': 0, 'fail': 1, 'phone': formatted, 'error': 'DB不可用'}
            cursor = conn.cursor()
            assign_data = {
                'type': type_,
                'assigned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            cursor.execute(
                'UPDATE numbers SET assign = ? WHERE number = ?',
                (json.dumps(assign_data), formatted)
            )
            if cursor.rowcount > 0:
                conn.commit()
                return {'success': 1, 'fail': 0, 'phone': formatted}
            conn.rollback()
            return {'success': 0, 'fail': 1, 'phone': formatted, 'error': '号码不存在'}

    def assign_batch(self, file_path: str, type_: str = 'sales') -> Dict[str, int | str]:
        """
        批量分配
        Returns: {'success':int, 'fail':int, 'file':str}
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {'success': 0, 'fail': 0, 'file': str(file_path), 'error': '文件不存在'}
        
        suffix = path_obj.suffix.lower()
        if suffix not in ['.xlsx', '.csv']:
            return {'success': 0, 'fail': 0, 'file': str(file_path), 'error': '不支持格式'}
        
        try:
            if suffix == '.xlsx':
                df = pd.read_excel(path_obj)
            else:
                df = pd.read_csv(path_obj)
            
            if 'number' not in df.columns:
                return {'success': 0, 'fail': 0, 'file': str(file_path), 'error': '无number列'}
            
            numbers = df['number'].dropna().astype(str).str.strip().tolist()
            success = 0
            fail = 0
            
            for num in numbers:
                if num:
                    result = self.assign_single(num, type_)
                    success += result['success']
                    fail += result['fail']
            
            return {'success': success, 'fail': fail, 'file': str(file_path)}
        except Exception as e:
            return {'success': 0, 'fail': 0, 'file': str(file_path), 'error': str(e)}

if __name__ == '__main__':
    a = Assigner()
    print(a.assign_single('13800138000', 'sales'))

