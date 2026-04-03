#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from modules.query import Query

def test_lookup_single(sample_db):
    q = Query(sample_db)
    result = q.lookup_single('13800138000')
    assert 'dup_count' in result
    assert isinstance(result['dup_count'], int)

# 类似 batch/invalid

