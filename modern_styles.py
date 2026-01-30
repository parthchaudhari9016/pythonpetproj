"""
Modern UI styles with glassmorphism, gradients, and animations.
Inspired by OpenCode, Perplexity, and Claude interfaces.
"""

# Modern dark palette with vibrant accents
COLORS = {
    # Base
    'bg_primary': '#0d0d12',
    'bg_secondary': '#16161f',
    'bg_tertiary': '#1e1e2e',
    'bg_card': '#252536',
    'bg_card_hover': '#2d2d42',
    'bg_glass': 'rgba(30, 30, 46, 0.7)',
    
    # Surfaces
    'surface': '#252536',
    'surface_hover': '#2f2f45',
    'surface_active': '#36364f',
    'border': '#313244',
    'border_hover': '#585b70',
    'border_accent': '#89b4fa',
    
    # Text
    'text_primary': '#f8f8f8',
    'text_secondary': '#a6adc8',
    'text_muted': '#6c7086',
    
    # Accents (vibrant gradient palette)
    'accent_blue': '#60a5fa',
    'accent_cyan': '#22d3ee',
    'accent_purple': '#c084fc',
    'accent_pink': '#f472b6',
    'accent_green': '#4ade80',
    'accent_yellow': '#facc15',
    'accent_orange': '#fb923c',
    'accent_red': '#f87171',
    
    # Gradients
    'gradient_hero': 'linear-gradient(135deg, #60a5fa 0%, #c084fc 50%, #f472b6 100%)',
    'gradient_blue': 'linear-gradient(135deg, #60a5fa 0%, #22d3ee 100%)',
    'gradient_purple': 'linear-gradient(135deg, #c084fc 0%, #f472b6 100%)',
    'gradient_green': 'linear-gradient(135deg, #4ade80 0%, #22d3ee 100%)',
    'gradient_orange': 'linear-gradient(135deg, #fb923c 0%, #facc15 100%)',
}

# Category colors with modern palette
CATEGORY_COLORS = {
    'Documents': ('#60a5fa', '#3b82f6'),      # Blue gradient
    'Images': ('#c084fc', '#a855f7'),         # Purple gradient
    'Audio': ('#22d3ee', '#06b6d4'),          # Cyan gradient
    'Video': ('#f472b6', '#ec4899'),          # Pink gradient
    'Code': ('#4ade80', '#22c55e'),           # Green gradient
    'Archives': ('#fb923c', '#f97316'),       # Orange gradient
    'Data': ('#facc15', '#eab308'),           # Yellow gradient
    'Executables': ('#f87171', '#ef4444'),    # Red gradient
    'Others': ('#94a3b8', '#64748b'),         # Gray gradient
}

