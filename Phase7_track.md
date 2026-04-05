# Phase7: Git & Release 部署跟踪

## 当前状态: 文档完善 (0/5完成)

**要点**: commit/push GHA → EXE onefile → docs更新 → 验证 → cleanup.

**步骤清单**:
1. [ ] Git add . && commit -m 'blackboxai/phase7-exe-ready' && push (触发GHA 8pass)
2. [ ] pyinstaller --onefile main.spec → dist/main.exe (50MB portable)
3. [ ] 验证: ./dist/main GUI 30s无Qt crash, test_numbers导入OK
4. [ ] 更新docs/10_部署指南.md + README.md (exe分发)
5. [ ] Cleanup: rm Phase7_track.md + build/dist旧文件

**检查点**:
- GHA: 8 jobs pass
- EXE: --help输出, DB auto-create
- Docs: 'exe分发'段存在

**防护规则**:
- Commit msg: str 'blackboxai/phase7'
- 边界: 无remote → git remote add
- 必填: main.spec binaries OK

**进度更新**: 编辑本文件标记[ x ]
