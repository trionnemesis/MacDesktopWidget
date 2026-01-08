# SDD + TDD 開發流程 Skill

## 描述
結合規格驅動開發 (Specification-Driven Development) 與測試驅動開發 (Test-Driven Development) 的完整工作流程。確保程式碼品質、可維護性與測試覆蓋率。

## 觸發條件
- 開始新功能開發時自動觸發
- 使用者執行 `/dev-workflow` 指令
- 重構現有程式碼時

## 開發流程

### 階段 1️⃣：規格定義 (Specification)

在撰寫任何程式碼前，必須先定義清晰的規格。

#### 規格文件範本

建立 `specs/` 目錄，每個功能建立對應的規格檔案：

```markdown
# [功能名稱] 規格書

## 📋 功能概述
[簡短描述這個功能的目的]

## 🎯 目標
- 目標 1
- 目標 2

## 📊 狀態變數 (State Variables)
| 變數名稱 | 型別 | 初始值 | 說明 |
|---------|------|--------|------|
| `userStatus` | `str` | `"idle"` | 使用者當前狀態 |

## ⚡ 允許的操作 (Actions)
1. **startMonitoring()**: 開始監控系統資源
   - 前置條件：`status == "idle"`
   - 後置條件：`status == "monitoring"`

## 🚫 硬性約束 (Constraints)
- CPU 使用率不得超過 30%
- 記憶體佔用不得超過 150MB
- UI 必須在 16ms 內響應

## 📝 使用案例
1. **正常流程**
   - 使用者點擊「開始監控」
   - 系統檢查權限
   - 開始顯示即時資料

2. **異常流程**
   - 無權限時顯示錯誤訊息
   - 網路斷線時切換至離線模式

## 🧪 驗收標準
- [ ] 所有單元測試通過
- [ ] 測試覆蓋率 ≥ 80%
- [ ] UI 響應時間 < 100ms
- [ ] 無記憶體洩漏
```

#### Model-First Reasoning 檢查清單

建立規格時必須明確定義：
- [ ] ✅ 所有狀態變數已列出
- [ ] ✅ 所有操作的前後置條件已定義
- [ ] ✅ 所有業務邏輯約束已明確
- [ ] ✅ 邊界條件已考慮
- [ ] ✅ 錯誤處理策略已規劃

### 階段 2️⃣：測試先行 (Test-First)

根據規格撰寫測試，**在實作之前**。

#### 測試檔案結構

```
tests/
├── unit/           # 單元測試
│   ├── test_monitor.py
│   └── test_widget.py
├── integration/    # 整合測試
│   └── test_system.py
└── fixtures/       # 測試資料
    └── mock_data.py
```

#### Python (PyQt6) 測試範例

```python
# tests/unit/test_monitor.py
import pytest
from unittest.mock import Mock, patch
from src.monitor import SystemMonitor

class TestSystemMonitor:
    """系統監控器單元測試"""

    @pytest.fixture
    def monitor(self):
        return SystemMonitor()

    def test_initial_state_is_idle(self, monitor):
        """測試：初始狀態應為 idle"""
        assert monitor.status == "idle"

    def test_start_monitoring_changes_status(self, monitor):
        """測試：開始監控後狀態變為 monitoring"""
        monitor.start_monitoring()
        assert monitor.status == "monitoring"

    def test_cpu_usage_below_threshold(self, monitor):
        """測試：CPU 使用率低於 30%"""
        monitor.start_monitoring()
        cpu_usage = monitor.get_cpu_usage()
        assert cpu_usage < 30.0

    @patch('psutil.cpu_percent')
    def test_handles_psutil_error(self, mock_cpu, monitor):
        """測試：處理 psutil 錯誤"""
        mock_cpu.side_effect = Exception("Permission denied")
        with pytest.raises(SystemMonitorError):
            monitor.get_cpu_usage()

    def test_memory_usage_below_threshold(self, monitor):
        """測試：記憶體佔用低於 150MB"""
        monitor.start_monitoring()
        memory_mb = monitor.get_memory_usage()
        assert memory_mb < 150

    @pytest.mark.asyncio
    async def test_async_data_fetch(self, monitor):
        """測試：非同步資料獲取"""
        data = await monitor.fetch_langchain_data()
        assert data is not None
        assert 'result' in data
```

#### Rust 測試範例

