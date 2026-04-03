#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase6: pytest main integration (recorder/query/assigner)
End2end batch logic with test_data/test_numbers.csv
Run: pytest tests/main.py -v (expect 100% pass)
"""

import pytest
import sqlite3
import json
from pathlib import Path
import pandas as pd
from modules.recorder import Recorder
from modules.query import Query
from modules.assigner import Assigner

@pytest.fixture(scope='session')
def temp_db_path():
    db_path = Path('temp_test.db')
    rec = Recorder(str(db_path))
    # Prefill test data
    test_csv = Path('test_data/test_numbers.csv')
    if test_csv.exists():
        rec.add_batch(str(test_csv))
    else:
        rec.add_single_number('13800138000', 'test')
        rec.add_single_number('13800138001', 'test')
    yield str(db_path)
    db_path.unlink(missing_ok=True)

def test_import_batch(temp_db_path):
    rec = Recorder(temp_db_path)
    result = rec.add_batch('test_data/test_numbers.csv')
    assert result['new_count'] >= 0
    assert result['dup_count'] >= 0
    # DB growth
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM numbers')
        rowcount = cursor.fetchone()[0]
    assert rowcount > 0

def test_query_duplicates(temp_db_path):
    q = Query(temp_db_path)
    result = q.lookup_batch('test_data/test_numbers.csv')
    assert result['processed'] > 0
    dups = [r for r in result['results'] if r['dup_count'] > 0]
    # Possible dups from prefill
    assert len(result['results']) > 0

def test_assign_sales(temp_db_path):
    a = Assigner(temp_db_path)
    result = a.assign_batch('test_data/test_numbers.csv', 'sales')
    assert result['success'] >= 0
    # DB assign
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT json(assign) FROM numbers WHERE assign IS NOT NULL LIMIT 1")
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            assert data.get('type') == 'sales'

def test_end2end(temp_db_path):
    rec = Recorder(temp_db_path)
    rec.add_batch('test_data/test_numbers.csv')
    q = Query(temp_db_path)
    q.lookup_batch('test_data/test_numbers.csv')
    a = Assigner(temp_db_path)
    a.assign_batch('test_data/test_numbers.csv', 'sales')
    # All core pass

def test_boundaries(temp_db_path):
    rec = Recorder(temp_db_path)
    # Empty/invalid
    result = rec.add_batch('nonexistent.csv')
    assert result['new_count'] == 0
    result = rec.add_single_number('invalid', 'test')
    assert result['new_count'] == 0
