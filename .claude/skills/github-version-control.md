# GitHub 版本控制 Skill

## 描述
通過資安檢查後，自動更新版本號並推送到 GitHub。實施語義化版本控制 (Semantic Versioning)，確保版本號清晰且可追溯。

## 觸發條件
- **自動觸發**：Snyk 資安檢查通過後
- **手動觸發**：執行 `/release` 指令
- **時機**：`post-push` 或手動發布

## GitHub Repository 資訊

- **Repository URL**: https://github.com/trionnemesis/MacDesktopWidget
- **SSH Key**: SHA256:hWPEAbEC7yt9jHqOf4BHfx/eo1ITUZbXYumR+VK2NFw
- **起始版本**: v0.1.0

## 語義化版本控制 (Semantic Versioning)

### 版本號格式

```
v{MAJOR}.{MINOR}.{PATCH}

範例：v1.2.3
```

- **MAJOR (主版本號)**: 不相容的 API 變更
- **MINOR (次版本號)**: 向下相容的功能新增
- **PATCH (修訂號)**: 向下相容的問題修復

### 版本號遞增規則

| 變更類型 | 版本遞增 | 範例 |
|---------|---------|------|
| 🔴 **Breaking Change** | MAJOR | v1.0.0 → v2.0.0 |
| 🟢 **New Feature** | MINOR | v1.2.0 → v1.3.0 |
| 🔵 **Bug Fix** | PATCH | v1.2.3 → v1.2.4 |
| 🟡 **Refactor/Docs** | PATCH | v1.2.3 → v1.2.4 |

### Commit Message 與版本對應

使用 Conventional Commits 規範：

```bash
# PATCH 版本
fix: 修復 CPU 監控記憶體洩漏
docs: 更新 README
perf: 優化 UI 渲染效能

# MINOR 版本
feat: 新增 LangChain 整合功能
feat(ui): 新增深色模式

# MAJOR 版本
feat!: 重新設計 API 介面
BREAKING CHANGE: 移除舊版 API
```

## 版本檔案管理

### VERSION 檔案

建立 `VERSION` 檔案追蹤當前版本：

```
0.1.0
```

### Python setup.py / pyproject.toml

```toml
# pyproject.toml
[project]
name = "mac-desktop-widget"
version = "0.1.0"
description = "MAC Desktop Widget with System Monitoring"
```

### Rust Cargo.toml

```toml
[package]
name = "mac-desktop-widget"
version = "0.1.0"
edition = "2021"
```

### Go go.mod

```go
module github.com/trionnemesis/MacDesktopWidget

go 1.21
```

## 自動版本更新腳本

### 版本更新工具 (.claude/scripts/bump-version.sh)

```bash
#!/bin/bash
# bump-version.sh: 自動更新版本號

set -e

CURRENT_VERSION=$(cat VERSION)

# 解析版本號
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# 根據 commit 訊息決定遞增類型
if git log -1 --pretty=%B | grep -qE "BREAKING CHANGE|feat!"; then
    # Major 版本
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    BUMP_TYPE="major"
elif git log -1 --pretty=%B | grep -qE "^feat"; then
    # Minor 版本
    MINOR=$((MINOR + 1))
    PATCH=0
    BUMP_TYPE="minor"
else
    # Patch 版本
    PATCH=$((PATCH + 1))
    BUMP_TYPE="patch"
fi

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo "🔄 版本更新: v$CURRENT_VERSION → v$NEW_VERSION ($BUMP_TYPE)"

# 更新 VERSION 檔案
echo "$NEW_VERSION" > VERSION

# 更新 Python pyproject.toml
if [ -f "pyproject.toml" ]; then
    sed -i '' "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
fi

# 更新 Rust Cargo.toml
if [ -f "Cargo.toml" ]; then
    sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" Cargo.toml
fi

# 更新 package.json（如果有）
if [ -f "package.json" ]; then
    jq ".version = \"$NEW_VERSION\"" package.json > package.json.tmp
    mv package.json.tmp package.json
fi

echo "✅ 版本號已更新至 v$NEW_VERSION"
echo "$NEW_VERSION"
```

**設定執行權限：**

```bash
chmod +x .claude/scripts/bump-version.sh
```

