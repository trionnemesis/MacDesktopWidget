# Code Review 與覆蓋率檢查 Skill

## 描述
在 `post-commit` 階段自動觸發 code review 與測試覆蓋率計算。確保程式碼品質、安全性與測試完整性。

## 觸發條件
- **自動觸發**：每次 `git commit` 後
- **手動觸發**：執行 `/code-review` 指令
- **Hook 機制**：透過 `post-commit` hook

## Code Review 檢查項目

### 1️⃣ 程式碼品質檢查

#### Python (PyQt6) Linting

```bash
# 安裝工具
pip install pylint flake8 black mypy

# Pylint 檢查
pylint src/ --fail-under=8.0

# Flake8 風格檢查
flake8 src/ --max-line-length=100 --ignore=E203,W503

# Black 格式化檢查
black --check src/

# MyPy 型別檢查
mypy src/ --strict
```

**檢查標準：**
- [ ] Pylint 評分 ≥ 8.0/10
- [ ] 無 Flake8 錯誤
- [ ] 符合 Black 格式
- [ ] 通過 MyPy 型別檢查

#### Rust Linting

```bash
# Clippy 檢查
cargo clippy -- -D warnings

# 格式化檢查
cargo fmt --check

# 安全性檢查
cargo audit
```

**檢查標準：**
- [ ] 無 Clippy 警告
- [ ] 符合 rustfmt 格式
- [ ] 無已知安全漏洞

#### Go Linting

```bash
# 安裝工具
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Linting 檢查
golangci-lint run ./...

# 格式化檢查
gofmt -l .

# Vet 檢查
go vet ./...
```

**檢查標準：**
- [ ] 無 golangci-lint 錯誤
- [ ] 符合 gofmt 格式
- [ ] 通過 go vet 檢查

### 2️⃣ 複雜度分析

#### 程式碼複雜度限制
- **循環複雜度 (Cyclomatic Complexity)**: ≤ 10
- **認知複雜度 (Cognitive Complexity)**: ≤ 15
- **函式長度**: ≤ 50 行
- **類別長度**: ≤ 300 行

#### Python 複雜度檢查

```bash
# 安裝 radon
pip install radon

# 循環複雜度
radon cc src/ -a -nb

# 可維護性指數
radon mi src/ -nb
```

#### Rust 複雜度檢查

```bash
# 安裝 cargo-geiger (不安全程式碼檢測)
cargo install cargo-geiger

# 檢查
cargo geiger
```

### 3️⃣ 安全性檢查

#### 常見漏洞檢查
- [ ] SQL Injection
- [ ] XSS (Cross-Site Scripting)
- [ ] 硬編碼密碼/金鑰
- [ ] 不安全的隨機數生成
- [ ] 路徑遍歷漏洞

#### Python 安全性工具

```bash
# 安裝 bandit
pip install bandit

# 安全性掃描
bandit -r src/ -f json -o security-report.json
```

#### 敏感資訊檢測

```bash
# 檢查是否有洩露的 API Key、密碼等
grep -r -E "(api[_-]?key|password|secret|token).*=.*['\"][^'\"]{8,}['\"]" src/
```

### 4️⃣ 依賴檢查

#### Python 依賴檢查

```bash
# 安裝 pip-audit
pip install pip-audit

# 檢查已知漏洞
pip-audit
```

#### Rust 依賴檢查

```bash
cargo audit
```

#### Go 依賴檢查

```bash
go list -m all | nancy sleuth
```

## 測試覆蓋率計算

### 覆蓋率門檻規則

**硬性要求：**
- **整體覆蓋率**: ≥ 80%
- **新增程式碼覆蓋率**: ≥ 90%
- **關鍵模組覆蓋率**: ≥ 95%

**未達標處理：**
1. 阻止 push 到遠端
2. 生成詳細報告
3. Claude Code hook 持續執行直到達標

### Python 覆蓋率計算

```bash
# 執行測試並生成覆蓋率
pytest --cov=src \
       --cov-report=html \
       --cov-report=term \
       --cov-report=json \
       --cov-fail-under=80

# 只檢查新增/修改的檔案
git diff --name-only HEAD~1 | grep "\.py$" | xargs pytest --cov
```

**覆蓋率報告位置：**
- HTML: `htmlcov/index.html`
- JSON: `coverage.json`

### Rust 覆蓋率計算

```bash
# 使用 tarpaulin
cargo tarpaulin \
    --out Html \
    --out Json \
    --output-dir coverage \
    --fail-under 80 \
    --timeout 300

# 只測試修改的模組
git diff --name-only HEAD~1 | grep "\.rs$" | xargs cargo test
```

### Go 覆蓋率計算

```bash
# 執行測試並生成覆蓋率
go test -coverprofile=coverage.out \
        -covermode=atomic \
        ./...

# 生成 HTML 報告
go tool cover -html=coverage.out -o coverage.html

# 檢查門檻
COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
if (( $(echo "$COVERAGE < 80" | bc -l) )); then
    echo "❌ 覆蓋率不足: $COVERAGE%"
    exit 1
fi
```

## 自動化 Code Review 腳本

### post-commit Hook 腳本

建立 `.git/hooks/post-commit` 檔案：

