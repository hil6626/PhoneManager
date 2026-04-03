# Phase8 Release TODO (基于确认计划)

## 当前进度: 0/7

**全局顺序**: Phase1-7 完成 → Phase8 Release → 生产扩展。

**步骤清单** (逻辑顺序，确保无冲突/重复):
1. [x] tox -e py312 (8/8 pass, modules 修复完成)。
2. [ ] git add . && git commit -m 'blackboxai/phase8-release-prep' && git push (GHA 8pass)。
3. [ ] 检查/构建 dist/main (pyinstaller if missing), wine ./dist/main GUI30s + test_numbers.csv {'new':4 'dup':1}。
4. [ ] Windows VM: pyinstaller --onefile --windowed main.spec → dist/main.exe。
5. [ ] git tag v1.0.0 && gh release create v1.0.0 --title 'v1.0 Release' --notes 'ELF 75MB + docs' --assets dist/main docs/*.md。
6. [ ] Cleanup: rm -rf build dist tmp venv-* logs/*, git clean -fd (dry-run)。
7. [ ] Docs: 更新 README.md + docs/10_部署指南.md 引用 Phase8；rm Phase8_track.md。

**检查点**:
- 每步后更新 [x] + log。
- 防护: tox fail → deps pin；gh no auth → gh auth login。

**完成**: attempt_completion + 进度反馈。"
</xai:function_call >  
<xai:function_call name="execute_command">
<parameter name="command">which tox || pip install tox
