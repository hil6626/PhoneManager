#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared pytest fixtures for all tests
"""
import pytest
from pathlib import Path
from modules.recorder import Recorder


@pytest.fixture
def temp_db():
    """Create a temporary test database"""
    db_path = 'temp_test.db'
    rec = Recorder(db_path=str(Path(db_path).absolute()))
    # No init needed, DB creates on first use

    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_db(temp_db):
    """Create and pre-fill a test database with sample data"""
    rec = Recorder(db_path=temp_db)
    # Pre-fill with sample data for assigner/query tests
    rec.add_single_number('13800138000', 'test')
    return temp_db