```bash
#!/bin/bash
# post-commit: 自動 code review 與覆蓋率檢查

set -e

echo "🔍 開始 Code Review..."

# 1. Linting 檢查
echo "📝 執行 Linting..."
if [ -f "requirements.txt" ]; then
    pylint src/ --fail-under=8.0 || exit 1
    flake8 src/ || exit 1
    mypy src/ --strict || exit 1
fi

if [ -f "Cargo.toml" ]; then
    cargo clippy -- -D warnings || exit 1
    cargo fmt --check || exit 1
fi

if [ -f "go.mod" ]; then
    golangci-lint run ./... || exit 1
fi

# 2. 複雜度檢查
echo "📊 檢查程式碼複雜度..."
if [ -f "requirements.txt" ]; then
    radon cc src/ -a -nb --total-average || exit 1
fi

# 3. 安全性檢查
echo "🔒 執行安全性掃描..."
if [ -f "requirements.txt" ]; then
    bandit -r src/ -ll || exit 1
fi

# 4. 測試覆蓋率檢查
echo "🧪 計算測試覆蓋率..."
COVERAGE_PASSED=false

while [ "$COVERAGE_PASSED" = false ]; do
    if [ -f "requirements.txt" ]; then
        COVERAGE=$(pytest --cov=src --cov-report=term | grep TOTAL | awk '{print $4}' | sed 's/%//')
        if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
            COVERAGE_PASSED=true
            echo "✅ 測試覆蓋率達標: $COVERAGE%"
        else
            echo "❌ 測試覆蓋率不足: $COVERAGE% (需要 ≥ 80%)"
            echo "📝 未覆蓋的程式碼："
            pytest --cov=src --cov-report=term-missing | grep -v "100%"
            echo ""
            echo "請補充測試後重新提交。按 Ctrl+C 取消，或按 Enter 重新檢查..."
            read
        fi
    fi

    if [ -f "Cargo.toml" ]; then
        cargo tarpaulin --fail-under 80 && COVERAGE_PASSED=true || {
            echo "❌ Rust 測試覆蓋率不足"
            echo "請補充測試後重新檢查..."
            read
        }
    fi

    if [ -f "go.mod" ]; then
        COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
        if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
            COVERAGE_PASSED=true
            echo "✅ Go 測試覆蓋率達標: $COVERAGE%"
        else
            echo "❌ Go 測試覆蓋率不足: $COVERAGE%"
            echo "請補充測試後重新檢查..."
            read
        fi
    fi
done

# 5. 生成 Code Review 報告
echo "📄 生成 Code Review 報告..."
cat > code-review-report.md <<EOF
# Code Review 報告

生成時間: $(date)
Commit: $(git rev-parse --short HEAD)

## ✅ 檢查結果

- [x] Linting 檢查通過
- [x] 複雜度檢查通過
- [x] 安全性掃描通過
- [x] 測試覆蓋率達標 ($COVERAGE%)

## 📊 詳細報告

### 測試覆蓋率
- 整體覆蓋率: $COVERAGE%
- 報告位置: htmlcov/index.html

### 程式碼品質
- Pylint 評分: $(pylint src/ | grep "Your code has been rated" | awk '{print $7}')

EOF

echo "✅ Code Review 完成！報告已生成: code-review-report.md"
```

## Claude Code Hook 配置

在 `.claude/hooks.json` 中配置：

```json
{
  "post-commit": {
    "command": ".git/hooks/post-commit",
    "blocking": true,
    "description": "自動 code review 與覆蓋率檢查"
  }
}
```

## Code Review 報告格式

```markdown
# Code Review 報告

## 📋 基本資訊
- **Commit**: abc1234
- **作者**: Claude + User
- **時間**: 2026-01-09 10:30:00
- **修改檔案**: 5 個

## ✅ 檢查結果

### Linting
- ✅ Pylint: 9.2/10
- ✅ Flake8: 通過
- ✅ MyPy: 通過

### 測試覆蓋率
- ✅ 整體: 85%
- ✅ 新增程式碼: 92%
- ⚠️  需改進: src/legacy.py (45%)

### 安全性
- ✅ Bandit: 無高風險問題
- ✅ 依賴漏洞: 無

### 複雜度
- ✅ 平均循環複雜度: 6.2
- ⚠️  高複雜度函式: process_data() (CC=12)

## 📝 建議

1. 提升 src/legacy.py 測試覆蓋率
2. 重構 process_data() 降低複雜度
3. 考慮拆分大型類別

## 📊 詳細報告
- HTML 覆蓋率: htmlcov/index.html
- JSON 資料: coverage.json
```

## 執行指令

```bash
# 手動觸發 code review
/code-review

# 只檢查覆蓋率
/code-review coverage

# 跳過特定檢查（不建議）
/code-review --skip-lint

# 生成詳細報告
/code-review --verbose
```

## 品質門檻總結

| 項目 | 門檻 | 阻止提交 |
|-----|------|---------|
| 測試覆蓋率 | ≥ 80% | ✅ 是 |
| Pylint 評分 | ≥ 8.0 | ✅ 是 |
| 循環複雜度 | ≤ 10 | ⚠️  警告 |
| 安全性問題 | 0 高危 | ✅ 是 |
| 依賴漏洞 | 0 高危 | ✅ 是 |
