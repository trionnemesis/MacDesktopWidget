# MAC Desktop Widget Development Optimizer

## 描述
針對 MAC 桌面應用開發的程式碼優化 skill，支援 Python (PyQt6)、Rust、Go 三種語言，確保最佳效能與 Apple Silicon 相容性。

## 觸發條件
- 使用者執行 `/mac-optimize` 指令
- 偵測到效能瓶頸或資源佔用過高
- 新增或修改 UI 元件時

## 優化檢查清單

### 🐍 Python (PyQt6) 優化

#### UI/UX 效能
- [ ] 使用 `QThread` 進行耗時操作，避免阻塞主執行緒
- [ ] 實作 `asyncio` 整合，處理非同步任務
- [ ] QSS 樣式表優化：避免過度使用選擇器，使用類別選擇器提升效能
- [ ] Qt Designer 生成的程式碼檢查：移除未使用的 widget
- [ ] 實作 lazy loading 機制，延遲載入非關鍵元件

#### 資源監控 (psutil)
- [ ] 監控 CPU 使用率，避免持續高於 30%
- [ ] 記憶體佔用控制在 150MB 以下
- [ ] 實作資源釋放機制，避免記憶體洩漏
- [ ] 定期清理未使用的 QObject 實例

#### LangChain/LangGraph 整合
- [ ] 使用非同步 API 呼叫 (`async`/`await`)
- [ ] 實作快取機制，減少重複 LLM 請求
- [ ] 錯誤處理與 fallback 機制
- [ ] Token 用量監控與成本控制

#### PyQt6 最佳實踐
```python
# ✅ 正確：使用 QThread 處理耗時任務
class WorkerThread(QThread):
    finished = pyqtSignal(object)

    def run(self):
        result = self.heavy_computation()
        self.finished.emit(result)

# ✅ 正確：asyncio 整合
class AsyncWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()

    async def fetch_data(self):
        # 非同步操作
        await self.api_call()
```

#### QSS 優化
```qss
/* ✅ 高效能：使用類別選擇器 */
.custom-button {
    background-color: #007AFF;
    border-radius: 8px;
}

/* ❌ 避免：複雜的後代選擇器 */
QMainWindow QWidget QPushButton#myButton {
    /* 過度具體，效能差 */
}
```

### 🦀 Rust 優化

#### Framework 選擇
- [ ] 使用 `tauri` 框架進行跨平台開發
- [ ] 或使用 `cocoa-rs` 原生 macOS 開發
- [ ] 實作 `tokio` 非同步運行時

#### 效能優化
- [ ] 啟用 LTO (Link Time Optimization)
- [ ] 使用 `cargo build --release` 編譯
- [ ] Apple Silicon 編譯：`--target aarch64-apple-darwin`
- [ ] 記憶體安全檢查：避免 `unsafe` block 濫用

```rust
// Cargo.toml 優化配置
[profile.release]
lto = true
opt-level = 3
codegen-units = 1
strip = true

[target.aarch64-apple-darwin]
rustflags = ["-C", "target-cpu=native"]
```

### 🐹 Go 優化

#### Framework 選擇
- [ ] 使用 `fyne` 進行跨平台 UI 開發
- [ ] 或使用 `macdriver` 原生 macOS 整合
- [ ] 實作 `goroutine` 並發處理

#### 效能優化
- [ ] 使用 `sync.Pool` 減少記憶體分配
- [ ] 實作 goroutine 池，避免無限制建立
- [ ] Apple Silicon 編譯：`GOARCH=arm64 go build`
- [ ] 使用 `pprof` 進行效能分析

```go
// 編譯優化
// GOOS=darwin GOARCH=arm64 go build -ldflags="-s -w" -o app

// goroutine 池範例
type WorkerPool struct {
    tasks chan func()
}

func (p *WorkerPool) Start(workerCount int) {
    for i := 0; i < workerCount; i++ {
        go p.worker()
    }
}
```

## Apple Silicon (M1/M2/M3) 相容性

### 編譯檢查
- [ ] Python: 確保所有依賴支援 ARM64
- [ ] Rust: 使用 `aarch64-apple-darwin` target
- [ ] Go: 設定 `GOARCH=arm64`

### Universal Binary (通用二進位檔)
```bash
# Rust
cargo build --release --target x86_64-apple-darwin
cargo build --release --target aarch64-apple-darwin
lipo -create -output app target/x86_64-apple-darwin/release/app target/aarch64-apple-darwin/release/app

# Go
GOOS=darwin GOARCH=amd64 go build -o app-amd64
GOOS=darwin GOARCH=arm64 go build -o app-arm64
lipo -create -output app app-amd64 app-arm64
```

## 效能基準

### 資源使用目標
- **CPU**: 閒置 < 5%, 活動 < 30%
- **記憶體**: < 150MB (Python), < 50MB (Rust/Go)
- **啟動時間**: < 2 秒
- **UI 響應**: < 16ms (60 FPS)

## 檢查指令

執行以下指令進行優化檢查：

```bash
# Python 效能分析
python -m cProfile -o profile.stats main.py
python -m pstats profile.stats

# Rust 效能分析
cargo flamegraph

# Go 效能分析
go test -cpuprofile=cpu.prof -memprofile=mem.prof
go tool pprof cpu.prof
```

## 輸出報告

完成優化後，生成報告包含：
1. 優化前後效能對比
2. 資源使用統計
3. 建議改進項目
4. Apple Silicon 相容性確認
