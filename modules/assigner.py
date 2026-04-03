#!/usr/bin/env python3
# -*- coding: utf-8 -*-
&#34;&#34;&#34;
Assigner 模块 - 号码分配 (PhoneManager)

职责: 单条/批量将号码分配到类型(sales/marketing), 更新 numbers.assign JSON字段
复用: Recorder DB/get_conn/format logic

示例:
>>> from assigner import Assigner
>>> a = Assigner()
>>> print(a.assign_single(&#39;13800138000&#39;, &#39;sales&#39;))
{&#39;success&#39;: 1, &#39;fail&#39;: 0, &#39;phone&#39;: &#39;13800138000&#39;}
&#34;&#34;&#34;

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List
from pathlib import Path
import pandas as pd

class Assigner:
    def __init__(self, db_path: str = &#39;../database/data.db&#39;):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            print(f&#34;DB不存在: {self.db_path}&#34;)
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
        formatted = phone.replace(&#39;+86&#39;, &#39;&#39;).replace(&#39; &#39;, &#39;&#39;).replace(&#39;-&#39;, &#39;&#39;)
        return formatted if len(formatted) >= 11 and formatted.isdigit() else &#39;&#39;

    def _valid_type(self, type_str: str) -> bool:
        return type_str in [&#39;sales&#39;, &#39;marketing&#39;]

    def assign_single(self, phone: str, type_: str = &#39;sales&#39;) -> Dict[str, int | str]:
        &#34;&#34;&#34;
        单条分配: UPDATE numbers assign=JSON(type, assigned_at)
        Returns: {&#39;success&#39;:1/0, &#39;fail&#39;:0/1, &#39;phone&#39;:str, &#39;error&#39;:str|None}
        &#34;&#34;&#34;
        formatted = self._format_phone(phone)
        if not formatted:
            return {&#39;success&#39;: 0, &#39;fail&#39;: 1, &#39;phone&#39;: phone, &#39;error&#39;: &#39;无效号码&#39;}
        if not self._valid_type(type_):
            return {&#39;success&#39;: 0, &#39;fail&#39;: 1, &#39;phone&#39;: formatted, &#39;error&#39;: &#39;无效类型&#39;}

        with self.get_conn() as conn:
            if not conn:
                return {&#39;success&#39;: 0, &#39;fail&#39;: 1, &#39;phone&#39;: formatted, &#39;error&#39;: &#39;DB不可用&#39;}
            cursor = conn.cursor()
            assign_data = {
                &#39;type&#39;: type_,
                &#39;assigned_at&#39;: datetime.now().strftime(&#39;%Y-%m-%d %H:%M:%S&#39;)
            }
            cursor.execute(
                &#39;UPDATE numbers SET assign = ? WHERE number = ?&#39;,
                (json.dumps(assign_data), formatted)
            )
            if cursor.rowcount > 0:
                conn.commit()
                return {&#39;success&#39;: 1, &#39;fail&#39;: 0, &#39;phone&#39;: formatted}
            conn.rollback()
            return {&#39;success&#39;: 0, &#39;fail&#39;: 1, &#39;phone&#39;: formatted, &#39;error&#39;: &#39;号码不存在&#39;}

    def assign_batch(self, file_path: str, type_: str = &#39;sales&#39;) -> Dict[str, int | str]:
        &#34;&#34;&#34;
        批量分配
        Returns: {&#39;success&#39;:int, &#39;fail&#39;:int, &#39;file&#39;:str}
        &#34;&#34;&#34;
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {&#39;success&#39;: 0, &#39;fail&#39;: 0, &#39;file&#39;: str(file_path), &#39;error&#39;: &#39;文件不存在&#39;}
        
        suffix = path_obj.suffix.lower()
        if suffix not in [&#39;.xlsx&#39;, &#39;.csv&#39;]:
            return {&#39;success&#39;: 0, &#39;fail&#39;: 0, &#39;file&#39;: str(file_path), &#39;error&#39;: &#39;不支持格式&#39;}
        
        try:
            if suffix == &#39;.xlsx&#39;:
                df = pd.read_excel(path_obj)
            else:
                df = pd.read_csv(path_obj)
            
            if &#39;number&#39; not in df.columns:
                return {&#39;success&#39;: 0, &#39;fail&#39;: 0, &#39;file&#39;: str(file_path), &#39;error&#39;: &#39;无number列&#39;}
            
            numbers = df[&#39;number&#39;].dropna().astype(str).str.strip().tolist()
            success = 0
            fail = 0
            
            for num in numbers:
                if num:
                    result = self.assign_single(num, type_)
                    success += result[&#39;success&#39;]
                    fail += result[&#39;fail&#39;]
            
            return {&#39;success&#39;: success, &#39;fail&#39;: fail, &#39;file&#39;: str(file_path)}
        except Exception as e:
            return {&#39;success&#39;: 0, &#39;fail&#39;: 0, &#39;file&#39;: str(file_path), &#39;error&#39;: str(e)}

if __name__ == &#39;__main__&#39;:
    a = Assigner()
    print(a.assign_single(&#39;13800138000&#39;, &#39;sales&#39;))

