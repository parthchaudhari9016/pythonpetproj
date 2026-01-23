"""
Qt Stylesheet definitions for dark theme with enhanced section styling.
"""

# Catppuccin Mocha inspired color palette
COLORS = {
    'base': '#1e1e2e',
    'mantle': '#181825',
    'crust': '#11111b',
    'surface0': '#313244',
    'surface1': '#45475a',
    'surface2': '#585b70',
    'overlay0': '#6c7086',
    'overlay1': '#7f849c',
    'text': '#cdd6f4',
    'subtext0': '#a6adc8',
    'subtext1': '#bac2de',
    'blue': '#89b4fa',
    'lavender': '#b4befe',
    'sapphire': '#74c7ec',
    'sky': '#89dceb',
    'teal': '#94e2d5',
    'green': '#a6e3a1',
    'yellow': '#f9e2af',
    'peach': '#fab387',
    'maroon': '#eba0ac',
    'red': '#f38ba8',
    'mauve': '#cba6f7',
    'pink': '#f5c2e7',
    'rosewater': '#f5e0dc',
}

DARK_STYLESHEET = f"""
/* Main Window */
QMainWindow {{
    background-color: {COLORS['base']};
}}

QWidget {{
    background-color: {COLORS['base']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}

/* Scroll Areas */
QScrollArea {{
    border: none;
    background-color: {COLORS['base']};
}}

QScrollArea > QWidget > QWidget {{
    background-color: {COLORS['base']};
}}

QScrollBar:vertical {{
    background-color: {COLORS['surface0']};
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['surface2']};
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['overlay0']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['surface0']};
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['surface2']};
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}}

/* Tree Widget - Enhanced */
QTreeWidget {{
    background-color: {COLORS['surface0']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 10px;
    padding: 8px;
    outline: none;
    font-size: 12px;
}}

QTreeWidget::item {{
    padding: 8px 10px;
    border-radius: 6px;
    margin: 1px 0;
}}

QTreeWidget::item:hover {{
    background-color: {COLORS['surface1']};
}}

QTreeWidget::item:selected {{
    background-color: {COLORS['blue']};
    color: {COLORS['base']};
}}

QTreeWidget::branch {{
    background-color: transparent;
}}

QTreeWidget::branch:has-siblings:!adjoins-item {{
    border-image: none;
}}

QTreeWidget::branch:has-siblings:adjoins-item {{
    border-image: none;
}}

QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
    border-image: none;
}}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    border-image: none;
    image: none;
}}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    border-image: none;
    image: none;
}}

QHeaderView::section {{
    background-color: {COLORS['surface1']};
    color: {COLORS['text']};
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid {COLORS['blue']};
    font-weight: bold;
    font-size: 12px;
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['blue']};
    color: {COLORS['crust']};
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLORS['sapphire']};
}}

QPushButton:pressed {{
    background-color: {COLORS['lavender']};
}}

QPushButton:disabled {{
    background-color: {COLORS['surface2']};
    color: {COLORS['overlay0']};
}}

/* Labels */
QLabel {{
    color: {COLORS['text']};
    background-color: transparent;
}}

QLabel#title {{
    font-size: 22px;
    font-weight: bold;
    color: {COLORS['text']};
}}

QLabel#subtitle {{
    font-size: 13px;
    color: {COLORS['subtext0']};
}}

QLabel#stat-value {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['blue']};
}}

QLabel#stat-label {{
    font-size: 11px;
    color: {COLORS['subtext0']};
    text-transform: uppercase;
}}

/* Group Boxes / Cards */
QGroupBox {{
    background-color: {COLORS['surface0']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 12px;
    margin-top: 15px;
    padding: 15px;
    padding-top: 25px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 10px;
    color: {COLORS['text']};
    background-color: {COLORS['surface0']};
}}

/* Frames / Cards - Main sections */
QFrame#card {{
    background-color: {COLORS['surface0']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 12px;
    padding: 10px;
}}

QFrame#stat-card {{
    background-color: {COLORS['surface0']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 10px;
    padding: 10px;
}}

QFrame#stat-card:hover {{
    border: 1px solid {COLORS['blue']};
    background-color: {COLORS['surface1']};
}}

/* Text Edit for insights */
QTextEdit {{
    background-color: {COLORS['mantle']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 8px;
    padding: 12px;
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: {COLORS['blue']};
}}

QTextEdit:focus {{
    border: 1px solid {COLORS['blue']};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS['surface1']};
    border-radius: 2px;
}}

QSplitter::handle:horizontal {{
    width: 4px;
    margin: 5px 2px;
}}

QSplitter::handle:vertical {{
    height: 4px;
    margin: 2px 5px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['blue']};
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS['surface0']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text']};
    height: 22px;
    font-size: 11px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['blue']}, stop:1 {COLORS['sapphire']});
    border-radius: 5px;
}}

/* Tab Widget - Enhanced */
QTabWidget::pane {{
    background-color: {COLORS['surface0']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 10px;
    padding: 10px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS['surface0']};
    color: {COLORS['subtext0']};
    padding: 10px 16px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['surface1']};
    color: {COLORS['text']};
    border-bottom: 2px solid {COLORS['blue']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['surface1']};
    color: {COLORS['text']};
}}

/* Tooltips */
QToolTip {{
    background-color: {COLORS['surface0']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['surface1']};
    border-radius: 6px;
    padding: 8px;
    font-size: 12px;
}}

/* Status Bar */
QStatusBar {{
    background-color: {COLORS['mantle']};
    color: {COLORS['subtext0']};
    border-top: 1px solid {COLORS['surface1']};
    padding: 5px;
    font-size: 12px;
}}

QStatusBar::item {{
    border: none;
}}
"""
