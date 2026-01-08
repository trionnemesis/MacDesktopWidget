# 🖥️ MacDesktopWidget

極簡透明的 macOS 系統儀表板，整合 **Ollama + LLaMA3 8B AI Agent**，提供即時繁體中文資源監控建議。

A minimal transparent macOS system dashboard with Ollama + LLaMA3 8B AI Agent for Traditional Chinese resource monitoring suggestions.

---

## 🌟 核心特色 (Core Features)

### 📊 實時監控 (Real-time Monitoring)
- **CPU 使用量**: 追蹤整體及各核心負載、運作頻率。
- **記憶體狀況**: 監控 RAM 及 Swap 虛擬記憶體使用率。
- **磁碟 I/O**: 即時顯示資料讀取與寫入速度。
- **GPU 支援**: 專屬 macOS GPU 使用監測 (macmon)。
- **程序排行**: 自動過濾並顯示前 5 名高資源消耗程序。

### 🤖 AI 智能建議 (AI-Powered Suggestions)
- **本地推理**: 支援 Ollama + LLaMA3 8B 在地運行，隱私安全無虞。
- **繁體中文**: 精準的中文回應，語氣專業且符合習慣。
- **簡潔明瞭**: 嚴格限制回應在 30 字元內，方便一眼掃過。
- **異常檢測**: 基於狀態機的異常檢測，避免過度干擾。

### 🎨 極簡設計 (Minimalist UI)
- **Glassmorphism**: 現代感毛玻璃特效 UI。
- **完全透明**: 無邊框設計，可隨意拖曳定位。
- **低功耗**: 優化後的 1 秒更新頻率，對系統負載極小。

---

## 🚀 快速上手 (Quick Start)

### 1. 前置準備 (Prerequisites)
安裝 [Ollama](https://ollama.com/) 並下載 LLaMA3 模型：
```bash
# 下載模型
ollama pull llama3

# 驗證安裝
ollama list
```

### 2. 安裝步驟 (Installation)
```bash
# 下載專案並進入目錄
git clone https://github.com/trionnemesis/MacDesktopWidget
cd MacDesktopWidget

# 建立並啟動虛擬環境
python -m venv venv
source venv/bin/activate  # Windows 使用: venv\Scripts\activate

# 安裝相依套件
pip install -e .

# (選配) macOS GPU 支援
pip install -e ".[macos]"
```

### 3. 啟動程式 (Run)
```bash
python src/python/main.py
```

---

## ⚙️ 進階配置 (Configuration)

您可以透過建立 `.env` 檔案來調整監控閾值：

| 參數 | 預設值 | 說明 |
| :--- | :--- | :--- |
| `UPDATE_INTERVAL_MS` | `1000` | 更新頻率 (毫秒) |
| `CPU_THRESHOLD` | `80` | CPU 異常警示門檻 (%) |
| `MEMORY_THRESHOLD` | `90` | 記憶體異常警示門檻 (%) |
| `PROCESS_THRESHOLD` | `50` | 單一程序資源異常門檻 (%) |
| `OLLAMA_MODEL` | `llama3` | 使用的 AI 模型名稱 |

---

## 🏗️ 專案架構 (Technical Architecture)

```
MacDesktopWidget/
├── src/python/
│   ├── core/           # 核心控制、配置管理 (App, Config)
│   ├── monitoring/     # 系統監測邏輯 (CPU, Memory, GPU, etc.)
│   ├── ai/             # AI 整合、Prompt 模版、建議引擎
│   └── ui/             # PyQt6 介面、QSS 樣式、Glassmorphism
├── tests/              # 單元測試與集成測試
└── README.md           # 專案說明文件
```

**技術棧:**
- **Frontend**: PyQt6 + Glassmorphism QSS
- **Monitoring**: psutil + macmon
- **AI Engine**: LangChain + Ollama (LLaMA3)
- **Data**: Pydantic models for type safety

---

## 🧪 開發與測試 (Development)

```bash
# 執行單元測試
pytest tests/unit/

# 程式碼品質檢查
ruff check src/
black src/
```

---

## 📈 目前進度 (Project Status: 90%)

- [x] 核心監控系統 (CPU, RAM, Disk, GPU)
- [x] 異常檢測狀態機 (Anomaly Detection)
- [x] Ollama / LLaMA3 AI 串接
- [x] 繁體中文 Few-shot Prompt 設計
- [x] 透明毛玻璃介面 (Glassmorphism UI)
- [x] 系統整合與訊號串接
- [ ] 自動化部署腳本
- [ ] 使用者自定義選單面板

---

## 📝 授權協議 (License)

本專案採用 **MIT License** 授權。

## 🙏 鳴謝 (Acknowledgments)
- [Ollama](https://ollama.com/)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [psutil](https://github.com/giampaolo/psutil)
- [LangChain](https://www.langchain.com/)

---

> **Note**: 本專案主要針對 macOS 優化，但在 Windows 下亦可進行開發 (GPU 監控受限)。
