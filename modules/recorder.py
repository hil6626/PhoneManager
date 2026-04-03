#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recorder 模块 - 电话号码去重核心 (PhoneManager)
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import json

class Recorder:
    def __init__(self, db_path=None):
        if db_path is None:
            try:
                with open('config/config
