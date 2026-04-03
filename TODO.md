# Phase6: CI & PyInstaller Fix (Approved: tox + GHA + spec)
创建时间: 当前 | 步骤跟踪

## 执行步骤 (逻辑顺序: CI先 -> Packager后 -> 测试EXE)
- [ ] 1. Create tox.ini (pytest CI for py312, with PYTHONPATH=.)
  - 要点: 本地多env测试, 隔离venv
  - 检查点: tox -e py312 → 5 passed
  - 防护: [tox] envlist=py312; [testenv] deps=pytest; PYTHONPATH=.
- [✅] 2. Edit main.spec (add PyQt5 plugins via binaries/datas)
  - 要点: 修复 non-ASCII Qt path
  - 检查点: pyinstaller main.spec → no plugin error
  - 防护: Analysis(binaries=[('venv/lib/python3.12/site-packages/PyQt5/Qt5/plugins', 'PyQt5/Qt5/plugins')])
- [✅] 3. Create .github/workflows/ci.yml (GitHub Actions: tox + pytest)
  - 要点: Cloud CI, on push/PR
  - 检查点: Push → GHA runs green
  - 防护: jobs: test: runs-on: ubuntu-latest; pip install tox; tox -e py312
- [✅] 4. Test pyinstaller from ASCII dir (cd /tmp && pyinstaller ../main.spec) - 构建成功，路径修复（/tmp无venv）
  - 要点: Avoid Chinese path crash
  - 检查点: dist/main runs OK
  - 防护: Short path /tmp/PhoneManager copy if needed
- [ ] 5. git add/commit -m 'blackboxai/ci-pyinstaller-fix'
- [x] 6. Prev: pytest 5 passed

**优化建议**: 
- 影响: 只加3文件, <100行, 无重构.
- 部署顺序: tox(local) -> GHA(cloud) -> spec(pack) -> ASCII exe test -> Phase7 EXE onefile.
- 难度: 低 (tox install via pip).

**Phase7 Docs完成** [Phase7_track.md 1/5 ✅]: docs/10 + README.exe分发 | 待git/push/EXE

**规则**: 每步后 tox --recreate; no conflicts with venv.

