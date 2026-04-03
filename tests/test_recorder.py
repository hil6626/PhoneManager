#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import sqlite3
from pathlib import Path
import pandas as pd
from modules.recorder import Recorder

def test_add_single_new(temp_db):
    rec = Recorder(temp_db)
    result = rec.add_single_number('13800138000', 'test')
    assert result['new_count'] == 1
    assert result['dup_count'] == 0

def test_add_single_dup(temp_db):
    rec = Recorder(temp_db)
    rec.add_single_number('13800138000', 'test')
    result = rec.add_single_number('13800138000', 'test')
    assert result['new_count'] == 0
    assert result['dup_count'] == 1

def test_add_batch(temp_db):
    df = pd.DataFrame({'number': ['13800138001', '13800138000', 'invalid']})
    df.to_csv('temp_batch.csv', index=False)
    rec = Recorder(temp_db)
    result = rec.add_batch('temp_batch.csv')
    assert result['new_count'] >= 1
    assert result['dup_count'] == 0  # 取决于顺序
    Path('temp_batch.csv').unlink()

def test_invalid_phone(temp_db):
    rec = Recorder(temp_db)
    result = rec.add_single_number('abc', 'test')
    assert result['new_count'] == 0

