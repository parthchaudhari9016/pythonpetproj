"""
File preview system for quick content inspection.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, 
    QHBoxLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage

from modern_styles import COLORS


class PreviewType(Enum):
    """Types of file previews."""
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    DATA = "data"
    BINARY = "binary"
    UNKNOWN = "unknown"


@dataclass
class PreviewInfo:
    """Preview information."""
    preview_type: PreviewType
    content: str
    metadata: Dict
    can_preview: bool


class FilePreviewWidget(QFrame):
    """Widget for previewing file contents."""
    
    # Maximum file sizes for preview
    MAX_TEXT_SIZE = 1024 * 1024  # 1MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_LINES = 100
    
    # Syntax highlighting colors
    CODE_COLORS = {
        'keyword': '#c084fc',
        'string': '#4ade80',
        'comment': '#6c7086',
        'number': '#f472b6',
        'function': '#60a5fa',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glass-card")
        self.setMinimumHeight(300)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel("📄")
        self.icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(self.icon_label)
        
        self.name_label = QLabel("Select a file to preview")
        self.name_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        
        self.type_label = QLabel("")
        self.type_label.setStyleSheet(f"""
            background-color: {COLORS['surface']};
            color: {COLORS['text_secondary']};
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
        """)
        header_layout.addWidget(self.type_label)
        
        layout.addWidget(header)
        
        # Preview content
        self.preview_stack = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_stack)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Text preview
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
                font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
        """)
        self.text_preview.hide()
        self.preview_layout.addWidget(self.text_preview)
        
        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        self.image_preview.hide()
        self.preview_layout.addWidget(self.image_preview)
        
        # Binary/unknown preview
        self.binary_preview = QLabel("🔒 Binary file - preview not available")
        self.binary_preview.setAlignment(Qt.AlignCenter)
        self.binary_preview.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
        self.binary_preview.hide()
        self.preview_layout.addWidget(self.binary_preview)
        
        layout.addWidget(self.preview_stack, 1)
        
        # Metadata footer
        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.meta_label)
    
    def preview_file(self, file_path: str, file_size: int = 0, file_type: str = ""):
        """Generate preview for a file."""
        path = Path(file_path)
        
        if not path.exists():
            self._show_error("File not found")
            return
        
        # Update header
        self.name_label.setText(path.name)
        self.type_label.setText(file_type or path.suffix or "Unknown")
        
        # Determine preview type
        ext = path.suffix.lower()
        preview_type = self._get_preview_type(ext)
        
        # Hide all previews
        self.text_preview.hide()
        self.image_preview.hide()
        self.binary_preview.hide()
        
        if preview_type == PreviewType.IMAGE:
            self._preview_image(path, file_size)
        elif preview_type in (PreviewType.TEXT, PreviewType.CODE, PreviewType.DATA):
            self._preview_text(path, file_size, preview_type)
        else:
            self._preview_binary(path, file_size)
        
        # Update metadata
        self._update_metadata(path, file_size)
    
    def _get_preview_type(self, ext: str) -> PreviewType:
        """Determine preview type from extension."""
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
        code_exts = {'.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.h', 
                     '.json', '.xml', '.yaml', '.yml', '.sql', '.sh', '.bat', '.ps1',
                     '.md', '.txt', '.log', '.ini', '.cfg', '.conf'}
        data_exts = {'.csv', '.tsv'}
        
        if ext in image_exts:
            return PreviewType.IMAGE
        elif ext in code_exts:
            return PreviewType.CODE
        elif ext in data_exts:
            return PreviewType.DATA
        elif ext in {'.exe', '.dll', '.bin', '.dat'}:
            return PreviewType.BINARY
        else:
            return PreviewType.UNKNOWN
    
    def _preview_image(self, path: Path, file_size: int):
        """Preview image file."""
        if file_size > self.MAX_IMAGE_SIZE:
            self.binary_preview.setText("📷 Image too large for preview")
            self.binary_preview.show()
            return
        
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.binary_preview.setText("⚠️ Failed to load image")
            self.binary_preview.show()
            return
        
        # Scale to fit while maintaining aspect ratio
        scaled = pixmap.scaled(
            600, 400,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_preview.setPixmap(scaled)
        self.image_preview.show()
    
    def _preview_text(self, path: Path, file_size: int, preview_type: PreviewType):
        """Preview text file."""
        if file_size > self.MAX_TEXT_SIZE:
            self.text_preview.setPlainText(
                f"⚠️ File too large for preview ({file_size / 1024 / 1024:.1f} MB)\n"
                "Maximum preview size: 1 MB"
            )
            self.text_preview.show()
            return
        
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Limit lines
            lines = content.split('\n')
            if len(lines) > self.MAX_LINES:
                content = '\n'.join(lines[:self.MAX_LINES])
                content += f"\n\n... ({len(lines) - self.MAX_LINES} more lines)"
            
            # Apply syntax highlighting for code
            if preview_type == PreviewType.CODE:
                content = self._highlight_code(content, path.suffix)
                self.text_preview.setHtml(content)
            else:
                self.text_preview.setPlainText(content)
            
            self.text_preview.show()
            
        except Exception as e:
            self.text_preview.setPlainText(f"⚠️ Error reading file:\n{str(e)}")
            self.text_preview.show()
    
    def _highlight_code(self, content: str, ext: str) -> str:
        """Simple syntax highlighting for code."""
        import html
        
        # Escape HTML
        content = html.escape(content)
        
        # Simple keyword highlighting (basic implementation)
        keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'for', 
                   'while', 'try', 'except', 'finally', 'with', 'as', 'pass', 'break',
                   'continue', 'lambda', 'yield', 'async', 'await', 'function', 'var',
                   'let', 'const', 'async', 'await', 'export', 'default']
        
        for kw in keywords:
            content = content.replace(
                f' {kw} ', 
                f' <span style="color:{self.CODE_COLORS["keyword"]}">{kw}</span> '
            )
        
        # String highlighting (simple)
        import re
        content = re.sub(
            r'(".*?"|\'.*?\')',
            rf'<span style="color:{self.CODE_COLORS["string"]}">\1</span>',
            content
        )
        
        # Comments
        content = re.sub(
            r'(#.*$|//.*$)',
            rf'<span style="color:{self.CODE_COLORS["comment"]}">\1</span>',
            content,
            flags=re.MULTILINE
        )
        
        return f"<pre>{content}</pre>"
    
    def _preview_binary(self, path: Path, file_size: int):
        """Show binary file info."""
        self.binary_preview.setText(
            f"🔒 Binary file\n\n"
            f"Preview not available for this file type.\n"
            f"Use external applications to view this file."
        )
        self.binary_preview.show()
    
    def _update_metadata(self, path: Path, file_size: int):
        """Update metadata display."""
        import time
        
        try:
            stat = path.stat()
            modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
            
            size_str = self._format_size(stat.st_size)
            
            self.meta_label.setText(
                f"📍 {path}  ·  📦 {size_str}  ·  🕐 Modified: {modified}"
            )
        except:
            self.meta_label.setText(str(path))
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    def _show_error(self, message: str):
        """Show error message."""
        self.text_preview.setPlainText(f"⚠️ {message}")
        self.text_preview.show()
        self.image_preview.hide()
        self.binary_preview.hide()
    
    def clear(self):
        """Clear the preview."""
        self.name_label.setText("Select a file to preview")
        self.type_label.setText("")
        self.text_preview.clear()
        self.text_preview.hide()
        self.image_preview.clear()
        self.image_preview.hide()
        self.binary_preview.hide()
        self.meta_label.setText("")
