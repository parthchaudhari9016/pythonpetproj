"""
Modern UI components with animations, effects, and enhanced interactivity.
"""
import math
from typing import Optional, Callable, List
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QProgressBar, QPushButton,
    QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer,
    Property, Signal, Slot, QPoint, QSize
)
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QFont, QFontMetrics

from modern_styles import COLORS, CATEGORY_COLORS


class AnimatedProgressBar(QProgressBar):
    """Progress bar with smooth animated transitions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setMaximumHeight(6)
        self._target_value = 0
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(500)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def setValueAnimated(self, value: int):
        """Set value with smooth animation."""
        self._target_value = value
        self._animation.stop()
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        self._animation.start()


class GlowEffect(QGraphicsDropShadowEffect):
    """Custom glow effect for cards and buttons."""
    
    def __init__(self, color: str = "#60a5fa", radius: int = 20, parent=None):
        super().__init__(parent)
        self.setColor(QColor(color))
        self.setBlurRadius(radius)
        self.setOffset(0, 0)


class ModernStatCard(QFrame):
    """Modern stat card with gradient, glow effect, and animations."""
    
    clicked = Signal()
    
    def __init__(self, title: str, value: str = "0", icon: str = "📊", 
                 gradient: tuple = ("#60a5fa", "#c084fc"), parent=None):
        super().__init__(parent)
        self.setObjectName("stat-card")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(120)
        self.setMinimumWidth(180)
        
        self.title = title
        self.value = value
        self.icon = icon
        self.gradient_start, self.gradient_end = gradient
        
        # Setup glow effect (hidden by default)
        self._glow = GlowEffect(self.gradient_start, 0, self)
        self.setGraphicsEffect(self._glow)
        
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Top row: icon + value
        top_layout = QHBoxLayout()
        
        # Icon with gradient background
        self.icon_container = QFrame()
        self.icon_container.setFixedSize(44, 44)
        self.icon_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.gradient_start}, stop:1 {self.gradient_end});
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        self.icon_label = QLabel(self.icon)
        self.icon_label.setStyleSheet("font-size: 22px; background: transparent;")
        icon_layout.addWidget(self.icon_label)
        
        top_layout.addWidget(self.icon_container)
        top_layout.addStretch()
        
        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        top_layout.addWidget(self.value_label)
        
        layout.addLayout(top_layout)
        
        # Title
        self.title_label = QLabel(self.title.upper())
        self.title_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {COLORS['text_muted']};
            letter-spacing: 1.5px;
            background: transparent;
        """)
        layout.addWidget(self.title_label)
        
        # Progress bar (optional, shows relative size)
        self.progress = AnimatedProgressBar()
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['surface']};
                border: none;
                border-radius: 3px;
                height: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.gradient_start}, stop:1 {self.gradient_end});
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress)
    
    def _setup_animations(self):
        # Glow animation
        self._glow_animation = QPropertyAnimation(self._glow, b"blurRadius")
        self._glow_animation.setDuration(300)
        self._glow_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        self._glow_animation.stop()
        self._glow_animation.setStartValue(self._glow.blurRadius())
        self._glow_animation.setEndValue(25)
        self._glow_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._glow_animation.stop()
        self._glow_animation.setStartValue(self._glow.blurRadius())
        self._glow_animation.setEndValue(0)
        self._glow_animation.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
    
    def set_value(self, value: str, progress_pct: float = 0):
        """Update displayed value with animation."""
        self.value_label.setText(value)
        self.progress.setValueAnimated(int(progress_pct * 100))
    
    def set_progress(self, pct: float):
        """Update progress bar."""
        self.progress.setValueAnimated(int(pct * 100))


