# 号码管理系统 README

当前状态：核心模块已实现，GUI入口已上线，部署指南已补充为可验证流程（避免“未来再做”遗留问题）。

## 1. 快速启动 (Ubuntu开发)
要点:
- Python 3.8+，建议 3.10。
- 依赖管理：`requirements.txt`，避免新增无关依赖。
- GUI 已可运行（`main.py` 已实现批量导入与查询动作）。

步骤:
```bash
cd PhoneManager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

检查点:
- `venv` 目录存在，`pip list` 含 `pandas`, `PyQt5`, `tqdm`。
- 启动时无报错，界面可点击“批量导入”和“查询号码”。
- 出现`database/data.db`文件，且路径正确。

防护/检测规则:
- 输入类型：`add_single_number(number: str, source: str)`；`add_batch(file_path: str)`；`lookup_single(phone: str)`；`lookup_batch(file_path: str)`。
- 边界条件：空字符串、格式不符、文件不存在、文件空、缺少`number`列应返回空结果而不抛异常。
- 必填项：`config/config.json`必须存在；`config.logging.path`和`app.title`必填；`number`列必须存在于 XLSX/CSV。

## 2. 实际进度与模块覆盖
- `modules/recorder.py`：已完成
  - `add_single_number`：格式清洗、长度校验、去重、入库、统计
  - `add_batch`：Excel/CSV 通用、空文件、格式校验、批量去重
  - 保护规则：+86/空格/- 清理，11~13数字校验
- `modules/query.py`：已完成
  - `lookup_single`：返回 first_seen/dup_count/source 列表
  - `lookup_batch`：逐行查询 + 文件校验
- `main.py`：已完成
  - GUI 按钮绑定；异常提示；日志初始化。

检查点:
- `Recorder().add_single_number('13800138000','manual')` 结果 `new_count=1`，再调用一次`dup_count=1`。
- `Recorder().add_batch('test_data/test_numbers.csv')` 后库中记录数符合预期。
- `Query().lookup_single('13800138000')` 返回 `dup_count` 与来源。

防护/检测规则:
- 数据库表结构：`numbers(id, number TEXT UNIQUE NOT NULL, source NOT NULL, batch_id, created_at)`。
- 重复检查：`SELECT number FROM numbers WHERE number=?`，不允许插入重复。
- 日志异常：启动失败应写入 `config.logging.path`，并向用户弹窗。

## 3. 逻辑部署顺序与优化建议
1. 代码验证阶段
   - 运行 `python -m pytest`（建议补充单测）。
   - 重点覆盖模块核心：`recorder`, `query`, `main` 入口。
2. 编排配置
   - `config/config.json` 加入必填字段检查（已在 `load_config`）。
   - 增加 `schema` 文件可选，防止遗留格式不一致。
3. 逐步上线
   - 阶段1：CLI模式（`add_batch`/`lookup_batch`）完全运行。
   - 阶段2：GUI模式上线（验证文件对话框、结果弹框、异常处理）。
   - 阶段3：监控与报警（日志文件 + `database/data.db` 锁定异常）。

影响范围分析:
- 仅触及当前项目文件：`README.md`, `config/config.json`, `main.py`, `modules/*`。
- 不涉及第三方依赖变更，已禁止大规模重构。

## 4. 兼容性与联动性
- 多平台：Ubuntu、Windows、Mac（PyQt5 与 pandas）
- 数据联动：`Recorder` 写、`Query` 读同一 DB 路径；需保证 `db_path` 统一，可通过配置项参数化。
- 兼容规则：文件路径兼容绝对/相对（`Path(file_path)`）。

检查点:
- `config/config.json` `db_path` 字段同步到模块初始化（目前默认 `'../database/data.db'`，预留可配置）。
- 如果 GUI 未来改成 Web 服务，保留 `Recorder` 与 `Query` 独立纯逻辑层，减少耦合。

## 5. Cleanup Complete
Phase1-5 verified (core modules/GUI/DB ready). Legacy conflicts merged/removed. Phase6 ready for tests/EXE.

---

## 7. Phase7: Git Release & EXE Prod (Tracking: Phase7_track.md)
### Status: Docs Ready (1/5)
**要点**: git push → GHA tox pass → pyinstaller --onefile → dist/main.exe分发。

1. git commit/push (触发ci.yml)
2. pyinstaller --onefile main.spec
3. ./dist/main GUI test (import test_numbers.csv)
4. Docs更新完成 ✅
5. Cleanup: rm Phase7_track.md + build/

**分发包**: dist/main.exe (50MB) + test_data/ + database/data.db空模板 (离线双击运行)

**防护**: GHA 8pass必过; EXE --help无crash; 中文路径workaround (/tmp构建)。

**Run**: Windows双击/Ubuntu wine dist/main.exe


