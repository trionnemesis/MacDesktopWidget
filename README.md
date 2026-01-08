# MacDesktopWidget

MAC 桌面小工具應用程式，支援系統監控與 AI 整合功能。

## 🚀 功能特色

- 🖥️ **系統監控**: 即時顯示 CPU、記憶體使用率
- 🎨 **PyQt6 UI**: 現代化使用者介面，支援 QSS 自訂樣式
- 🤖 **LangChain 整合**: AI 驅動的智慧功能
- ⚡ **高效能**: 針對 Apple Silicon (M1/M2/M3) 優化
- 🔒 **安全第一**: Snyk 自動資安掃描
- 🧪 **測試覆蓋率**: ≥ 80% 的測試覆蓋

## 📋 技術棧

### Python 主要框架
- **PyQt6**: GUI 框架
- **QSS**: Qt 樣式表
- **psutil**: 系統資源監控
- **LangChain/LangGraph**: AI/LLM 整合
- **asyncio/QThread**: 非同步處理

### 多語言支援
- Python (主要)
- Rust (效能關鍵模組)
- Go (系統級操作)

## 🛠️ 開發流程

本專案採用 **SDD (Specification-Driven Development) + TDD (Test-Driven Development)** 流程：

1. **規格定義**: 先撰寫功能規格 (specs/)
2. **測試先行**: 根據規格撰寫測試
3. **實作**: 實作功能使測試通過
4. **Code Review**: 自動檢查程式碼品質與覆蓋率
5. **資安掃描**: Snyk 自動掃描漏洞
6. **版本發布**: 自動更新版本並發布到 GitHub

## 📦 安裝

### 前置需求

- Python 3.11+
- Rust 1.70+ (可選)
- Go 1.21+ (可選)
- Node.js 18+ (用於 Snyk CLI)

### 安裝步驟

```bash
# 克隆專案
git clone git@github.com:trionnemesis/MacDesktopWidget.git
cd MacDesktopWidget

# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝開發工具
pip install pytest pytest-cov pylint flake8 black mypy bandit

# 安裝 Snyk CLI
npm install -g snyk

# 設定環境變數（複製範本並填入實際值）
cp .env.example .env
# 編輯 .env 填入你的 SNYK_TOKEN
```

## 🧪 執行測試

```bash
# 執行所有測試
pytest

# 執行測試並生成覆蓋率報告
pytest --cov=src --cov-report=html

# 查看 HTML 報告
open htmlcov/index.html  # macOS
```

## 🔒 安全性

### Snyk 掃描

```bash
# 手動執行 Snyk 掃描
snyk test

# 掃描程式碼安全性
snyk code test src/

# 自動修復漏洞
snyk fix
```

### Git Hooks

本專案配置了自動化 hooks：

- **post-commit**: 自動執行 code review 與測試覆蓋率檢查
  - 覆蓋率未達 80% 會持續要求補充測試
- **pre-push**: 執行 Snyk 資安掃描
  - 發現 Critical/High 漏洞會阻止 push

## 📚 Skills 文件

專案包含以下自訂 skills（位於 `.claude/skills/`）：

1. **mac-dev-optimizer.md**: MAC 應用開發優化指南
2. **sdd-tdd-workflow.md**: SDD+TDD 開發流程
3. **code-review-coverage.md**: Code Review 與覆蓋率檢查
4. **snyk-security-check.md**: Snyk 資安檢查流程
5. **github-version-control.md**: GitHub 版本控制與發布

## 🏗️ 專案結構

```
MacDesktopWidget/
├── .claude/                    # Claude Code 配置
│   ├── skills/                # 自訂 skills
│   ├── hooks.json             # Hooks 配置
│   ├── mcp/                   # MCP Server 配置
│   └── scripts/               # 自動化腳本
├── src/                       # 原始碼
│   ├── python/               # Python 模組
│   ├── rust/                 # Rust 模組
│   └── go/                   # Go 模組
├── tests/                     # 測試
│   ├── unit/                 # 單元測試
│   ├── integration/          # 整合測試
│   └── fixtures/             # 測試資料
├── specs/                     # 功能規格文件
├── reports/                   # 測試與安全報告
├── .env                       # 環境變數（不提交到 Git）
├── .gitignore                # Git 忽略清單
├── VERSION                    # 版本號
└── README.md                  # 本檔案
```

## 🔖 版本控制

本專案遵循 [語義化版本](https://semver.org/lang/zh-TW/)：

- **MAJOR**: 不相容的 API 變更
- **MINOR**: 向下相容的功能新增
- **PATCH**: 向下相容的問題修復

當前版本: **v0.1.0**

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 撰寫規格文件 (specs/)
4. 撰寫測試（確保覆蓋率 ≥ 80%）
5. 實作功能
6. Commit 變更 (`git commit -m 'feat: add amazing feature'`)
7. Push 到分支 (`git push origin feature/amazing-feature`)
8. 開啟 Pull Request

### Commit Message 規範

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新功能
fix: 修復問題
docs: 文件更新
refactor: 重構
test: 測試相關
chore: 維護任務
```

## 📄 授權

待定

## 🙏 致謝

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Powered by [LangChain](https://github.com/langchain-ai/langchain)
- Security by [Snyk](https://snyk.io)
- Assisted by [Claude Code](https://claude.com/claude-code)

---

© 2026 MacDesktopWidget
