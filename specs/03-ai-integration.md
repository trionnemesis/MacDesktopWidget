# AI Integration Specification

## Overview

This document specifies the integration of Ollama + LLaMA3 8B for AI-powered Traditional Chinese system monitoring suggestions.

## Requirements

### Local AI Model
- **Platform**: Ollama
- **Model**: LLaMA3 8B (`llama3`)
- **Deployment**: Local inference (http://localhost:11434)
- **Resource Requirements**:
  - Model size: ~4.7GB
  - RAM: Minimum 8GB, recommended 16GB
  - CPU: Modern multi-core processor

### Output Requirements
- **Language**: Traditional Chinese (繁體中文)
- **Length**: Maximum 30 characters
- **Format**: Single-line suggestion
- **Tone**: Concise, actionable, helpful

## Architecture

### Components

#### Ollama Client (`ollama_client.py`)
- Async HTTP client for Ollama API
- Non-blocking API calls
- Request timeout: 5 seconds (configurable)
- Retry logic: 2 retries with exponential backoff
- Health check: Verify model availability on startup

#### LangChain Agent (`langchain_agent.py`)
- Wrapper around Ollama LLM
- Construct prompts with system context
- Parse and validate responses
- Enforce output constraints (length, language)

#### Suggestion Engine (`suggestion_engine.py`)
- Runs in separate QThread
- Receives anomaly events via queue
- Calls LangChain agent asynchronously
- Caches suggestions to avoid duplicates
- Rate limiting: Max 1 request per 10 seconds

#### Prompt Templates (`zh_tw_templates.py`)
- System prompt defining AI role
- Few-shot examples for each anomaly type
- Context injection templates
- Output format enforcement

## Ollama API Integration

### Endpoint
```
POST http://localhost:11434/api/generate
```

### Request Format
```json
{
  "model": "llama3",
  "prompt": "<full_prompt>",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "max_tokens": 50,
    "top_p": 0.9
  }
}
```

### Response Format
```json
{
  "model": "llama3",
  "response": "建議文字",
  "done": true
}
```

### Error Handling
- **Connection Error**: Log and disable AI temporarily
- **Timeout**: Cancel request, show cached suggestion if available
- **Invalid Response**: Fallback to template-based suggestion

## Prompt Engineering

### System Prompt (Traditional Chinese)
```
你是一個 macOS 系統監控助手。你的任務是分析系統資源使用情況，並提供簡潔的繁體中文建議。

規則：
1. 回應必須使用繁體中文
2. 回應長度不超過 30 個字元（包含標點符號）
3. 提供可執行的具體建議，不要只描述問題
4. 語氣友善、專業
5. 只回應建議內容，不要加前綴或解釋

範例：
問題：CPU 使用率 95%，Chrome 佔用 60%
建議：關閉 Chrome 分頁以降低 CPU 負載

問題：記憶體使用率 92%，總共 16GB
建議：關閉未使用的應用程式釋放記憶體

問題：Python 程序佔用 CPU 85%
建議：檢查 Python 程序是否有無限迴圈
```

### Context Template
```
當前系統狀況：
- CPU 使用率：{cpu_percent}%
- 記憶體使用率：{memory_percent}% ({memory_used}GB / {memory_total}GB)
- 磁碟 I/O：讀取 {disk_read}MB/s，寫入 {disk_write}MB/s
- 最高資源消耗程序：{top_process_name} (CPU: {process_cpu}%, Memory: {process_memory}%)

問題類型：{anomaly_type}
詳細資訊：{anomaly_details}

請提供一個不超過 30 字元的繁體中文建議：
```

### Few-Shot Examples

#### Example 1: High CPU from Browser
**Input:**
```
CPU: 95%, Top Process: Chrome (60% CPU)
```
**Expected Output:**
```
關閉 Chrome 分頁降低 CPU 使用
```
**(Character count: 15)**

#### Example 2: High Memory
**Input:**
```
Memory: 92% (14.7GB / 16GB), Top Process: Photoshop (8GB)
```
**Expected Output:**
```
關閉 Photoshop 以釋放記憶體
```
**(Character count: 15)**

#### Example 3: High Process Resource
**Input:**
```
Python process using 85% CPU
```
**Expected Output:**
```
檢查 Python 是否有無限迴圈
```
**(Character count: 16)**

#### Example 4: Disk I/O Spike
**Input:**
```
Disk Write: 500MB/s, Process: Time Machine
```
**Expected Output:**
```
Time Machine 備份中請稍候
```
**(Character count: 16)**

## LangChain Configuration

### LLM Setup
```python
from langchain_community.llms import Ollama

llm = Ollama(
    base_url="http://localhost:11434",
    model="llama3",
    temperature=0.7,
    num_predict=50,  # Max tokens
)
```

### Prompt Template
```python
from langchain.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=[
        "cpu_percent", "memory_percent", "memory_used", "memory_total",
        "disk_read", "disk_write", "top_process_name", "process_cpu",
        "process_memory", "anomaly_type", "anomaly_details"
    ],
    template=CONTEXT_TEMPLATE  # From zh_tw_templates.py
)
```

### Chain Execution
```python
from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=template)
response = await chain.arun(**context_data)
```

## Suggestion Caching

### Cache Strategy
- **Key**: Hash of (anomaly_type, primary_metric_value)
- **Duration**: 60 seconds (configurable)
- **Purpose**: Avoid duplicate suggestions for same issue
- **Storage**: In-memory dict with timestamps

### Example
```python
cache_key = f"{anomaly_type}_{int(primary_value/10)*10}"
# Round to nearest 10 to allow minor fluctuations

if cache_key in cache and (now - cache[cache_key]['time']) < 60:
    return cache[cache_key]['suggestion']
```

## Rate Limiting

### Strategy
- **Limit**: Max 1 AI request per 10 seconds
- **Queue**: Pending anomalies queued during cooldown
- **Priority**: Latest anomaly takes precedence
- **Debounce**: Drop intermediate anomalies if queue > 3

## Response Validation

### Character Length Check
```python
def validate_suggestion(suggestion: str) -> str:
    # Remove whitespace
    clean = suggestion.strip()
    
    # Check length (Traditional Chinese characters)
    if len(clean) > 30:
        # Truncate at 27 chars + "..."
        return clean[:27] + "..."
    
    return clean
```

### Language Verification
```python
import unicodedata

def is_traditional_chinese(text: str) -> bool:
    """Check if text contains primarily Traditional Chinese."""
    chinese_count = sum(
        1 for c in text 
        if '\u4e00' <= c <= '\u9fff'  # CJK Unified Ideographs
    )
    return chinese_count / len(text) > 0.5
```

### Fallback Suggestions
If AI fails or returns invalid response, use template-based fallbacks:

```python
FALLBACK_SUGGESTIONS = {
    "high_cpu": "請檢查高 CPU 使用率的應用程式",
    "high_memory": "建議關閉未使用的應用程式",
    "high_process": "檢查異常程序的資源使用",
    "disk_io": "磁碟 I/O 活動頻繁請稍候",
}
```

## Anomaly Event Integration

### Event Structure
```python
@dataclass
class AnomalyEvent:
    type: str  # 'cpu', 'memory', 'process', 'disk'
    timestamp: float
    severity: str  # 'warning', 'critical'
    metrics: Dict[str, Any]
    top_process: Optional[ProcessInfo]
```

### Event-to-Context Mapping
```python
def build_context(event: AnomalyEvent, system_data: SystemData) -> Dict:
    """Convert anomaly event to AI context."""
    return {
        "cpu_percent": system_data.cpu.total_percent,
        "memory_percent": system_data.memory.percent,
        "memory_used": system_data.memory.used_bytes / 1e9,  # GB
        "memory_total": system_data.memory.total_bytes / 1e9,  # GB
        "disk_read": system_data.disk.read_bytes_per_sec / 1e6,  # MB/s
        "disk_write": system_data.disk.write_bytes_per_sec / 1e6,  # MB/s
        "top_process_name": event.top_process.name if event.top_process else "N/A",
        "process_cpu": event.top_process.cpu_percent if event.top_process else 0,
        "process_memory": event.top_process.memory_percent if event.top_process else 0,
        "anomaly_type": event.type,
        "anomaly_details": format_anomaly_details(event),
    }
```

## Testing Strategy

### Unit Tests
- Mock Ollama API responses
- Test prompt template rendering
- Verify character length enforcement
- Test cache behavior

### Integration Tests
- Test with real Ollama instance (if available)
- Verify end-to-end anomaly → suggestion flow
- Test fallback when Ollama unavailable

### Manual Testing
- Trigger each anomaly type
- Verify Traditional Chinese output
- Check suggestion relevance and quality
- Test rate limiting and caching

## Performance Considerations

### Latency
- **Target**: Suggestion displayed within 2 seconds of anomaly
- **AI inference**: ~500-1500ms (depends on hardware)
- **Total pipeline**: < 2000ms

### Resource Usage
- **CPU**: AI inference is CPU-intensive (acceptable as one-off)
- **Memory**: Model loaded by Ollama (external process)
- **Network**: localhost only, minimal overhead

### Optimization
- Use async/await to prevent blocking
- Run in separate thread (QThread)
- Cache frequently occurring suggestions

## Error Recovery

### Ollama Not Running
- Detect on startup via health check
- Show warning to user: "AI 建議功能需要 Ollama"
- Continue without AI, show template suggestions

### Model Not Downloaded
- Detect via API error
- Show instruction: "請執行: ollama pull llama3"
- Provide download link

### Repeated Failures
- After 3 consecutive failures, disable AI temporarily
- Log errors for debugging
- Retry after 5 minutes

## Future Enhancements

### Learning
- Track which suggestions user acts on
- Adjust prompts based on effectiveness

### Personalization
- Learn user's typical workload patterns
- Customize suggestions to user's habits

### Multi-Language
- Support other languages via configuration
- Simplified Chinese, English support
