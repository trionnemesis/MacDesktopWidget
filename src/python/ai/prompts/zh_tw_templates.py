"""
Traditional Chinese prompt templates for system monitoring AI.
Uses few-shot learning for consistent, concise Traditional Chinese output.
"""

# System prompt defining the AI's role and constraints
SYSTEM_PROMPT = """你是一個 macOS 系統監控助手。你的任務是分析系統資源使用情況，並提供簡潔的台灣繁體中文建議。

規則：
1. 回應必須使用台灣繁體中文（zh-TW）
2. 回應長度不超過 30 個字元（包含標點符號）
3. 提供可執行的具體建議，不要只描述問題
4. 語氣友善、專業
5. 只回應建議內容，不要加前綴或解釋
6. 使用台灣常用詞彙（如：程式、網路、充電，而非程序、网络、充电）

範例：

問題：CPU 使用率 95%，Chrome 佔用 60%
建議：關閉 Chrome 分頁以降低 CPU 負載

問題：記憶體使用率 92%，總共 16GB
建議：關閉未使用的應用程式釋放記憶體

問題：Python 程式佔用 CPU 85%
建議：檢查 Python 程式是否有無限迴圈

問題：磁碟寫入速度 500MB/s，Time Machine 執行中
建議：Time Machine 備份中請稍候

問題：網路上傳速度 80MB/s，OneDrive 同步中
建議：OneDrive 上傳中請稍候

問題：電池剩餘 15%，未連接電源
建議：請盡快連接電源充電

問題：電池健康度 68%，循環次數 850
建議：電池健康度偏低建議更換

問題：CPU 溫度 88°C，風扇全速運轉
建議：調低亮度或關閉高耗能程式"""


# Context template for injecting current system state
CONTEXT_TEMPLATE = """當前系統狀況：
- CPU 使用率：{cpu_percent:.1f}%
- 記憶體使用率：{memory_percent:.1f}% ({memory_used:.1f}GB / {memory_total:.1f}GB)
- 磁碟 I/O：讀取 {disk_read:.1f}MB/s，寫入 {disk_write:.1f}MB/s
- 最高資源消耗程序：{top_process_name} (CPU: {process_cpu:.1f}%, Memory: {process_memory:.1f}%)

問題類型：{anomaly_type}
詳細資訊：{anomaly_details}

請提供一個不超過 30 字元的繁體中文建議："""


