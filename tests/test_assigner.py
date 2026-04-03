#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import pandas as pd
from pathlib import Path
from modules.assigner import Assigner

def test_assign_single_success(sample_db):
    a = Assigner(db_path=str(Path(sample_db).absolute()))
    result = a.assign_single('13800138000', 'sales')
    assert result['success'] == 1

def test_assign_invalid():
    a = Assigner()
    result = a.assign_single('abc', 'sales')
    assert result['fail'] == 1

def test_assign_batch(sample_db):
    df = pd.DataFrame({'number': ['13800138001']})
    df.to_csv('temp_assign.csv', index=False)
    a = Assigner(db_path=str(Path(sample_db).absolute()))
    result = a.assign_batch('temp_assign.csv', 'marketing')
    Path('temp_assign.csv').unlink()
    # Assert based on DB state

