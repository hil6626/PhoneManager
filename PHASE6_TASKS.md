# Phase6 执行详细任务文档 (EXE部署 & 验证)
创建时间: 当前 | 路径: PhoneManager/PHASE6_TASKS.md

## 项目状态快照
- Core: recorder/query/assigner健壮 (batch/single, error dict返回)
- GUI: main.py 3按钮绑定, config.json ready
- Tests: 3独立pytest文件 (需main.py整合, fixture temp_db)
- PyInstaller: tmpvenv ready, main.spec datas含test_data/database
- DB: data.db numbers表 UNIQUE number + assign JSON

## 详细待执行任务列表 (顺序执行, 每个确认通过)
### 1. 测试验证 (Python层, ~10min)
   - **创建**: PhoneManager/tests/main.py (150行 pytest end2end)
     - Fixture: temp_db = Recorder('temp.db') + prefill test_numbers.csv (4 nums)
     - Tests:
       | 测试名 | 输入 | Assert |
       |--------|------|--------|
       | test_import_batch | add_batch(csv) | new_count>0, DB rowcount>=4 |
       | test_query_duplicates | lookup_batch(csv) | dup_count>0, sources list |
       | test_assign_sales | assign_batch(csv,'sales') | success>0, DB json(assign)['type']=='sales' |
       | test_end2end | chain + log | coverage>80%, log keywords |
       | boundaries | invalid/empty | new=0/fail=1 |
     - **命令预览**: pytest tests/main.py -v (expect 100% pass)
   - **检查点**: pytest report 全pass前跳过
   - **防护**: temp_db unlink; CSV number col存在

### 2. PyInstaller打包 (EXE生成, ~5min)
   - **激活venv**: cd PhoneManager && source tmpvenv/bin/activate
   - **构建**: tmpvenv/bin/pyinstaller main.spec
     - spec确认: onefile=False? console=False, datas=test_data/database/config/resources, hiddenimports=pandas/numpy/PyQt5/sqlite3
   - **检查点**: ls dist/PhoneManager.exe (50-100MB), no build/ crash
   - **防护**: backup data.db; --clean if retry

### 3. EXE全流程验证 (manual, ~10min)
   - **运行**: ./dist/PhoneManager.exe
     1. Import test_data/test_numbers.csv → popup new/dup counts
     2. Query same csv → popup processed/dups
     3. Assign same 'sales' → success popup
   - **DB/log检查**:
     ```bash
     sqlite3 database/data.db \"SELECT COUNT(*), json(assign) FROM numbers WHERE assign LIKE '%sales%' GROUP BY 1\"
     ls -lh logs/*.log  # <10MB, keywords '导入完成'
     ```
   - **检查点**: data.db更新, logs生成, GUI no crash
   - **防护**: run前 cp data.db data.db.bak; empty logs/

### 4. DB优化 & 清理 (~2min)
   - **维护**:
     ```bash
     sqlite3 database/data.db \"VACUUM; CREATE INDEX IF NOT EXISTS idx_number ON numbers(number); CREATE INDEX IF NOT EXISTS idx_assign ON numbers(assign);\"
     ```
   - **清理**: rm -rf tmpvenv/ .pytest_cache/ build/ (keep dist/)
   - **检查点**: db size降, indexes exist (`sqlite3 .schema`)

### 5. Git & 文档收尾 (~5min)
   - **分支**: git checkout -b blackboxai/phase6
   - **commit**: git add . && git commit -m \"Phase6: tests/main.py + EXE deploy ready + README Phase6\"
   - **README.md追加** (30行):
     ```
     ## Phase6: Windows EXE分发
     1. pyinstaller main.spec → dist/PhoneManager.exe (50MB self-contained)
     2. Copy dist/ + config/database空db + test_data/
     3. Double-click run, full GUI/CLI (import csv → query → assign sales)
     CLI dev: python main.py
     ```
   - **检查点**: git status clean, no TODO遗留

## 整体时间/难度: 30min 低 | 生产可分发性: 高 (EXE独立)
## 冲突避免: 无重构, 仅新增tests/main.py + README + git
## 执行追踪: 每步后更新此文件打✅, 或用TODO.md同步

**下一步: 用户确认 → 执行1.create tests/main.py → pytest → ...**