MODERN_STYLESHEET = f"""
/* ===== GLOBAL STYLES ===== */
QMainWindow, QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 13px;
    border: none;
}}

/* ===== SCROLLBARS - Minimal Modern ===== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    min-height: 40px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['border_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 6px;
    margin: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    min-width: 40px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['border_hover']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ===== GLASSMORPHISM CARD ===== */
QFrame#glass-card {{
    background-color: rgba(37, 37, 54, 0.6);
    border: 1px solid rgba(137, 180, 250, 0.15);
    border-radius: 16px;
}}

QFrame#glass-card:hover {{
    border: 1px solid rgba(137, 180, 250, 0.3);
    background-color: rgba(37, 37, 54, 0.8);
}}

/* ===== STAT CARDS - Modern Gradient ===== */
QFrame#stat-card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 20px;
}}

QFrame#stat-card:hover {{
    border: 1px solid {COLORS['border_hover']};
    background-color: {COLORS['bg_card_hover']};
}}

/* ===== MODERN BUTTONS ===== */
QPushButton#primary-btn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #60a5fa, stop:1 #c084fc);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    font-weight: 600;
    font-size: 14px;
}}

QPushButton#primary-btn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #3b82f6, stop:1 #a855f7);
}}

QPushButton#primary-btn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #2563eb, stop:1 #9333ea);
}}

QPushButton#secondary-btn {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton#secondary-btn:hover {{
    background-color: {COLORS['surface_hover']};
    border: 1px solid {COLORS['border_hover']};
}}

QPushButton#icon-btn {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-radius: 8px;
    padding: 8px;
    font-size: 16px;
}}

QPushButton#icon-btn:hover {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_primary']};
}}

QPushButton#nav-btn {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    text-align: left;
}}

QPushButton#nav-btn:hover {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_primary']};
}}

QPushButton#nav-btn-active {{
    background-color: {COLORS['surface_active']};
    color: {COLORS['accent_blue']};
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}

/* ===== MODERN INPUTS ===== */
QLineEdit {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['accent_blue']};
}}

QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}

/* ===== TREE WIDGET - Modern Clean ===== */
QTreeWidget {{
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 13px;
}}

QTreeWidget::item {{
    padding: 10px 12px;
    border-radius: 8px;
    margin: 2px 4px;
    color: {COLORS['text_secondary']};
}}

QTreeWidget::item:hover {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_primary']};
}}

QTreeWidget::item:selected {{
    background-color: {COLORS['surface_active']};
    color: {COLORS['accent_blue']};
}}

QTreeWidget::branch {{
    background-color: transparent;
}}

QHeaderView::section {{
    background-color: transparent;
    color: {COLORS['text_muted']};
    padding: 12px;
    border: none;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ===== TABS - Minimal ===== */
QTabWidget::pane {{
    background-color: transparent;
    border: none;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_muted']};
    padding: 12px 20px;
    margin-right: 4px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: {COLORS['accent_blue']};
    border-bottom: 2px solid {COLORS['accent_blue']};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['text_secondary']};
}}

/* ===== SPLITTER ===== */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
    margin: 4px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['border_hover']};
}}

/* ===== PROGRESS BAR - Modern ===== */
QProgressBar {{
    background-color: {COLORS['surface']};
    border: none;
    border-radius: 6px;
    height: 6px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #60a5fa, stop:1 #c084fc);
    border-radius: 6px;
}}

/* ===== TEXT EDIT - Clean ===== */
QTextEdit {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
    font-size: 14px;
    line-height: 1.6;
}}

QTextEdit:focus {{
    border: 1px solid {COLORS['border_hover']};
}}

/* ===== COMBOBOX ===== */
QComboBox {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 10px 14px;
    min-width: 120px;
}}

QComboBox:hover {{
    border: 1px solid {COLORS['border_hover']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    selection-background-color: {COLORS['surface_active']};
}}

/* ===== LIST WIDGET ===== */
QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
}}

QListWidget::item {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 12px;
    margin: 4px 0;
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_card_hover']};
    border: 1px solid {COLORS['border_hover']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['surface_active']};
    border: 1px solid {COLORS['accent_blue']};
}}

/* ===== TOOLTIP ===== */
QToolTip {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
    border-top: 1px solid {COLORS['border']};
    padding: 8px 16px;
}}

/* ===== MENU ===== */
QMenu {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 8px;
}}

QMenu::item {{
    padding: 10px 16px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: {COLORS['surface_hover']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border']};
    margin: 6px 0;
}}

/* ===== DIALOGS ===== */
QDialog {{
    background-color: {COLORS['bg_primary']};
}}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    margin-top: 16px;
    padding: 20px;
    padding-top: 24px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    padding: 0 12px;
    color: {COLORS['text_secondary']};
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ===== LOADING SPINNER ===== */
QFrame#loading-container {{
    background-color: {COLORS['bg_primary']};
}}

/* ===== ANIMATED ELEMENTS ===== */
QFrame#animated-card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
}}

/* ===== SIDEBAR ===== */
QFrame#sidebar {{
    background-color: {COLORS['bg_secondary']};
    border-right: 1px solid {COLORS['border']};
}}

/* ===== CONTENT AREA ===== */
QFrame#content-area {{
    background-color: {COLORS['bg_primary']};
}}

/* ===== SEARCH BOX ===== */
QFrame#search-box {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
}}

QFrame#search-box:focus-within {{
    border: 2px solid {COLORS['accent_blue']};
}}

/* ===== WELCOME SCREEN ===== */
QLabel#welcome-title {{
    font-size: 42px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    letter-spacing: -1px;
}}

QLabel#welcome-subtitle {{
    font-size: 18px;
    color: {COLORS['text_secondary']};
    font-weight: 400;
}}

QLabel#hero-gradient {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #60a5fa, stop:0.5 #c084fc, stop:1 #f472b6);
    border-radius: 20px;
}}

/* ===== CATEGORY PILL ===== */
QFrame#category-pill {{
    background-color: {COLORS['surface']};
    border-radius: 20px;
    padding: 8px 16px;
}}

/* ===== BADGE ===== */
QLabel#badge {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_secondary']};
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#badge-primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #60a5fa, stop:1 #c084fc);
    color: white;
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}}
"""
