"""
Modern tree widget with file preview support.
"""
from typing import Dict, Optional
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from models import FolderInfo, FileInfo, FileCategory


class ModernFolderTreeWidget(QTreeWidget):
    """Enhanced tree widget with file support and modern styling."""
    
    folder_selected = Signal(object)  # Emits FolderInfo
    file_selected = Signal(object)    # Emits FileInfo
    
    CATEGORY_COLORS = {
        FileCategory.DOCUMENTS: "#60a5fa",
        FileCategory.MEDIA_IMAGES: "#c084fc",
        FileCategory.MEDIA_AUDIO: "#22d3ee",
        FileCategory.MEDIA_VIDEO: "#f472b6",
        FileCategory.CODE: "#4ade80",
        FileCategory.ARCHIVES: "#fb923c",
        FileCategory.DATA: "#facc15",
        FileCategory.EXECUTABLES: "#f87171",
        FileCategory.OTHERS: "#94a3b8",
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(['📁 Name', '📦 Size', '📄 Files', '🏷️ Type'])
        self.setAnimated(True)
        self.setIndentation(20)
        self.setAlternatingRowColors(False)
        self.setRootIsDecorated(True)
        
        # Modern styling
        self.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px 10px;
                border-radius: 8px;
                margin: 2px 4px;
                color: #a6adc8;
            }
            QTreeWidget::item:hover {
                background-color: rgba(49, 50, 68, 0.5);
                color: #cdd6f4;
            }
            QTreeWidget::item:selected {
                background-color: rgba(137, 180, 250, 0.2);
                color: #89b4fa;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: transparent;
                color: #6c7086;
                padding: 10px 8px;
                border: none;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
            }
        """)
        
        # Column sizing
        header = self.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Storage
        self._folder_map: Dict[int, FolderInfo] = {}
        self._file_map: Dict[int, FileInfo] = {}
        
        # Signals
        self.itemClicked.connect(self._on_item_clicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def populate(self, root_folder: FolderInfo):
        """Populate tree with folder data."""
        self.clear()
        self._folder_map.clear()
        self._file_map.clear()
        
        # Add root
        root_item = self._create_folder_item(root_folder, is_root=True)
        self.addTopLevelItem(root_item)
        root_item.setExpanded(True)
        
        # Add children
        self._add_children(root_item, root_folder)
    
    def _create_folder_item(self, folder: FolderInfo, is_root: bool = False) -> QTreeWidgetItem:
        """Create tree item for a folder."""
        # Choose icon based on content
        if is_root:
            icon = "🏠"
        elif folder.folder_count > 5:
            icon = "📚"
        elif folder.dominant_category:
            icon_map = {
                FileCategory.MEDIA_IMAGES: "🖼️",
                FileCategory.MEDIA_VIDEO: "🎬",
                FileCategory.MEDIA_AUDIO: "🎵",
                FileCategory.CODE: "💻",
                FileCategory.DOCUMENTS: "📄",
                FileCategory.ARCHIVES: "📦",
                FileCategory.DATA: "📊",
            }
            icon = icon_map.get(folder.dominant_category, "📁")
        else:
            icon = "📁"
        
        item = QTreeWidgetItem([
            f"{icon} {folder.name}",
            folder.size_formatted,
            f"{folder.file_count:,}",
            folder.dominant_category.value if folder.dominant_category else "-"
        ])
        
        # Color code by category
        if folder.dominant_category and folder.dominant_category in self.CATEGORY_COLORS:
            color = QColor(self.CATEGORY_COLORS[folder.dominant_category])
            item.setForeground(3, QBrush(color))
        
        # Store reference
        item_id = id(item)
        self._folder_map[item_id] = folder
        item.setData(0, Qt.UserRole, ("folder", item_id))
        
        # Tooltip
        tooltip = f"Path: {folder.path}\nFiles: {folder.file_count:,}\nFolders: {folder.folder_count:,}\nSize: {folder.size_formatted}"
        item.setToolTip(0, tooltip)
        
        return item
    
    def _create_file_item(self, file: FileInfo) -> QTreeWidgetItem:
        """Create tree item for a file."""
        # Icon based on category
        icon_map = {
            FileCategory.DOCUMENTS: "📄",
            FileCategory.MEDIA_IMAGES: "🖼️",
            FileCategory.MEDIA_VIDEO: "🎬",
            FileCategory.MEDIA_AUDIO: "🎵",
            FileCategory.CODE: "💻",
            FileCategory.ARCHIVES: "📦",
            FileCategory.DATA: "📊",
            FileCategory.EXECUTABLES: "⚙️",
            FileCategory.OTHERS: "📎",
        }
        icon = icon_map.get(file.category, "📄")
        
        item = QTreeWidgetItem([
            f"{icon} {file.name}",
            file.size_formatted,
            "",
            file.extension.upper().lstrip('.') if file.extension else "N/A"
        ])
        
        # Color code
        if file.category in self.CATEGORY_COLORS:
            color = QColor(self.CATEGORY_COLORS[file.category])
            item.setForeground(3, QBrush(color))
        
        # Make file items italic and slightly smaller appearance
        font = item.font(0)
        font.setItalic(True)
        item.setFont(0, font)
        
        # Store reference
        item_id = id(item)
        self._file_map[item_id] = file
        item.setData(0, Qt.UserRole, ("file", item_id))
        
        # Tooltip with file info
        tooltip = f"Path: {file.path}\nSize: {file.size_formatted}\nType: {file.category.value}"
        item.setToolTip(0, tooltip)
        
        return item
    
    def _add_children(self, parent_item: QTreeWidgetItem, parent_folder: FolderInfo):
        """Recursively add child folders and files."""
        # Sort folders by size
        sorted_folders = sorted(parent_folder.children, key=lambda f: f.total_size, reverse=True)
        
        for child_folder in sorted_folders:
            child_item = self._create_folder_item(child_folder)
            parent_item.addChild(child_item)
            
            # Recursively add grandchildren
            if child_folder.children:
                self._add_children(child_item, child_folder)
            
            # Add files (limit to top 20 for performance)
            if child_folder.files:
                sorted_files = sorted(child_folder.files, key=lambda f: f.size, reverse=True)[:20]
                for file in sorted_files:
                    file_item = self._create_file_item(file)
                    child_item.addChild(file_item)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        item_type, item_id = data
        
        if item_type == "folder" and item_id in self._folder_map:
            self.folder_selected.emit(self._folder_map[item_id])
        elif item_type == "file" and item_id in self._file_map:
            self.file_selected.emit(self._file_map[item_id])

    def _show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.itemAt(position)
        if not item:
            return
            
        data = item.data(0, Qt.UserRole)
        if not data:
            return
            
        item_type, item_id = data
        path = None
        
        if item_type == "folder" and item_id in self._folder_map:
            path = self._folder_map[item_id].path
        elif item_type == "file" and item_id in self._file_map:
            path = self._file_map[item_id].path
            
        if not path:
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
            }
        """)
        
        open_action = menu.addAction("📂 Open in Explorer")
        copy_action = menu.addAction("📋 Copy Path")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action == open_action:
            import os
            import subprocess
            if os.name == 'nt':
                subprocess.run(['explorer', '/select,', str(path)])
            else:
                import platform
                if platform.system() == 'Darwin':
                    subprocess.run(['open', '-R', str(path)])
                else:
                    subprocess.run(['xdg-open', str(path.parent)])
        elif action == copy_action:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(str(path))
