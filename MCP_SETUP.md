# Snyk MCP Server 設定指南

## ✅ 已完成配置

Snyk MCP Server 已經為您配置完成！

## 📦 配置檔案

### 1. `.mcp.json`（專案根目錄）
包含 Snyk MCP server 配置和您的 API token。

```json
{
  "mcpServers": {
    "snyk": {
      "command": "snyk",
      "args": ["mcp"],
      "env": {
        "SNYK_TOKEN": "fd6646b4-1e74-4fdb-a2c9-13f207c1a418"
      }
    }
  }
}
```

⚠️ **重要**: 此檔案已被 `.gitignore` 排除，**不會**提交到 Git，以保護您的 API token 安全。

### 2. `.claude/settings.local.json`
啟用專案級 MCP servers：

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": [
    "snyk"
  ]
}
```

### 3. `.mcp.json.example`（範本）
供其他開發者參考的配置範本（不含真實 token）。

## 🚀 啟用 MCP Server

### 前置需求

確保已安裝 Snyk CLI：

```bash
# 使用 npm 安裝
npm install -g snyk

# 或使用 Homebrew (macOS)
brew install snyk

# 驗證安裝
snyk --version
```

### 啟用步驟

1. **確認 Snyk CLI 支援 MCP**

```bash
# 檢查 Snyk 是否支援 mcp 子命令
snyk mcp --help
```

如果不支援，可能需要更新到最新版本：
```bash
npm update -g snyk
```

2. **重新啟動 Claude Code**

配置變更後，您需要：
- 退出 Claude Code（或關閉終端機）
- 重新啟動 Claude Code

3. **驗證 MCP Server 載入**

重新啟動後，可以詢問 Claude：

```
請檢查 Snyk MCP server 是否已載入
```

## 🔧 使用 Snyk MCP Server

### 可用功能

一旦 MCP server 載入成功，您可以通過 Claude Code 使用 Snyk 功能：

```
# 掃描專案依賴
請使用 Snyk 掃描專案的依賴漏洞

# 掃描程式碼安全性
使用 Snyk Code 檢查 src/ 目錄的安全問題

# 查看漏洞詳情
請顯示 Snyk 掃描結果的詳細資訊
```

### 與 Git Hooks 整合

專案已配置 Git hooks，會在 `pre-push` 階段自動執行 Snyk CLI 掃描：

```bash
# 手動執行 pre-push hook
.git/hooks/pre-push

# 或正常 push（會自動觸發）
git push
```

## 🔒 安全性

### Token 保護

✅ `.mcp.json` 已被 `.gitignore` 排除
✅ `.env` 也包含備份 token，同樣被排除
✅ 只有 `.mcp.json.example` 會被提交（不含真實 token）

### 驗證保護

```bash
# 確認 .mcp.json 不會被提交
git check-ignore -v .mcp.json

# 應顯示: .gitignore:76:*.json    .mcp.json
```

## 🐛 疑難排解

### 問題 1: Snyk CLI 未安裝

```bash
# 安裝 Snyk CLI
npm install -g snyk

# 驗證
snyk --version
```

### 問題 2: Snyk 不支援 MCP 子命令

Snyk 的 MCP 支援可能需要特定版本。如果 `snyk mcp` 不可用：

**替代方案 A**: 使用 Git Hooks（已配置）
```bash
# pre-push hook 使用 Snyk CLI 的標準命令
snyk test --severity-threshold=high
snyk code test src/
```

**替代方案 B**: 手動使用 Snyk CLI
```bash
# 依賴掃描
snyk test

# 程式碼掃描
snyk code test

# 生成報告
snyk test --json-file-output=snyk-report.json
```

### 問題 3: MCP Server 未載入

檢查配置：
```bash
# 檢查 .mcp.json 是否存在
cat .mcp.json

# 檢查 settings.local.json
cat .claude/settings.local.json
```

重新啟動 Claude Code 並檢查啟動訊息。

### 問題 4: Token 認證失敗

```bash
# 測試 token 是否有效
snyk auth fd6646b4-1e74-4fdb-a2c9-13f207c1a418

# 或手動設定
snyk config set api=fd6646b4-1e74-4fdb-a2c9-13f207c1a418
```

## 📚 相關文件

- **Snyk CLI 文件**: https://docs.snyk.io/snyk-cli
- **MCP 協議**: https://modelcontextprotocol.io/
- **專案 Snyk Skill**: `.claude/skills/snyk-security-check.md`

## 🎯 下一步

1. ✅ Snyk MCP server 已配置
2. 🔄 **請重新啟動 Claude Code**
3. ✅ Git hooks 已配置（自動掃描）
4. ✅ 開始使用！

---

配置完成！重新啟動 Claude Code 後即可使用 Snyk MCP server。🚀
