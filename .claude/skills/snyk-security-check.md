# Snyk 資安檢查 Skill

## 描述
在 `pre-push` 階段使用 Snyk 進行全面資安掃描，檢查依賴套件漏洞、程式碼安全性與容器映像檔。整合 Snyk MCP Server 實現自動化檢查。

## 觸發條件
- **自動觸發**：每次 `git push` 前
- **手動觸發**：執行 `/security-check` 指令
- **Hook 機制**：透過 `pre-push` hook

## Snyk MCP Server 配置

### 認證資訊
- **API Token**: `fd6646b4-1e74-4fdb-a2c9-13f207c1a418`
- **儲存位置**: 環境變數（不可提交到 Git）

### MCP Server 設定

建立 `.claude/mcp/snyk-config.json`：

```json
{
  "mcpServers": {
    "snyk": {
      "command": "snyk",
      "args": ["mcp"],
      "env": {
        "SNYK_TOKEN": "fd6646b4-1e74-4fdb-a2c9-13f207c1a418"
      },
      "description": "Snyk 安全性掃描服務"
    }
  }
}
```

### 環境變數設定

```bash
# .env 檔案（加入 .gitignore）
SNYK_TOKEN=fd6646b4-1e74-4fdb-a2c9-13f207c1a418

# 或在系統環境變數設定
export SNYK_TOKEN="fd6646b4-1e74-4fdb-a2c9-13f207c1a418"
```

## Snyk 檢查項目

### 1️⃣ 依賴套件漏洞掃描

#### Python 依賴掃描

```bash
# 安裝 Snyk CLI
npm install -g snyk

# 認證
snyk auth $SNYK_TOKEN

# 掃描 requirements.txt
snyk test --file=requirements.txt --severity-threshold=high

# 掃描並生成報告
snyk test --json --json-file-output=snyk-report.json

# 修復建議
snyk wizard
```

**掃描範圍：**
- ✅ PyQt6 及其依賴
- ✅ psutil
- ✅ LangChain/LangGraph
- ✅ asyncio 相關套件
- ✅ 所有 dev dependencies

#### Rust 依賴掃描

```bash
# 掃描 Cargo.toml
snyk test --file=Cargo.toml --severity-threshold=high

# 同時使用 cargo-audit
cargo audit --deny warnings
```

#### Go 依賴掃描

```bash
# 掃描 go.mod
snyk test --file=go.mod --severity-threshold=high

# 使用 govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...
```

### 2️⃣ 程式碼安全性掃描

#### Python 程式碼掃描

```bash
# Snyk Code 掃描
snyk code test src/ \
    --severity-threshold=high \
    --json-file-output=snyk-code-report.json

# 檢查項目：
# - SQL Injection
# - XSS
# - 硬編碼密鑰
# - 不安全的反序列化
# - 路徑遍歷
```

**常見漏洞檢測：**

```python
# ❌ 不安全：SQL Injection 風險
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 安全：使用參數化查詢
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# ❌ 不安全：硬編碼密鑰
API_KEY = "abc123456789"

# ✅ 安全：從環境變數讀取
API_KEY = os.getenv("API_KEY")

# ❌ 不安全：命令注入風險
os.system(f"ls {user_input}")

# ✅ 安全：使用 subprocess 並驗證輸入
subprocess.run(["ls", sanitized_input], check=True)
```

#### Rust 程式碼掃描

```bash
# Snyk Code 掃描
snyk code test src/ --language=rust

# RustSec 漏洞檢查
cargo audit
```

#### Go 程式碼掃描

```bash
# Snyk Code 掃描
snyk code test . --language=go

# Gosec 安全掃描
gosec ./...
```

### 3️⃣ 容器映像檔掃描（如有使用）

```bash
# 掃描 Docker 映像檔
snyk container test python:3.11-slim \
    --file=Dockerfile \
    --severity-threshold=high

# 掃描並監控
snyk container monitor python:3.11-slim
```

### 4️⃣ 授權合規性檢查

```bash
# 檢查依賴套件授權
snyk test --license-policy=.snyk-license-policy.json

# 生成授權報告
snyk test --json | jq '.vulnerabilities[].license' | sort | uniq
```

**授權政策範例** (`.snyk-license-policy.json`)：

