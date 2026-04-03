# Phase8: Release 部署跟踪

## 当前状态: 0/6完成

**要点**：tox GHA → git → wine test → Windows cross → tag release → cleanup。

**步骤清单**：
1. [ ] tox -e py312 (8 tests pass) or GHA push check。
2. [ ] git add . && commit -m 'blackboxai/phase7-complete-dbparam-docs' && push (GHA 8pass)。
3. [ ] wine ./dist/main GUI30s + test_numbers.csv {'new':4 'dup':1}。
4. [ ] Windows VM pyinstaller --onefile --windowed main.spec → dist/main.exe。
5. [ ] git tag v1.0 && gh release create v1.0 'dist/main Linux ELF + docs'。
6. [ ] Cleanup: rm -rf build dist tmp venv-* logs, keep Phase8_track.md。

**检查点**：
- tox: 100% pass。
- wine: no Qt/numpy crash。
- Release: assets download ELF75MB。
- Docs: Phase8 ref in README/docs/10。

**防护规则**：
- Commit: str 'blackboxai/phase'.
- tox fail: requirements pin numpy=1.26.4。
- gh: auth gh auth login。

**优化**：
- 顺序: tox→git→wine→cross→release→clean。
- 影响: <50行 docs/git。
