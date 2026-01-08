# Quick Start Guide - MacDesktopWidget

## 🚀 Installation

### 1. Prerequisites

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com for Windows

# Pull LLaMA3 model
ollama pull llama3

# Verify installation
ollama list
```

### 2. Install Application

```bash
cd MacDesktopWidget

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -e .
```

## ▶️ Running the Application

```bash
# Make sure Ollama is running
# It should start automatically, or run: ollama serve

# Run the widget
python src/python/main.py
```

You should see a transparent window appear with:
- 🖥️ Real-time system metrics (CPU, Memory, Disk, GPU)
- 📊 Top 5 processes by CPU usage
- 🤖 AI suggestions when anomalies are detected

## 🎮 Using the Widget

### Window Controls
- **Drag to Move**: Click and drag anywhere on the window
- **Close**: Click the ✕ button in the top-right
- **Always on Top**: Window stays above other applications

### Monitoring Thresholds
The widget detects anomalies when:
- CPU > 80% (sustained for 3 seconds)
- Memory > 90% (sustained for 5 seconds)
- Single process using > 50% CPU or Memory
- Disk I/O > 200 MB/s

### AI Suggestions
When an anomaly is detected:
1. System analyzes the issue
2. Sends context to LLaMA3 via Ollama
3. Displays Traditional Chinese suggestion (≤30 characters)
4. Suggestion auto-fades after showing

## 🧪 Testing Anomalies

### Trigger CPU Anomaly
```bash
# macOS/Linux - creates CPU load
yes > /dev/null &

# Kill it
killall yes
```

### Trigger Memory Anomaly
```python
# Python - allocates large memory
python -c "import time; x = [0] * (10**9); time.sleep(30)"
```

## ⚙️ Configuration

Create `.env` file in project root:

```bash
# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Update interval (milliseconds)
UPDATE_INTERVAL_MS=1000

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=90
PROCESS_THRESHOLD=50

# Logging
DEBUG=false
LOG_LEVEL=INFO
```

## 🐛 Troubleshooting

### "Ollama not available"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Verify model is installed
ollama list
```

### GPU Shows "N/A"
This is normal on Windows or if `macmon` isn't installed:
```bash
# macOS only - install GPU monitoring
pip install macmon
```

### Window Not Appearing
Check logs in `mac_desktop_widget.log`:
```bash
tail -f mac_desktop_widget.log
```

## 📝 Keyboard Shortcuts

- **Ctrl+C** (in terminal): Gracefully stop the application
- The window can be closed with the ✕ button

## 🎨 UI Features

- **Glassmorphism Design**: Translucent frosted glass effect
- **Real-time Updates**: Metrics refresh every second
- **Color-coded Metrics**: 
  - Green (0-60%): Normal
  - Yellow (60-80%): Warning
  - Red (80-100%): Critical
- **AI Suggestion Colors**:
  - Purple: Info
  - Orange: Warning
  - Red: Critical

## 📊 Performance

Typical resource usage:
- **CPU**: < 2% (monitoring overhead)
- **Memory**: ~50-70MB (without Ollama)
- **Update Latency**: 50-100ms per refresh

## 🔄 Updating

```bash
# Pull latest changes
git pull

# Reinstall dependencies
pip install -e .
```

## 📚 Advanced Usage

### Run Without AI
Set in `.env`:
```bash
ENABLE_AI=false
```

### Adjust Update Frequency
```bash
# Slower updates (2 seconds) - uses less CPU
UPDATE_INTERVAL_MS=2000

# Faster updates (500ms) - may use more CPU
UPDATE_INTERVAL_MS=500
```

### Change Thresholds
```bash
# More sensitive (triggers more often)
CPU_THRESHOLD=70
MEMORY_THRESHOLD=85

# Less sensitive (triggers less often)
CPU_THRESHOLD=90
MEMORY_THRESHOLD=95
```

## 🎯 Next Steps

1. **Customize**: Edit thresholds in `.env`
2. **Monitor**: Watch your system resources
3. **Learn**: Observe AI suggestions
4. **Optimize**: Act on recommendations

Enjoy your AI-powered system monitoring! 🚀
