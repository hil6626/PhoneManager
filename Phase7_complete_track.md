# Phase7 Complete & Optimize Track (Single Source)

## 当前进度: 1/8 (Prior EXE numpy fix complete, DB param/docs统一)

**要点**: Prior numpy spec/venv fix → docs统一 → DB config param → git/clean。

**步骤清单**:
1. [x] Prior main.spec numpy hiddenimports + venv numpy1.26.4 rebuild dist/main 75MB (unpack/lib OK)
2. [ ] Update Phase7_track.md → this file (merge TODO/prior, Phase1-7 full清单)
3. [ ] Edit README.md: 第3/7节引用this，remove duplicate
4. [ ] Edit docs/10: add Linux ELF分发/test
5. [ ] Edit modules/*.py: DB path from config.json
6. [ ] Test: python main.py + EXE run (GUI30s+csv {'new':4 'dup':1})
7. [ ] Git commit 'phase7-complete-docs-dbparam'
8. [ ] Cleanup: rm TODO.md Phase7_track.md old build/ + this mark complete

**Phase1-7 Full Deployment Checklist** (逻辑顺序):
Phase1: core recorder.py (add_single/batch) → test CLI new/dup
Phase2: query.py (lookup) → test lookup_single/batch
Phase3: assigner.py (assign) → test assign_batch
Phase4: DB schema/log config.json → sqlite3 verify
Phase5: GUI main.py + ui/widgets → python main.py GUI test
Phase6: CI tox.ini GHA + main.spec → tox/pyinstaller build
Phase7: git push → EXE test → docs → param config → release

**检查点**:
- dist/main 75MB ./main GUI no crash/error, csv import OK
- Recorder(Query,Assigner).db_path = config.database.path
- Phase7_track.md/TODO.md rm, README引用this
- GHA pass, git commit 'phase7-complete'

**防护规则**:
- Config load: json KeyError→default db '../database/data.db'
- DB path: Path str, rel/abs, mkdir exist_ok
- Numpy: venv numpy1.26.4 pandas2.1.1 no dtype error
- Input: config db.path str len>0, file exist for test
- 边界: no config→default; invalid path→ValueError log

**更新**：每步 [x] + log。
