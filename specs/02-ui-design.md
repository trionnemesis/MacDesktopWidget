# UI Design Specification

## Overview

Design specification for the transparent, frameless macOS desktop widget with glassmorphism aesthetics.

## Core Requirements

### Transparency & Frameless Window
- **Framework**: PyQt6 with PyQt6-Frameless-Window
- **Transparency**: 90% opacity (configurable via `UIConfig.transparency`)
- **Frameless**: No OS window decorations
- **Always on Top**: Optional (default: enabled)
- **Draggable**: User can drag window by clicking anywhere

### Glassmorphism Effect
- **Background Blur**: 20px blur radius
- **Background Opacity**: 30% dark background
- **Border**: 1px subtle border with gradient
- **Shadow**: Soft drop shadow for depth
- **Color Palette**: Dark theme with cyan/blue accents

## Window Specifications

### Dimensions
- **Default Width**: 400px
- **Default Height**: 600px
- **Minimum Width**: 300px
- **Minimum Height**: 400px
- **Resizable**: No (fixed size for consistent layout)

### Positioning
- **Default**: Top-right corner with 20px margin
- **Persistence**: Save position on close, restore on open
- **Multi-monitor**: Position relative to primary display

## Layout Structure

```
┌─────────────────────────────────────────┐
│  ╔═══════════════════════════════════╗  │
│  ║       Mac Desktop Widget          ║  │ ← Title Bar (minimal, draggable)
│  ╚═══════════════════════════════════╝  │
│  ┌─────────┐  ┌─────────┐              │
│  │   CPU   │  │ Memory  │              │ ← Resource Gauges
│  │   45%   │  │  8.2GB  │              │
│  └─────────┘  └─────────┘              │
│  ┌─────────┐  ┌─────────┐              │
│  │  Disk   │  │   GPU   │              │
│  │ 120MB/s │  │   32%   │              │
│  └─────────┘  └─────────┘              │
│  ┌───────────────────────────────────┐ │
│  │     Top Processes                 │ │ ← Process List
│  │  1. Chrome      45%    2.1GB      │ │
│  │  2. Python      12%    456MB      │ │
│  │  3. Safari       8%    1.8GB      │ │
│  │  ...                               │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  🤖 建議: 關閉Chrome節省記憶體   │ │ ← AI Suggestion
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Widget Specifications

### CPU Widget
- **Type**: Circular progress indicator
- **Display**:
  - Center: Percentage (e.g., "45%")
  - Outer ring: Animated progress circle
  - Below: "CPU" label
- **Colors**:
  - 0-60%: Green (#00FF88)
  - 60-80%: Yellow (#FFD700)
  - 80-100%: Red (#FF4444)
- **Animation**: Smooth transition (300ms ease-in-out)
- **Size**: 80x80px

### Memory Widget
- **Type**: Horizontal progress bar with text
- **Display**:
  - Top: "Memory" label
  - Bar: Filled progress bar with gradient
  - Bottom: "8.2GB / 16.0GB (51%)"
- **Colors**: Same thresholds as CPU
- **Animation**: Width transition (300ms)
- **Size**: 180x60px

### Disk Widget
- **Type**: Combined usage + I/O display
- **Display**:
  - Top: "Disk" label
  - Middle: Read/Write indicators with icons
  - Bottom: "↑ 120MB/s ↓ 85MB/s"
  - Background: Animated pulse on I/O activity
- **Colors**: Cyan (#00BFFF) for activity
- **Size**: 180x60px

### GPU Widget
- **Type**: Gauge similar to CPU
- **Display**:
  - Center: Utilization percentage
  - Label: "GPU"
  - Fallback: "N/A" if unavailable
- **Colors**: Purple gradient (#9D4EDD to #C77DFF)
- **Size**: 80x80px

### Process Widget
- **Type**: Scrollable table
- **Columns**:
  1. Rank (#1-10)
  2. Process Name (truncated)
  3. CPU %
  4. Memory (GB/MB)
- **Rows**: 10 visible processes
- **Sorting**: Toggle between CPU/Memory sort
- **Hover**: Highlight row, show full process name tooltip
- **Click**: Show process details dialog
- **Color Coding**:
  - High resource: Red background tint
  - Medium: Yellow tint
  - Normal: Transparent
- **Size**: Full width, 200px height

### AI Suggestion Widget
- **Type**: Alert-style banner
- **Display**:
  - Icon: 🤖 (robot emoji)
  - Text: AI suggestion in Traditional Chinese
  - Character limit: ≤30 characters
- **Behavior**:
  - Slide in from bottom with animation (400ms)
  - Display for 10 seconds
  - Fade out (400ms)
  - Show only when new suggestion arrives
- **Colors**:
  - Warning: Orange background (#FF9800)
  - Info: Blue background (#2196F3)
  - Tip: Green background (#4CAF50)
- **Size**: Full width, auto height (single line)

## Color Palette

### Primary Colors
- **Background**: `rgba(20, 20, 30, 0.3)` - Dark translucent
- **Border**: `rgba(100, 200, 255, 0.3)` - Cyan translucent
- **Text Primary**: `#FFFFFF` - White
- **Text Secondary**: `rgba(255, 255, 255, 0.7)` - Translucent white

