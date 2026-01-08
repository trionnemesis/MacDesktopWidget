#!/bin/bash
# bump-version.sh: 自動更新版本號

set -e

# 如果 VERSION 檔案不存在，建立初始版本
if [ ! -f "VERSION" ]; then
    echo "0.1.0" > VERSION
    echo "0.1.0"
    exit 0
fi

CURRENT_VERSION=$(cat VERSION)

# 解析版本號
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# 根據 commit 訊息決定遞增類型
LAST_COMMIT=$(git log -1 --pretty=%B)

if echo "$LAST_COMMIT" | grep -qE "BREAKING CHANGE|feat!"; then
    # Major 版本
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    BUMP_TYPE="major"
elif echo "$LAST_COMMIT" | grep -qE "^feat"; then
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

echo "🔄 版本更新: v$CURRENT_VERSION → v$NEW_VERSION ($BUMP_TYPE)" >&2

# 更新 VERSION 檔案
echo "$NEW_VERSION" > VERSION

# 更新 Python pyproject.toml
if [ -f "pyproject.toml" ]; then
    if command -v sed &> /dev/null; then
        # Windows Git Bash 或 macOS
        sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml && rm -f pyproject.toml.bak
    fi
fi

# 更新 Rust Cargo.toml
if [ -f "Cargo.toml" ]; then
    if command -v sed &> /dev/null; then
        sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" Cargo.toml && rm -f Cargo.toml.bak
    fi
fi

# 更新 package.json（如果有）
if [ -f "package.json" ] && command -v jq &> /dev/null; then
    jq ".version = \"$NEW_VERSION\"" package.json > package.json.tmp
    mv package.json.tmp package.json
fi

echo "✅ 版本號已更新至 v$NEW_VERSION" >&2
echo "$NEW_VERSION"