## GitHub 發布流程

### post-push Hook 腳本

建立 `.git/hooks/post-push`（或在成功 push 後觸發）：

```bash
#!/bin/bash
# post-push: 自動版本標籤與發布

set -e

echo "🏷️  開始版本發布流程..."

# 1. 檢查是否通過資安檢查
if [ ! -f "reports/security-summary.md" ]; then
    echo "⚠️  未找到資安檢查報告，跳過自動發布"
    exit 0
fi

# 2. 更新版本號
echo "🔄 更新版本號..."
NEW_VERSION=$(.claude/scripts/bump-version.sh)

if [ -z "$NEW_VERSION" ]; then
    echo "❌ 版本更新失敗"
    exit 1
fi

# 3. 生成 CHANGELOG
echo "📝 生成 CHANGELOG..."

# 取得上一個標籤
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -z "$LAST_TAG" ]; then
    # 第一個版本
    git log --pretty=format:"- %s (%h)" > CHANGELOG-v$NEW_VERSION.md
else
    # 從上一個標籤到現在的變更
    git log $LAST_TAG..HEAD --pretty=format:"- %s (%h)" > CHANGELOG-v$NEW_VERSION.md
fi

# 4. Commit 版本更新
echo "💾 提交版本更新..."
git add VERSION pyproject.toml Cargo.toml package.json 2>/dev/null || true
git commit -m "chore: bump version to v$NEW_VERSION

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>" || {
    echo "ℹ️  無需提交（可能已是最新）"
}

# 5. 建立 Git Tag
echo "🏷️  建立 Git 標籤..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION

$(cat CHANGELOG-v$NEW_VERSION.md)

✅ All security checks passed
📊 Test coverage: $(grep -oP 'coverage.*\K[0-9.]+%' reports/security-summary.md || echo 'N/A')
"

# 6. Push 到 GitHub
echo "⬆️  推送到 GitHub..."

# 檢查是否已設定 remote
if ! git remote get-url origin &> /dev/null; then
    echo "📡 設定 GitHub remote..."
    git remote add origin git@github.com:trionnemesis/MacDesktopWidget.git
fi

# Push commits 與 tags
git push origin main --follow-tags

echo "✅ 成功推送版本 v$NEW_VERSION 到 GitHub"

# 7. 建立 GitHub Release
echo "🚀 建立 GitHub Release..."

if command -v gh &> /dev/null; then
    # 使用 GitHub CLI
    gh release create "v$NEW_VERSION" \
        --title "v$NEW_VERSION" \
        --notes-file CHANGELOG-v$NEW_VERSION.md \
        --verify-tag

    echo "✅ GitHub Release 已建立: https://github.com/trionnemesis/MacDesktopWidget/releases/tag/v$NEW_VERSION"
else
    echo "⚠️  GitHub CLI (gh) 未安裝，請手動建立 Release"
    echo "   或執行: brew install gh"
fi

# 8. 清理臨時檔案
rm -f CHANGELOG-v$NEW_VERSION.md

echo ""
echo "🎉 版本發布完成！"
echo "   版本: v$NEW_VERSION"
echo "   Repository: https://github.com/trionnemesis/MacDesktopWidget"
echo ""
```

**設定執行權限：**

```bash
chmod +x .git/hooks/post-push
```

## SSH 金鑰設定

### 配置 SSH 認證

```bash
# 檢查 SSH key
ssh-add -l | grep SHA256:hWPEAbEC7yt9jHqOf4BHfx/eo1ITUZbXYumR+VK2NFw

# 如果沒有，添加 SSH key
ssh-add ~/.ssh/id_ed25519  # 或你的金鑰路徑

# 測試 GitHub 連線
ssh -T git@github.com
# 應該看到: Hi trionnemesis! You've successfully authenticated...
```

### 設定 Git Remote

```bash
# 使用 SSH URL
git remote add origin git@github.com:trionnemesis/MacDesktopWidget.git

# 或更新現有 remote
git remote set-url origin git@github.com:trionnemesis/MacDesktopWidget.git

# 驗證設定
git remote -v
```

## CHANGELOG 生成

### 自動生成 CHANGELOG.md

