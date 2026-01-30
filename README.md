# File Analyzer

A modern, AI-like file analyzer with visual storage exploration, interactive charts, and intelligent insights.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## 🎨 Features

### Modern AI-like Interface
- **Glassmorphism Design**: Beautiful translucent cards with glow effects
- **Smooth Animations**: Animated counters, progress bars, and transitions
- **Interactive Charts**: Plotly-powered visualizations with hover effects
- **Dark Theme**: Easy-on-the-eyes dark color scheme

### Smart Features
- **Quick Search**: Instant file/folder search with fuzzy matching
- **Recent Folders**: Quickly re-scan previously analyzed folders
- **File Preview**: Preview text, code, and images without opening
- **Smart Insights**: AI-powered recommendations and warnings

### Visual Analytics
- **Storage Distribution**: Interactive pie/donut charts
- **Folder Comparison**: Horizontal bar charts
- **Category Treemap**: Visual storage breakdown
- **File Extensions**: Distribution analysis
- **Size Distribution**: Histogram of file sizes

## 🚀 Getting Started

### Installation

```bash
# Clone or download the project
cd file_analyzer

# Install dependencies
pip install -r requirements.txt

# For the full modern experience (interactive charts)
pip install PySide6-WebEngine
```

### Running the Application

```bash
# Run with modern AI-like interface (default)
python main.py

# Or explicitly
python main.py --modern

# Run with classic interface
python main.py --classic
```

## 📸 Screenshots

### Modern Interface
- Welcome screen with quick actions
- Real-time scanning with animated progress
- Interactive dashboard with multiple chart types
- Smart search with instant results

### Classic Interface
- Traditional split-pane layout
- Matplotlib-based charts
- Tree view navigation

## 🛠️ Architecture

```
file_analyzer/
├── main.py                 # Entry point with UI selector
├── modern_gui.py           # Modern AI-like interface
├── modern_styles.py        # Glassmorphism theme
├── modern_components.py    # Animated UI components
├── interactive_charts.py   # Plotly-based charts
├── search_engine.py        # Fast file search
├── file_preview.py         # File content preview
├── gui.py                  # Classic interface
├── styles.py               # Classic theme
├── scanner.py              # File system scanner
├── analyzer.py             # Data analysis
├── models.py               # Data models
├── visualizer.py           # Matplotlib charts
└── requirements.txt        # Dependencies
```

## 🎯 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + O` | Open folder |
| `F5` | Refresh scan |
| `Ctrl + Q` | Quit |

## 🧪 Advanced Features

### Search Syntax
- **Simple**: Just type any text to search
- **Glob**: Use `*.py` or `test_*` patterns
- **Regex**: Start with `/` for regex search (e.g., `/\d{4}`)

### File Categories
Files are automatically categorized:
- 📄 Documents (PDF, DOC, TXT, etc.)
- 🖼️ Images (JPG, PNG, GIF, etc.)
- 🎵 Audio (MP3, WAV, FLAC, etc.)
- 🎬 Video (MP4, AVI, MKV, etc.)
- 💻 Code (PY, JS, HTML, CSS, etc.)
- 📦 Archives (ZIP, RAR, 7Z, etc.)
- 📊 Data (CSV, JSON, XML, etc.)
- ⚙️ Executables (EXE, MSI, etc.)

## 📦 Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller FileAnalyzer.spec

# Or create new spec
pyinstaller --name="FileAnalyzer" --windowed --icon=icon.ico main.py
```

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📝 License

MIT License - Feel free to use and modify for your own projects.

## 🙏 Credits

- Icons: Emoji icons for cross-platform compatibility
- Charts: Plotly for interactive visualizations
- Theme: Inspired by Catppuccin color palette
- UI Design: Inspired by OpenCode, Perplexity, and Claude interfaces
