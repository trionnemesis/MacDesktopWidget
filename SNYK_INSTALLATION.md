# Snyk CLI 安裝指南

## 📦 安裝 Snyk CLI

### Windows

#### 方式 1: 使用 npm（推薦）

```bash
# 安裝 Node.js（如果尚未安裝）
# 下載: https://nodejs.org/

# 全域安裝 Snyk CLI
npm install -g snyk

# 驗證安裝
snyk --version
```

#### 方式 2: 使用 Scoop

```bash
scoop install snyk
```

#### 方式 3: 下載執行檔

1. 前往 https://github.com/snyk/cli/releases
2. 下載 `snyk-win.exe`
3. 重命名為 `snyk.exe`
4. 移動到 PATH 中的目錄（例如 `C:\Windows\System32`）

### macOS

#### 方式 1: 使用 Homebrew（推薦）

```bash
brew install snyk
```

#### 方式 2: 使用 npm

```bash
npm install -g snyk
```

### Linux

#### 使用 npm

```bash
npm install -g snyk
```

#### 使用 Snap

```bash
snap install snyk
```

## 🔑 認證 Snyk

安裝完成後，可使用瀏覽器登入完成認證。若使用 API token，請使用您自己的有效 token，並透過本機環境變數提供；不要將真實 token 放入文件、範本或命令列。

```bash
# 透過瀏覽器認證，不在命令列中包含 token
snyk auth
```

## ✅ 驗證安裝

```bash
# 檢查版本
snyk --version

# 測試掃描（在專案目錄）
snyk test

# 檢查 MCP 支援（如有）
snyk mcp --help
```

## 📝 環境變數設定

為了確保 Git hooks 能正確使用 Snyk，建議設定環境變數：

### Windows

#### PowerShell（目前工作階段）
```powershell
# 隱藏輸入；token 不會出現在輸入的命令或持久化設定中
$token = Read-Host 'Snyk token' -AsSecureString
$env:SNYK_TOKEN = [System.Net.NetworkCredential]::new('', $token).Password
Remove-Variable token
```

### macOS/Linux（Bash，目前工作階段）

```bash
# 在 Bash 中隱藏輸入，避免把 token 寫入命令歷史
read -r -s -p "Snyk token: " SNYK_TOKEN
printf '\n'
export SNYK_TOKEN
```

請從設定環境變數的同一終端機啟動 Snyk 或 Claude Code，讓子程序繼承 `SNYK_TOKEN`。環境變數中的 token 仍是敏感資料，不要輸出或提交它。

### 本機 `.env` 範例（可選）

`.env` 已被 `.gitignore` 排除。以下只是佔位值，必須在本機換成您自己的有效 token：

```dotenv
SNYK_TOKEN=your_snyk_token_here
```

Snyk CLI 不會自行載入專案的 `.env`；使用前需由您啟動的 shell 或工具載入。不要把真實 token 寫入 `.env.example`。

## 🧪 測試 Snyk 功能

安裝完成後，測試各項功能：

### 1. 基本掃描

```bash
# 掃描當前專案
cd /path/to/MacDesktopWidget
snyk test
```

### 2. 依賴掃描

```bash
# Python
snyk test --file=requirements.txt

# Rust
snyk test --file=Cargo.toml

# Go
snyk test --file=go.mod
```

### 3. 程式碼安全掃描

```bash
# 掃描程式碼
snyk code test src/

# 設定嚴重性門檻
snyk code test src/ --severity-threshold=high
```

### 4. 生成報告

```bash
# JSON 報告
snyk test --json > snyk-report.json

# HTML 報告
snyk test --json | snyk-to-html -o snyk-report.html
```

## 🔧 Git Hooks 測試

驗證 pre-push hook 是否能正確執行 Snyk：

```bash
# 手動執行 pre-push hook
.git/hooks/pre-push

# 應該會：
# 1. 檢查 Snyk CLI 是否安裝
# 2. 載入 SNYK_TOKEN
# 3. 執行依賴掃描
# 4. 執行程式碼掃描
# 5. 生成報告
```

## 📊 預期輸出

成功安裝後，執行 `snyk --version` 應該顯示：

```
1.1234.0 (或更新版本)
```

執行 `snyk test` 應該開始掃描專案依賴。

## 🐛 常見問題

### 問題 1: npm 未安裝

**解決方案**: 先安裝 Node.js
- Windows: https://nodejs.org/
- macOS: `brew install node`
- Linux: `sudo apt install nodejs npm`

### 問題 2: 權限錯誤

**Windows**:
```bash
# 以管理員身分執行 PowerShell
npm install -g snyk
```

**macOS/Linux**:
```bash
sudo npm install -g snyk
```

### 問題 3: snyk 命令找不到

檢查 PATH：
```bash
# Windows (PowerShell)
$env:Path -split ';'

# macOS/Linux
echo $PATH | tr ':' '\n'
```

確保 npm 全域目錄在 PATH 中：
```bash
npm config get prefix
```

### 問題 4: Token 認證失敗

```bash
# 清除舊配置
snyk config clear

# 透過瀏覽器重新認證，不輸出已儲存的 token
snyk auth

# 若設定了 SNYK_TOKEN，請確認該環境變數提供的是您自己的有效 token
```

## 🎯 安裝檢查清單

- [ ] Node.js 已安裝
- [ ] Snyk CLI 已安裝
- [ ] `snyk --version` 成功執行
- [ ] Snyk token 已認證
- [ ] `snyk test` 能正常掃描
- [ ] 環境變數 SNYK_TOKEN 已設定
- [ ] Git hooks 能執行 Snyk
- [ ] Claude Code MCP server 已配置

## 🚀 下一步

完成安裝後：

1. ✅ 執行 `snyk test` 驗證功能
2. ✅ 測試 pre-push hook: `.git/hooks/pre-push`
3. ✅ 重新啟動 Claude Code 載入 MCP server
4. ✅ 開始使用！

詳細的 MCP 配置說明請參考 `MCP_SETUP.md`。