```json
{
  "version": "v1.0.0",
  "license": {
    "deny": ["GPL-3.0", "AGPL-3.0"],
    "approve": ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"]
  }
}
```

## 漏洞嚴重性等級

### 處理規則

| 嚴重性 | 說明 | 處理方式 |
|-------|------|---------|
| 🔴 **Critical** | 可直接利用的高危漏洞 | ❌ 阻止 push |
| 🟠 **High** | 嚴重安全問題 | ❌ 阻止 push |
| 🟡 **Medium** | 中等風險 | ⚠️  警告但允許 |
| 🟢 **Low** | 低風險 | ℹ️  記錄但不警告 |

### 阻止條件

```bash
# 有 Critical 或 High 漏洞時阻止 push
snyk test --severity-threshold=high || {
    echo "❌ 發現高危漏洞，阻止 push"
    echo "📋 請先修復以下問題："
    snyk test --json | jq '.vulnerabilities[] | select(.severity=="critical" or .severity=="high")'
    exit 1
}
```

## pre-push Hook 腳本

建立 `.git/hooks/pre-push`：

```bash
#!/bin/bash
# pre-push: Snyk 資安檢查

set -e

echo "🔒 開始 Snyk 資安掃描..."

# 檢查 Snyk CLI 是否安裝
if ! command -v snyk &> /dev/null; then
    echo "❌ Snyk CLI 未安裝"
    echo "請執行: npm install -g snyk"
    exit 1
fi

# 載入環境變數
if [ -f ".env" ]; then
    export $(cat .env | grep SNYK_TOKEN | xargs)
fi

# 檢查認證
if [ -z "$SNYK_TOKEN" ]; then
    echo "❌ SNYK_TOKEN 未設定"
    echo "請在 .env 檔案中設定 SNYK_TOKEN"
    exit 1
fi

snyk auth $SNYK_TOKEN

# 1. 依賴套件掃描
echo "📦 掃描依賴套件..."

if [ -f "requirements.txt" ]; then
    echo "  → 掃描 Python 依賴..."
    snyk test --file=requirements.txt \
        --severity-threshold=high \
        --json-file-output=reports/snyk-python-deps.json || {
        echo "❌ Python 依賴發現高危漏洞"
        snyk test --file=requirements.txt --severity-threshold=high
        exit 1
    }
fi

if [ -f "Cargo.toml" ]; then
    echo "  → 掃描 Rust 依賴..."
    snyk test --file=Cargo.toml --severity-threshold=high || {
        echo "❌ Rust 依賴發現高危漏洞"
        exit 1
    }
    cargo audit --deny warnings || {
        echo "❌ cargo-audit 發現漏洞"
        exit 1
    }
fi

if [ -f "go.mod" ]; then
    echo "  → 掃描 Go 依賴..."
    snyk test --file=go.mod --severity-threshold=high || {
        echo "❌ Go 依賴發現高危漏洞"
        exit 1
    }
fi

# 2. 程式碼安全性掃描
echo "🔍 掃描程式碼安全性..."

if [ -d "src/" ]; then
    snyk code test src/ \
        --severity-threshold=high \
        --json-file-output=reports/snyk-code.json || {
        echo "❌ 程式碼發現高危安全問題"
        snyk code test src/ --severity-threshold=high
        exit 1
    }
fi

# 3. 授權合規性檢查
echo "⚖️  檢查授權合規性..."

if [ -f ".snyk-license-policy.json" ]; then
    snyk test --license-policy=.snyk-license-policy.json || {
        echo "⚠️  發現不合規的授權"
    }
fi

# 4. 生成安全報告
echo "📄 生成安全報告..."

mkdir -p reports

cat > reports/security-summary.md <<EOF
# Snyk 安全掃描報告

生成時間: $(date)
Commit: $(git rev-parse --short HEAD)

## ✅ 掃描結果

- [x] 依賴套件掃描完成
- [x] 程式碼安全性掃描完成
- [x] 授權合規性檢查完成

## 📊 漏洞統計

EOF

# 統計漏洞數量
if [ -f "reports/snyk-python-deps.json" ]; then
    CRITICAL=$(cat reports/snyk-python-deps.json | jq '[.vulnerabilities[] | select(.severity=="critical")] | length')
    HIGH=$(cat reports/snyk-python-deps.json | jq '[.vulnerabilities[] | select(.severity=="high")] | length')
    MEDIUM=$(cat reports/snyk-python-deps.json | jq '[.vulnerabilities[] | select(.severity=="medium")] | length')
    LOW=$(cat reports/snyk-python-deps.json | jq '[.vulnerabilities[] | select(.severity=="low")] | length')

    cat >> reports/security-summary.md <<EOF
### Python 依賴
- 🔴 Critical: $CRITICAL
- 🟠 High: $HIGH
- 🟡 Medium: $MEDIUM
- 🟢 Low: $LOW

EOF
fi

echo "✅ Snyk 資安檢查完成！"
echo "📋 詳細報告: reports/security-summary.md"

exit 0
```