```rust
// src/monitor.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_initial_state_is_idle() {
        let monitor = SystemMonitor::new();
        assert_eq!(monitor.status(), MonitorStatus::Idle);
    }

    #[test]
    fn test_start_monitoring_changes_status() {
        let mut monitor = SystemMonitor::new();
        monitor.start_monitoring().unwrap();
        assert_eq!(monitor.status(), MonitorStatus::Monitoring);
    }

    #[tokio::test]
    async fn test_async_cpu_usage() {
        let monitor = SystemMonitor::new();
        let cpu = monitor.get_cpu_usage().await.unwrap();
        assert!(cpu < 30.0);
    }
}
```

#### Go 測試範例

```go
// monitor_test.go
package main

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestInitialStateIsIdle(t *testing.T) {
    monitor := NewSystemMonitor()
    assert.Equal(t, "idle", monitor.Status())
}

func TestStartMonitoringChangesStatus(t *testing.T) {
    monitor := NewSystemMonitor()
    err := monitor.StartMonitoring()
    assert.NoError(t, err)
    assert.Equal(t, "monitoring", monitor.Status())
}

func TestCPUUsageBelowThreshold(t *testing.T) {
    monitor := NewSystemMonitor()
    monitor.StartMonitoring()
    cpu := monitor.GetCPUUsage()
    assert.Less(t, cpu, 30.0)
}
```

### 階段 3️⃣：實作 (Implementation)

根據規格與測試進行實作。

#### 實作檢查清單
- [ ] 僅實作規格中定義的功能
- [ ] 確保所有測試通過
- [ ] 遵循語言最佳實踐
- [ ] 避免過度工程化
- [ ] 程式碼可讀性優先

#### Red-Green-Refactor 循環

```
🔴 Red:    撰寫測試（測試失敗）
    ↓
🟢 Green:  撰寫最小可行程式碼（測試通過）
    ↓
🔵 Refactor: 重構優化（保持測試通過）
    ↓
    重複
```

### 階段 4️⃣：測試覆蓋率檢查

#### Python 覆蓋率工具

```bash
# 安裝 pytest-cov
pip install pytest-cov

# 執行測試並生成覆蓋率報告
pytest --cov=src --cov-report=html --cov-report=term

# 覆蓋率門檻檢查
pytest --cov=src --cov-fail-under=80
```

#### Rust 覆蓋率工具

```bash
# 安裝 tarpaulin
cargo install cargo-tarpaulin

# 執行測試並生成覆蓋率
cargo tarpaulin --out Html --output-dir coverage

# 覆蓋率門檻檢查
cargo tarpaulin --fail-under 80
```

#### Go 覆蓋率工具

```bash
# 執行測試並生成覆蓋率
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# 覆蓋率門檻檢查
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//' | awk '{if($1<80) exit 1}'
```

## 持續整合檢查

### 覆蓋率未達標處理

如果測試覆蓋率低於 80%：

1. **阻止 commit**：Claude Code hook 會持續執行直到達標
2. **生成報告**：列出未覆蓋的程式碼區塊
3. **建議補充**：提示需要補充的測試案例

```bash
# 範例：覆蓋率檢查腳本
#!/bin/bash

COVERAGE=$(pytest --cov=src --cov-report=term | grep TOTAL | awk '{print $4}' | sed 's/%//')

if (( $(echo "$COVERAGE < 80" | bc -l) )); then
    echo "❌ 測試覆蓋率不足：$COVERAGE% (需要 ≥ 80%)"
    echo "📝 請補充以下檔案的測試："
    pytest --cov=src --cov-report=term-missing | grep -v "100%"
    exit 1
else
    echo "✅ 測試覆蓋率達標：$COVERAGE%"
    exit 0
fi
```

## 文件同步

完成開發後，確保以下文件更新：
- [ ] 規格文件反映實際實作
- [ ] API 文件已生成
- [ ] README 包含使用範例
- [ ] CHANGELOG 記錄變更

## 開發流程命令

```bash
# 1. 建立新功能規格
/dev-workflow new-feature "系統監控器"

# 2. 生成測試模板
/dev-workflow generate-tests

# 3. 執行測試與覆蓋率檢查
/dev-workflow test

# 4. 驗證是否符合規格
/dev-workflow verify-spec
```

## 品質標準

每個功能必須滿足：
- ✅ 規格文件完整
- ✅ 測試覆蓋率 ≥ 80%
- ✅ 所有測試通過
- ✅ 無 linter 警告
- ✅ 無記憶體洩漏
- ✅ 效能符合約束

## 範例專案結構

```
MacDesktopWidget/
├── specs/                  # 📋 規格文件
│   ├── system-monitor.md
│   └── widget-ui.md
├── src/                    # 💻 原始碼
│   ├── python/
│   ├── rust/
│   └── go/
├── tests/                  # 🧪 測試
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                   # 📚 文件
└── coverage/              # 📊 覆蓋率報告
```