# Few-shot examples for different anomaly types
FEW_SHOT_EXAMPLES = {
    "cpu": [
        {
            "context": "CPU: 95%, Top Process: Chrome (60% CPU)",
            "suggestion": "關閉 Chrome 分頁降低 CPU 使用"
        },
        {
            "context": "CPU: 88%, Top Process: Safari (55% CPU)",
            "suggestion": "關閉 Safari 未使用的視窗"
        },
        {
            "context": "CPU: 92%, Top Process: python3 (75% CPU)",
            "suggestion": "檢查 Python 程序是否有問題"
        },
        {
            "context": "CPU: 85%, Top Process: node (68% CPU)",
            "suggestion": "重啟 Node.js 應用程式"
        },
    ],
    
    "memory": [
        {
            "context": "Memory: 92% (14.7GB / 16GB), Top Process: Photoshop (8GB)",
            "suggestion": "關閉 Photoshop 以釋放記憶體"
        },
        {
            "context": "Memory: 94% (7.5GB / 8GB), Top Process: Chrome (3.2GB)",
            "suggestion": "關閉 Chrome 分頁釋放記憶體"
        },
        {
            "context": "Memory: 91% (29GB / 32GB), Top Process: Docker (12GB)",
            "suggestion": "清理 Docker 容器釋放記憶體"
        },
        {
            "context": "Memory: 93% (15GB / 16GB), Top Process: Xcode (6GB)",
            "suggestion": "關閉 Xcode 專案釋放記憶體"
        },
    ],
    
    "process_cpu": [
        {
            "context": "Process: Chrome using 85% CPU",
            "suggestion": "Chrome 佔用過高請檢查擴充功能"
        },
        {
            "context": "Process: python3 using 92% CPU",
            "suggestion": "Python 程序異常請檢查程式碼"
        },
        {
            "context": "Process: kernel_task using 78% CPU",
            "suggestion": "系統核心忙碌中請稍候"
        },
        {
            "context": "Process: Safari using 65% CPU",
            "suggestion": "Safari 網頁佔用資源過高"
        },
    ],
    
    "process_memory": [
        {
            "context": "Process: Photoshop using 55% Memory (8.8GB)",
            "suggestion": "Photoshop 記憶體過高建議重啟"
        },
        {
            "context": "Process: Chrome using 62% Memory (9.9GB)",
            "suggestion": "Chrome 記憶體過高請關閉分頁"
        },
        {
            "context": "Process: Docker using 58% Memory (9.3GB)",
            "suggestion": "Docker 容器過多請清理"
        },
        {
            "context": "Process: IntelliJ using 51% Memory (8.2GB)",
            "suggestion": "IntelliJ 記憶體過高請重啟"
        },
    ],
    
    "disk_io": [
        {
            "context": "Disk Write: 500MB/s, Process: Time Machine",
            "suggestion": "Time Machine 備份中請稍候"
        },
        {
            "context": "Disk Read: 350MB/s, Process: Spotlight",
            "suggestion": "Spotlight 索引中請稍候"
        },
        {
            "context": "Disk Write: 450MB/s, Process: Docker",
            "suggestion": "Docker 映像建置中請稍候"
        },
        {
            "context": "Disk Read: 280MB/s, Process: Chrome",
            "suggestion": "瀏覽器快取讀取中"
        },
    ],

    "network_io": [
        {
            "context": "Network Upload: 80MB/s, Process: OneDrive",
            "suggestion": "OneDrive 上傳中請稍候"
        },
        {
            "context": "Network Download: 120MB/s, Process: Steam",
            "suggestion": "Steam 下載遊戲中請稍候"
        },
        {
            "context": "Network Upload: 65MB/s, Process: Dropbox",
            "suggestion": "Dropbox 同步中請稍候"
        },
        {
            "context": "Network Download: 95MB/s, Process: Chrome",
            "suggestion": "瀏覽器下載大型檔案中"
        },
    ],

    "battery_low": [
        {
            "context": "Battery: 15%, Not Charging",
            "suggestion": "電量不足請盡快充電"
        },
        {
            "context": "Battery: 8%, Not Charging",
            "suggestion": "電量嚴重不足請立即充電"
        },
        {
            "context": "Battery: 18%, Estimated 25 min remaining",
            "suggestion": "剩餘約 25 分鐘請盡快充電"
        },
        {
            "context": "Battery: 12%, Not Charging",
            "suggestion": "電量過低請連接電源"
        },
    ],

    "battery_health": [
        {
            "context": "Battery Health: 68%, Cycle Count: 850",
            "suggestion": "電池健康度偏低建議更換"
        },
        {
            "context": "Battery Health: 72%, Cycle Count: 920",
            "suggestion": "電池老化建議考慮更換"
        },
        {
            "context": "Battery Health: 65%, Condition: Replace Soon",
            "suggestion": "電池狀況差請聯繫維修"
        },
        {
            "context": "Battery Health: 75%, Cycle Count: 780",
            "suggestion": "電池健康度下降請留意"
        },
    ],

    "high_temperature": [
        {
            "context": "CPU Temp: 88°C, Avg Temp: 82°C",
            "suggestion": "CPU 溫度過高請降低負載"
        },
        {
            "context": "GPU Temp: 92°C, Max Temp: 92°C",
            "suggestion": "GPU 溫度過高建議暫停運算"
        },
        {
            "context": "CPU Temp: 85°C, Fan Speed: High",
            "suggestion": "溫度偏高建議調低亮度"
        },
        {
            "context": "Max Temp: 90°C, Process: Xcode",
            "suggestion": "編譯中溫度高屬正常現象"
        },
    ],
}


# Fallback suggestions when AI is unavailable
FALLBACK_SUGGESTIONS = {
    "cpu": "請檢查高 CPU 使用率的應用程式",
    "memory": "建議關閉未使用的應用程式",
    "process_cpu": "檢查異常程式的 CPU 使用",
    "process_memory": "檢查異常程式的記憶體使用",
    "disk_io": "磁碟 I/O 活動頻繁請稍候",
    "network_io": "網路流量異常請檢查同步程式",
    "battery_low": "電池電量不足請盡快充電",
    "battery_health": "電池健康度下降請留意",
    "high_temperature": "系統溫度過高請降低負載",
}


def get_anomaly_type_name(anomaly_type: str) -> str:
    """
    Get Traditional Chinese name for anomaly type.

    Args:
        anomaly_type: Anomaly type code.

    Returns:
        Traditional Chinese name.
    """
    type_names = {
        "cpu": "CPU 使用率過高",
        "memory": "記憶體使用率過高",
        "process_cpu": "程式 CPU 使用率過高",
        "process_memory": "程式記憶體使用率過高",
        "disk_io": "磁碟 I/O 活動頻繁",
        "network_io": "網路流量異常",
        "battery_low": "電池電量不足",
        "battery_health": "電池健康度下降",
        "high_temperature": "系統溫度過高",
    }
    return type_names.get(anomaly_type, "系統資源異常")


