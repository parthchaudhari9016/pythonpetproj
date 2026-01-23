# File Analyzer - Visual Storage Explorer

A modern Windows desktop application that analyzes folder contents and provides visual insights.

## Features

- 📁 **Interactive Folder Tree** - Navigate folder structure with size and file count info
- 📊 **Category Analysis** - Automatic file classification (Documents, Media, Code, etc.)
- 📈 **Visual Charts** - Pie charts, bar graphs, and distribution plots
- 💡 **Smart Insights** - Human-readable explanations of folder contents
- ⚠️ **Warnings** - Alerts for large files, storage issues, etc.
- 🌙 **Dark Theme** - Modern Catppuccin-inspired design

## Screenshot

![File Analyzer](icon.png)

## Requirements

- Python 3.9+
- PySide6
- Matplotlib

## Installation

```bash
pip install PySide6 matplotlib
```

## Running

```bash
python main.py
```

## Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "FileAnalyzer" --icon "icon.ico" main.py
```

## Project Structure

```
file_analyzer/
├── main.py          # Entry point
├── gui.py           # Main window and UI components
├── scanner.py       # Background directory scanner
├── analyzer.py      # Statistics and insight generation
├── visualizer.py    # Chart components (Matplotlib)
├── models.py        # Data structures
├── styles.py        # Dark theme stylesheet
├── icon.ico         # App icon
└── icon.png         # App icon (PNG)
```

## Author

Hobbiepy
