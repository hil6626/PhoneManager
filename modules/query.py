#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query module - Phone number lookup (PhoneManager)

Responsibility: Single/batch lookup first_seen, dup_count, sources (read-only)
DB config param
"""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import json

class Query:
    def __init__(self, db_path=None):
        if db_path is None:
            try:
                with open('config/config