### Accent Colors
- **Success/Low**: `#00FF88` - Green
- **Warning/Medium**: `#FFD700` - Yellow
- **Error/High**: `#FF4444` - Red
- **Info**: `#00BFFF` - Cyan
- **AI**: `#9D4EDD` - Purple

### Glassmorphism Effect
```css
background: rgba(20, 20, 30, 0.3);
backdrop-filter: blur(20px);
border: 1px solid rgba(100, 200, 255, 0.3);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
```

## Typography

### Font Family
- **Primary**: SF Pro Display (macOS native)
- **Fallback**: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto

### Font Sizes
- **Title**: 16px, bold
- **Widget Label**: 12px, medium
- **Main Value**: 24px, bold (CPU/Memory %)
- **Secondary Value**: 10px, regular
- **Process Table**: 11px, regular
- **AI Suggestion**: 13px, medium

## Animations

### Value Changes
- **Duration**: 300ms
- **Easing**: ease-in-out
- **Property**: Smooth interpolation of numbers

### Widget Transitions
- **Duration**: 400ms
- **Easing**: cubic-bezier(0.4, 0.0, 0.2, 1)
- **Transforms**: Slide, fade

### Micro-animations
- **Pulse**: On I/O activity (1s cycle)
- **Glow**: On threshold breach (subtle)
- **Bounce**: On new AI suggestion

## Accessibility

### Contrast
- All text must have minimum 4.5:1 contrast ratio
- Use white text on dark backgrounds

### Keyboard Navigation
- Tab through interactive elements
- Enter/Space to activate
- ESC to close dialogs

### Screen Reader
- Proper ARIA labels for all widgets
- Announce value changes only on significant changes (> 5%)

## Responsive Behavior

### Window Resizing
- Fixed size (no resizing)
- Maintain aspect ratio if resizing added in future

### Content Overflow
- Process list: Scrollable
- AI suggestion: Truncate with ellipsis if exceeds width
- Widget values: Auto-scale font size if needed

## QSS Stylesheet Structure

### File Organization
```
src/python/ui/styles/
├── main.qss          # Main stylesheet
├── widgets.qss       # Widget-specific styles
├── animations.qss    # Animation definitions
└── colors.qss        # Color variables (if supported)
```

### Key Style Classes
- `.MainWindow`: Frameless transparent window
- `.CPUWidget`: CPU gauge styles
- `.MemoryWidget`: Memory bar styles
- `.DiskWidget`: Disk I/O styles
- `.GPUWidget`: GPU gauge styles
- `.ProcessWidget`: Process table styles
- `.AIWidget`: AI suggestion banner styles

## Performance Considerations

### Rendering
- **Target**: 60 FPS smooth animations
- **Technique**: Use Qt's Graphics View Framework for complex graphics
- **Optimization**: Reduce unnecessary repaints

### Transparency
- **Cost**: Transparency and blur are expensive
- **Mitigation**: Use static background blur, not recalculated each frame

### Updates
- **Throttling**: Update UI only when values change significantly
- **Batching**: Batch multiple value updates in single repaint

## Platform-Specific Considerations

### macOS
- Use native window controls APIs
- Apply macOS-specific blur effects (NSVisualEffectView equivalent in Qt)
- Respect system dark mode settings

### Windows (Development)
- Transparency works but blur might differ
- Fallback to simple transparency without blur
- Test UI appearance on Windows

## Testing Requirements

### Visual Tests
- Screenshot comparison for widget layouts
- Verify glassmorphism effect renders correctly
- Test all color states (normal, warning, error)

### Interaction Tests
- Test drag-to-move functionality
- Verify click handlers for process list
- Test keyboard navigation

### Animation Tests
- Verify smooth transitions
- Test edge cases (rapid value changes)
- Performance profiling for 60 FPS target