def format_anomaly_details(anomaly_type: str, metrics: dict, process_name: str = None) -> str:
    """
    Format anomaly details in Traditional Chinese.
    
    Args:
        anomaly_type: Type of anomaly.
        metrics: Anomaly metrics.
        process_name: Related process name if applicable.
    
    Returns:
        Formatted details string.
    """
    if anomaly_type == "cpu":
        cpu_pct = metrics.get("cpu_percent", 0)
        if process_name:
            return f"CPU 使用率 {cpu_pct:.1f}%，{process_name} 佔用最高"
        return f"CPU 使用率 {cpu_pct:.1f}%"
    
    elif anomaly_type == "memory":
        mem_pct = metrics.get("memory_percent", 0)
        mem_used = metrics.get("memory_used_gb", 0)
        mem_total = metrics.get("memory_total_gb", 0)
        if process_name:
            return f"記憶體 {mem_pct:.1f}% ({mem_used:.1f}GB/{mem_total:.1f}GB)，{process_name} 佔用最高"
        return f"記憶體使用率 {mem_pct:.1f}%"
    
    elif anomaly_type == "process_cpu":
        cpu_pct = metrics.get("cpu_percent", 0)
        return f"{process_name or '程序'} 佔用 CPU {cpu_pct:.1f}%"
    
    elif anomaly_type == "process_memory":
        mem_pct = metrics.get("memory_percent", 0)
        return f"{process_name or '程序'} 佔用記憶體 {mem_pct:.1f}%"
    
    elif anomaly_type == "disk_io":
        read_mb = metrics.get("read_mb_per_sec", 0)
        write_mb = metrics.get("write_mb_per_sec", 0)
        max_io = max(read_mb, write_mb)
        return f"磁碟 I/O {max_io:.1f}MB/s"

    elif anomaly_type == "network_io":
        upload_mb = metrics.get("upload_mb_per_sec", 0)
        download_mb = metrics.get("download_mb_per_sec", 0)
        total_mb = metrics.get("total_mb_per_sec", 0)
        if process_name:
            return f"網路流量 {total_mb:.1f}MB/s，{process_name} 佔用最高"
        return f"網路流量 {total_mb:.1f}MB/s"

    elif anomaly_type == "battery_low":
        battery_pct = metrics.get("battery_percent", 0)
        time_remaining = metrics.get("time_remaining_hours", 0)
        if time_remaining > 0:
            return f"電池剩餘 {battery_pct:.0f}%，約 {time_remaining:.0f} 小時"
        return f"電池剩餘 {battery_pct:.0f}%"

    elif anomaly_type == "battery_health":
        health_pct = metrics.get("health_percent", 0)
        cycle_count = metrics.get("cycle_count", 0)
        return f"電池健康度 {health_pct}%，循環 {cycle_count} 次"

    elif anomaly_type == "high_temperature":
        max_temp = metrics.get("max_temp", 0)
        cpu_temp = metrics.get("cpu_temp", 0)
        if cpu_temp > 0:
            return f"CPU 溫度 {cpu_temp:.0f}°C，最高 {max_temp:.0f}°C"
        return f"系統溫度 {max_temp:.0f}°C"

    return "系統資源異常"


def build_prompt_context(anomaly_event, system_data) -> dict:
    """
    Build context dictionary for prompt template from anomaly event and system data.
    
    Args:
        anomaly_event: AnomalyEvent object.
        system_data: SystemData object.
    
    Returns:
        Dictionary with context variables.
    """
    # Extract process info
    process_name = "N/A"
    process_cpu = 0.0
    process_memory = 0.0
    
    if anomaly_event.related_process:
        process_name = anomaly_event.related_process.name
        process_cpu = anomaly_event.related_process.cpu_percent
        process_memory = anomaly_event.related_process.memory_percent
    
    # Build context
    context = {
        "cpu_percent": system_data.cpu.total_percent,
        "memory_percent": system_data.memory.percent,
        "memory_used": system_data.memory.used_gb,
        "memory_total": system_data.memory.total_gb,
        "disk_read": system_data.disk.read_mb_per_sec,
        "disk_write": system_data.disk.write_mb_per_sec,
        "top_process_name": process_name,
        "process_cpu": process_cpu,
        "process_memory": process_memory,
        "anomaly_type": get_anomaly_type_name(anomaly_event.type.value),
        "anomaly_details": format_anomaly_details(
            anomaly_event.type.value,
            anomaly_event.metrics,
            process_name if process_name != "N/A" else None
        ),
    }
    
    return context