class CategoryPill(QFrame):
    """Modern pill-shaped category indicator."""
    
    def __init__(self, category: str, count: int = 0, size_str: str = "0 B", 
                 percentage: float = 0, parent=None):
        super().__init__(parent)
        self.category = category
        self.count = count
        self.size_str = size_str
        self.percentage = percentage
        
        colors = CATEGORY_COLORS.get(category, ("#94a3b8", "#64748b"))
        self.color_start, self.color_end = colors
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setObjectName("category-pill")
        self.setStyleSheet(f"""
            QFrame#category-pill {{
                background-color: {COLORS['surface']};
                border-radius: 14px;
                border: 1px solid {COLORS['border']};
            }}
            QFrame#category-pill:hover {{
                background-color: {COLORS['surface_hover']};
                border: 1px solid {self.color_start};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Color indicator
        indicator = QFrame()
        indicator.setFixedSize(12, 12)
        indicator.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {self.color_start}, stop:1 {self.color_end});
            border-radius: 6px;
        """)
        layout.addWidget(indicator)
        
        # Category name
        name = QLabel(self.category)
        name.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-weight: 600;
            font-size: 13px;
        """)
        layout.addWidget(name)
        
        layout.addStretch()
        
        # Stats
        stats = QLabel(f"{count:,} files · {self.size_str}")
        stats.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(stats)
        
        # Percentage badge
        if self.percentage > 0:
            badge = QLabel(f"{self.percentage:.1f}%")
            badge.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.color_start}, stop:1 {self.color_end});
                color: white;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            """)
            layout.addWidget(badge)


class QuickActionButton(QPushButton):
    """Modern quick action button with icon and hover effects."""
    
    def __init__(self, icon: str, text: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("quick-action")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(64)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
        
        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(2)
        
        title = QLabel(text)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-weight: 600;
            font-size: 14px;
            background: transparent;
        """)
        text_container.addWidget(title)
        
        if description:
            desc = QLabel(description)
            desc.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 12px;
                background: transparent;
            """)
            text_container.addWidget(desc)
        
        layout.addLayout(text_container)
        layout.addStretch()
        
        # Arrow indicator
        arrow = QLabel("›")
        arrow.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 20px;
            font-weight: 300;
            background: transparent;
        """)
        layout.addWidget(arrow)
        
        self.setStyleSheet(f"""
            QPushButton#quick-action {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
                text-align: left;
            }}
            QPushButton#quick-action:hover {{
                background-color: {COLORS['surface_hover']};
                border: 1px solid {COLORS['border_hover']};
            }}
        """)


class SearchBox(QFrame):
    """Modern search box with focus effects."""
    
    search_changed = Signal(str)
    
    def __init__(self, placeholder: str = "Search files and folders...", parent=None):
        super().__init__(parent)
        self.setObjectName("search-box")
        self.setMinimumHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"font-size: 16px; color: {COLORS['text_muted']};")
        layout.addWidget(search_icon)
        
        # Input field
        from PySide6.QtWidgets import QLineEdit
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
                font-size: 15px;
                padding: 0;
            }}
        """)
        self.input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.input, 1)
        
        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setObjectName("icon-btn")
        self.clear_btn.setFixedSize(28, 28)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['text_muted']};
                font-size: 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.clear_btn.clicked.connect(self.clear)
        self.clear_btn.hide()
        layout.addWidget(self.clear_btn)
        
        self.input.textChanged.connect(self._on_text_changed)
        
        self.setStyleSheet(f"""
            QFrame#search-box {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame#search-box:focus-within {{
                border: 2px solid {COLORS['accent_blue']};
            }}
        """)
    
    def _on_text_changed(self, text: str):
        self.clear_btn.setVisible(bool(text))
    
    def clear(self):
        self.input.clear()
        self.input.setFocus()
    
    def text(self) -> str:
        return self.input.text()
    
    def setFocus(self):
        self.input.setFocus()


class AnimatedCounter(QLabel):
    """Label that animates counting up to a value."""
    
    def __init__(self, parent=None, suffix: str = ""):
        super().__init__("0", parent)
        self.suffix = suffix
        self._target_value = 0
        self._current_value = 0
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(800)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
    
    def setValue(self, value: int):
        """Set value property for animation."""
        self._current_value = value
        self.setText(f"{value:,}{self.suffix}")
    
    def getValue(self) -> int:
        return self._current_value
    
    value = Property(int, getValue, setValue)
    
    def animate_to(self, target: int):
        """Animate to target value."""
        self._target_value = target
        self._animation.stop()
        self._animation.setStartValue(self._current_value)
        self._animation.setEndValue(target)
        self._animation.start()