**設定執行權限：**

```bash
chmod +x .git/hooks/pre-push
```

## Claude Code Hook 配置

在 `.claude/hooks.json` 中配置：

```json
{
  "pre-push": {
    "command": ".git/hooks/pre-push",
    "blocking": true,
    "description": "Snyk 資安掃描（阻止高危漏洞 push）"
  }
}
```

## 漏洞修復流程

### 自動修復

```bash
# Snyk 自動修復（Python）
snyk fix

# 生成修復 PR（需要連接 GitHub）
snyk monitor
```

### 手動修復

1. **識別漏洞**：
   ```bash
   snyk test --json | jq '.vulnerabilities[] | {package: .name, version: .version, severity: .severity, fix: .fixedIn}'
   ```

2. **更新套件**：
   ```bash
   # Python
   pip install --upgrade package-name

   # Rust
   cargo update package-name

   # Go
   go get -u package-name
   ```

3. **驗證修復**：
   ```bash
   snyk test --severity-threshold=high
   ```

## 持續監控

### 設定 Snyk 專案監控

```bash
# 將專案加入 Snyk 監控
snyk monitor

# 每日自動掃描
# 在 Snyk 網頁介面設定：
# https://app.snyk.io/org/your-org/projects
```

### GitHub 整合

```bash
# 安裝 Snyk GitHub App
# https://github.com/apps/snyk-io

# 自動 PR 檢查
# 每個 PR 都會自動執行 Snyk 掃描
```

## 忽略特定漏洞

如果某個漏洞需要暫時忽略（需謹慎使用）：

建立 `.snyk` 檔案：

```yaml
# Snyk (https://snyk.io) policy file

version: v1.25.0

ignore:
  'SNYK-PYTHON-REQUESTS-12345':
    - '*':
        reason: 'False positive - not applicable to our use case'
        expires: '2026-02-09T00:00:00.000Z'
```

## 報告格式

```markdown
# Snyk 安全掃描報告

## 📋 基本資訊
- **掃描時間**: 2026-01-09 10:30:00
- **Commit**: abc1234
- **專案**: MacDesktopWidget

## 📊 漏洞統計

### Python 依賴
- 🔴 Critical: 0
- 🟠 High: 0
- 🟡 Medium: 2
- 🟢 Low: 5

### Rust 依賴
- 🔴 Critical: 0
- 🟠 High: 0
- 🟡 Medium: 0
- 🟢 Low: 1

### 程式碼安全性
- 🔴 Critical: 0
- 🟠 High: 0
- 🟡 Medium: 1
- 🟢 Low: 3

## ✅ 檢查結果
- [x] 無 Critical 漏洞
- [x] 無 High 漏洞
- [x] 授權合規性通過
- [x] 可以安全 push

## 📝 建議改進
1. 升級 package-A 至 v2.0.0 修復 Medium 漏洞
2. 重構 src/auth.py:45 避免潛在的注入風險
```

## 執行指令

```bash
# 手動執行完整掃描
/security-check

# 只掃描依賴
/security-check deps

# 只掃描程式碼
/security-check code

# 生成詳細報告
/security-check --report

# 嘗試自動修復
/security-check --fix
```

## 安全性最佳實踐

1. ✅ **永遠不要提交 API Token 到 Git**
2. ✅ **定期更新依賴套件**
3. ✅ **啟用 Snyk 持續監控**
4. ✅ **審查自動修復建議再套用**
5. ✅ **設定嚴格的授權政策**
6. ✅ **對 Critical/High 漏洞零容忍**
