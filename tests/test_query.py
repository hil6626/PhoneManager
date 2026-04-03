#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from modules.query import Query

@pytest.fixture
def sample_db(temp_db):  # 假设 recorder test 后 db 有数据
    pass  # 用 recorder fixture 预填数据

def test_lookup_single(sample_db):
    q = Query(sample_db)
    result = q.lookup_single('13800138000')
    assert 'dup_count' in result
    assert isinstance(result['dup_count'], int)

# 类似 batch/invalid