class FileTypeBadge(QLabel):
    """Badge showing file type/extension."""
    
    def __init__(self, extension: str, parent=None):
        super().__init__(parent)
        
        # Determine color based on extension
        ext_lower = extension.lower()
        if ext_lower in ['.py', '.js', '.ts', '.java', '.cpp']:
            color = COLORS['accent_green']
        elif ext_lower in ['.jpg', '.png', '.gif', '.webp']:
            color = COLORS['accent_purple']
        elif ext_lower in ['.mp4', '.avi', '.mkv']:
            color = COLORS['accent_pink']
        elif ext_lower in ['.mp3', '.wav', '.flac']:
            color = COLORS['accent_cyan']
        elif ext_lower in ['.pdf', '.doc', '.docx', '.txt']:
            color = COLORS['accent_blue']
        elif ext_lower in ['.zip', '.rar', '.7z']:
            color = COLORS['accent_orange']
        else:
            color = COLORS['text_muted']
        
        self.setText(extension.upper().lstrip('.') if extension else 'N/A')
        self.setStyleSheet(f"""
            background-color: {color}20;
            color: {color};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 600;
        """)


class ModernTreeItem(QFrame):
    """Modern tree item with hover effects and file info."""
    
    clicked = Signal()
    
    def __init__(self, name: str, size: str, file_type: str, is_folder: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("tree-item")
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        # Icon
        icon = "📁" if is_folder else "📄"
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_label)
        
        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-weight: 500;
            font-size: 13px;
        """)
        layout.addWidget(name_label, 1)
        
        # Type badge
        if not is_folder:
            badge = FileTypeBadge(file_type)
            layout.addWidget(badge)
        
        # Size
        size_label = QLabel(size)
        size_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(size_label)
        
        self.setStyleSheet(f"""
            QFrame#tree-item {{
                background-color: transparent;
                border-radius: 10px;
            }}
            QFrame#tree-item:hover {{
                background-color: {COLORS['surface']};
            }}
        """)
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class FloatingActionButton(QPushButton):
    """Floating action button for primary actions."""
    
    def __init__(self, icon: str, parent=None):
        super().__init__(icon, parent)
        self.setObjectName("fab")
        self.setFixedSize(56, 56)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton#fab {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #60a5fa, stop:1 #c084fc);
                border: none;
                border-radius: 28px;
                color: white;
                font-size: 24px;
            }}
            QPushButton#fab:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #a855f7);
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(96, 165, 250, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class LoadingSpinner(QWidget):
    """Animated loading spinner."""
    
    def __init__(self, size: int = 40, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(16)  # ~60fps
        self._size = size
    
    def _rotate(self):
        self._angle = (self._angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw gradient arc
        gradient = QLinearGradient(0, 0, self._size, self._size)
        gradient.setColorAt(0, QColor(COLORS['accent_blue']))
        gradient.setColorAt(0.5, QColor(COLORS['accent_purple']))
        gradient.setColorAt(1, QColor(COLORS['accent_pink']))
        
        painter.setPen(Qt.NoPen)
        
        # Draw background circle
        painter.setBrush(QColor(COLORS['surface']))
        painter.drawEllipse(2, 2, self._size - 4, self._size - 4)
        
        # Draw spinning arc
        pen = painter.pen()
        pen.setWidth(3)
        pen.setColor(QColor(COLORS['accent_blue']))
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        painter.drawArc(6, 6, self._size - 12, self._size - 12,
                       self._angle * 16, 120 * 16)


class EmptyStateWidget(QFrame):
    """Widget shown when no data is available."""
    
    def __init__(self, icon: str, title: str, subtitle: str, action_text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("glass-card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        if action_text:
            layout.addSpacing(20)
            self.action_btn = QPushButton(action_text)
            self.action_btn.setObjectName("primary-btn")
            self.action_btn.setMinimumWidth(200)
            layout.addWidget(self.action_btn, alignment=Qt.AlignCenter)