```bash
#!/bin/bash
# generate-changelog.sh: 生成完整 CHANGELOG

cat > CHANGELOG.md <<EOF
# Changelog

所有重要變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [語義化版本](https://semver.org/lang/zh-TW/)。

EOF

# 遍歷所有標籤
git tag -l --sort=-version:refname | while read TAG; do
    if [ -n "$TAG" ]; then
        echo "" >> CHANGELOG.md
        echo "## [$TAG] - $(git log -1 --format=%ai $TAG | cut -d ' ' -f 1)" >> CHANGELOG.md
        echo "" >> CHANGELOG.md

        # 取得該標籤的變更
        PREV_TAG=$(git describe --tags --abbrev=0 $TAG^ 2>/dev/null || echo "")

        if [ -n "$PREV_TAG" ]; then
            git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)" >> CHANGELOG.md
        else
            git log $TAG --pretty=format:"- %s (%h)" >> CHANGELOG.md
        fi

        echo "" >> CHANGELOG.md
    fi
done

echo "✅ CHANGELOG.md 已生成"
```

### CHANGELOG 範例

```markdown
# Changelog

## [0.2.0] - 2026-01-09

### Added
- feat: 新增 LangChain 整合功能 (abc1234)
- feat(ui): 新增深色模式支援 (def5678)

### Fixed
- fix: 修復 CPU 監控記憶體洩漏 (ghi9012)
- fix(test): 修正測試覆蓋率計算錯誤 (jkl3456)

### Changed
- refactor: 重構系統監控模組 (mno7890)

## [0.1.0] - 2026-01-08

### Added
- feat: 初始版本發布 (pqr1234)
- feat: 實作基本系統監控功能 (stu5678)
```

## GitHub Actions 自動化（可選）

### .github/workflows/release.yml

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: macos-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Setup Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable

    - name: Setup Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.21'

    - name: Run Tests
      run: |
        pytest --cov=src --cov-report=json
        cargo test
        go test ./...

    - name: Build Binaries
      run: |
        # Python
        pip install pyinstaller
        pyinstaller --onefile src/main.py

        # Rust
        cargo build --release

        # Go
        go build -o bin/app

    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/main
          target/release/app
          bin/app
        body_path: CHANGELOG.md
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 版本發布檢查清單

在發布新版本前，確認：
- [ ] ✅ 所有測試通過
- [ ] ✅ 測試覆蓋率 ≥ 80%
- [ ] ✅ Code review 完成
- [ ] ✅ Snyk 資安檢查通過（無 Critical/High）
- [ ] ✅ CHANGELOG 已更新
- [ ] ✅ 版本號已遞增
- [ ] ✅ Git tag 已建立
- [ ] ✅ 推送到 GitHub 成功
- [ ] ✅ GitHub Release 已建立

## 手動發布指令

```bash
# 方式 1: 使用 skill
/release

# 方式 2: 手動執行腳本
.claude/scripts/bump-version.sh
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --follow-tags

# 方式 3: 使用 GitHub CLI
gh release create v0.1.0 \
    --title "v0.1.0" \
    --notes "初始版本發布"
```

## 回滾版本

如果發布出現問題：

```bash
# 刪除本地標籤
git tag -d v0.1.0

# 刪除遠端標籤
git push origin :refs/tags/v0.1.0

# 刪除 GitHub Release
gh release delete v0.1.0 --yes

# 還原版本號
git revert HEAD
```

## 版本管理最佳實踐

1. ✅ **永遠遵循語義化版本**
2. ✅ **每個版本都有對應的 Git tag**
3. ✅ **CHANGELOG 保持更新**
4. ✅ **發布前確保所有檢查通過**
5. ✅ **使用有意義的 commit message**
6. ✅ **重大變更要有詳細說明**
7. ✅ **定期發布，保持節奏**

## 發布通知

發布成功後，可以：
- 📧 發送發布通知郵件
- 📱 在 Slack/Discord 通知
- 🐦 發布推文宣布新版本
- 📝 更新專案文件

```bash
# 範例：發送 Slack 通知
curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🎉 MacDesktopWidget v0.1.0 已發布！\nhttps://github.com/trionnemesis/MacDesktopWidget/releases/tag/v0.1.0"}' \
    YOUR_SLACK_WEBHOOK_URL
```
