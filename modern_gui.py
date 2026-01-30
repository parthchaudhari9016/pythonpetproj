"""
Modern File Analyzer GUI with AI-like interface.
Inspired by OpenCode, Perplexity, and Claude.
"""
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStackedWidget, QLabel, QPushButton, QFileDialog,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QTabWidget,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, Signal, Slot, QSettings, QTimer, QThread, QSize
)
from PySide6.QtGui import QFont, QIcon, QAction

# Import our modules
from models import FolderInfo, ScanResult, FileCategory, format_size
from scanner import ScannerThread
from analyzer import FolderAnalyzer, InsightGenerator, DuplicateDetector, MarkdownReporter
from modern_styles import MODERN_STYLESHEET, COLORS, CATEGORY_COLORS
from modern_components import (
    ModernStatCard, CategoryPill, QuickActionButton, SearchBox,
    AnimatedCounter, EmptyStateWidget, LoadingSpinner, 
    FloatingActionButton, AnimatedProgressBar, QuickActionButton
)
from search_engine import FileSearchEngine, SearchResult
from file_preview import FilePreviewWidget
try:
    from interactive_charts import (
        InteractivePieChart, InteractiveBarChart, InteractiveTreemap,
        InteractiveExtensionChart, ChartContainer
    )
    HAS_WEBENGINE = True
except ImportError:
    print("⚠️  Modern interactive charts not available (WebEngine missing). Falling back to Matplotlib.")
    from visualizer import (
        CategoryPieChart as InteractivePieChart,
        FolderBarChart as InteractiveBarChart,
        ExtensionChart as InteractiveExtensionChart,
        FileTypeTreemap as InteractiveTreemap
    )
    HAS_WEBENGINE = False

    class ChartContainer(QWidget):
        """Fallback container for matplotlib charts."""
        def __init__(self, title: str, chart: QWidget, parent=None):
            super().__init__(parent)
            self.setObjectName("glass-card")
            
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # Header
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {COLORS['text_primary']};")
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            layout.addWidget(header)
            
            # Chart
            self.chart = chart
            layout.addWidget(chart, 1)
            
            self.setStyleSheet(f"""
                QWidget#glass-card {{
                    background-color: rgba(37, 37, 54, 0.6);
                    border: 1px solid rgba(137, 180, 250, 0.15);
                    border-radius: 20px;
                }}
            """)


class RecentFoldersManager:
    """Manages recently scanned folders."""
    
    MAX_RECENT = 10
    
    def __init__(self):
        self.settings = QSettings("FileAnalyzer", "RecentFolders")
    
    def get_recent(self) -> List[Dict]:
        """Get list of recently scanned folders."""
        data = self.settings.value("recent", "[]")
        try:
            return json.loads(data)
        except:
            return []
    
    def add_recent(self, path: str, name: str, size_str: str, file_count: int):
        """Add a folder to recent list."""
        recent = self.get_recent()
        
        # Remove if already exists
        recent = [r for r in recent if r.get('path') != path]
        
        # Add to front
        recent.insert(0, {
            'path': path,
            'name': name,
            'size': size_str,
            'files': file_count,
            'date': datetime.now().isoformat()
        })
        
        # Keep only max
        recent = recent[:self.MAX_RECENT]
        
        self.settings.setValue("recent", json.dumps(recent))
    
    def clear_recent(self):
        """Clear recent folders."""
        self.settings.setValue("recent", "[]")


class WelcomeScreen(QWidget):
    """Modern welcome screen with quick actions."""
    
    browse_clicked = Signal()
    recent_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_manager = RecentFoldersManager()
        self._setup_ui()
        self._load_recent()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)
        
        # Hero section
        hero = QFrame()
        hero.setObjectName("glass-card")
        hero.setStyleSheet(f"""
            QFrame#glass-card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(96, 165, 250, 0.15),
                    stop:0.5 rgba(192, 132, 252, 0.15),
                    stop:1 rgba(244, 114, 182, 0.15));
                border: 1px solid rgba(137, 180, 250, 0.2);
                border-radius: 24px;
                padding: 40px;
            }}
        """)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Icon
        icon = QLabel("🔍")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignCenter)
        hero_layout.addWidget(icon)
        
        # Title with gradient effect
        title = QLabel("File Analyzer")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 700;
            color: {COLORS['text_primary']};
            letter-spacing: -1px;
        """)
        title.setAlignment(Qt.AlignCenter)
        hero_layout.addWidget(title)
        
        subtitle = QLabel("Visual Storage Explorer with AI-Powered Insights")
        subtitle.setStyleSheet(f"""
            font-size: 18px;
            color: {COLORS['text_secondary']};
            margin-top: 8px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        hero_layout.addWidget(subtitle)
        
        # Primary action
        self.browse_btn = QPushButton("📁  Browse Folder")
        self.browse_btn.setObjectName("primary-btn")
        self.browse_btn.setMinimumWidth(240)
        self.browse_btn.setMinimumHeight(52)
        self.browse_btn.clicked.connect(self.browse_clicked.emit)
        hero_layout.addSpacing(30)
        hero_layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(hero)
        
        # Quick stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        stats = [
            ("🚀", "Fast Scanning", "Multi-threaded analysis"),
            ("📊", "Visual Analytics", "Interactive charts"),
            ("🔍", "Smart Search", "Find files instantly"),
        ]
        
        for icon, title_text, desc in stats:
            card = self._create_feature_card(icon, title_text, desc)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Recent folders section
        recent_section = QFrame()
        recent_section.setObjectName("glass-card")
        recent_layout = QVBoxLayout(recent_section)
        recent_layout.setContentsMargins(24, 24, 24, 24)
        
        recent_header = QLabel("📂 Recent Folders")
        recent_header.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        recent_layout.addWidget(recent_header)
        
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
                margin: 6px 0;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['surface_hover']};
                border: 1px solid {COLORS['border_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['surface_active']};
                border: 1px solid {COLORS['accent_blue']};
            }}
        """)
        self.recent_list.itemClicked.connect(self._on_recent_clicked)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_section)
        layout.addStretch()
    
    def _create_feature_card(self, icon: str, title: str, desc: str) -> QFrame:
        card = QFrame()
        card.setObjectName("glass-card")
        card.setStyleSheet(f"""
            QFrame#glass-card {{
                background-color: rgba(37, 37, 54, 0.5);
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        return card
    
    def _load_recent(self):
        self.recent_list.clear()
        recent = self.recent_manager.get_recent()
        
        for item in recent:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            info = QVBoxLayout()
            name = QLabel(item['name'])
            name.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
            info.addWidget(name)
            
            meta = QLabel(f"{item['size']} · {item['files']:,} files")
            meta.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            info.addWidget(meta)
            
            layout.addLayout(info)
            layout.addStretch()
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.sizeHint() + QSize(0, 20))
            list_item.setData(Qt.UserRole, item['path'])
            self.recent_list.addItem(list_item)
            self.recent_list.setItemWidget(list_item, widget)
    
    def _on_recent_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        self.recent_selected.emit(path)
    
    def refresh_recent(self):
        self._load_recent()


class DashboardWidget(QWidget):
    """Main dashboard showing scan results."""
    
    folder_selected = Signal(object)  # FolderInfo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_result: Optional[ScanResult] = None
        self.search_engine = FileSearchEngine()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        
        # Header with search
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("📊 Dashboard")
        self.title_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.search_box = SearchBox("Search files and folders...")
        self.search_box.setMaximumWidth(400)
        self.search_box.search_changed.connect(self._on_search)
        header_layout.addWidget(self.search_box)
        
        # Search results button (hidden by default)
        self.search_results_btn = QPushButton("🔍")
        self.search_results_btn.setObjectName("icon-btn")
        self.search_results_btn.setFixedSize(40, 40)
        self.search_results_btn.hide()
        self.search_results_btn.clicked.connect(self._show_search_results)
        header_layout.addWidget(self.search_results_btn)
        
        layout.addWidget(header)
        
        # Stats cards row
        self.stats_container = QWidget()
        stats_layout = QHBoxLayout(self.stats_container)
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stat_cards = {
            'files': ModernStatCard("Total Files", "0", "📄", ("#60a5fa", "#3b82f6")),
            'folders': ModernStatCard("Folders", "0", "📁", ("#c084fc", "#a855f7")),
            'size': ModernStatCard("Total Size", "0 B", "💾", ("#22d3ee", "#06b6d4")),
            'time': ModernStatCard("Scan Time", "0s", "⏱️", ("#4ade80", "#22c55e")),
        }
        
        for card in self.stat_cards.values():
            stats_layout.addWidget(card)
        
        layout.addWidget(self.stats_container)
        
        # Main content splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left: Folder tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        tree_header = QLabel("🌲 Folder Structure")
        tree_header.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        left_layout.addWidget(tree_header)
        
        from modern_tree import ModernFolderTreeWidget
        self.tree = ModernFolderTreeWidget()
        self.tree.folder_selected.connect(self.folder_selected.emit)
        self.tree.file_selected.connect(self._on_file_selected)
        left_layout.addWidget(self.tree, 1)
        
        # File preview panel (initially hidden)
        self.preview_widget = FilePreviewWidget()
        self.preview_widget.setMaximumHeight(300)
        left_layout.addWidget(self.preview_widget)
        
        self.splitter.addWidget(left_panel)
        
        # Right: Charts and analytics
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setStyleSheet("background: transparent; border: none;")
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(24)
        
        # Charts tabs
        self.charts_tabs = QTabWidget()
        self.charts_tabs.setDocumentMode(True)
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_layout.setSpacing(20)
        
        # Category distribution pie chart
        self.pie_chart = InteractivePieChart()
        pie_container = ChartContainer("Storage Distribution", self.pie_chart)
        overview_layout.addWidget(pie_container)
        
        # Top folders bar chart
        self.bar_chart = InteractiveBarChart()
        bar_container = ChartContainer("Top Folders by Size", self.bar_chart)
        overview_layout.addWidget(bar_container)
        
        overview_layout.addStretch()
        self.charts_tabs.addTab(overview_tab, "📊 Overview")
        
        # Categories tab
        categories_tab = QWidget()
        categories_layout = QVBoxLayout(categories_tab)
        
        # Treemap
        self.treemap = InteractiveTreemap()
        treemap_container = ChartContainer("Category Treemap", self.treemap)
        categories_layout.addWidget(treemap_container)
        
        # Category pills
        self.category_pills = QWidget()
        self.pills_layout = QGridLayout(self.category_pills)
        self.pills_layout.setSpacing(12)
        categories_layout.addWidget(self.category_pills)
        
        categories_layout.addStretch()
        self.charts_tabs.addTab(categories_tab, "🏷️ Categories")
        
        # Extensions tab
        extensions_tab = QWidget()
        extensions_layout = QVBoxLayout(extensions_tab)
        
        self.ext_chart = InteractiveExtensionChart()
        ext_container = ChartContainer("File Extensions", self.ext_chart)
        extensions_layout.addWidget(ext_container)
        
        extensions_layout.addStretch()
        self.charts_tabs.addTab(extensions_tab, "📎 Extensions")
        
        right_layout.addWidget(self.charts_tabs)
        
        # Tools tab
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        tools_layout.setSpacing(20)
        
        tools_grid = QGridLayout()
        tools_grid.setSpacing(20)
        
        # Duplicate Finder Button
        self.dup_btn = QuickActionButton("🔍 Find Duplicates", "Locate files with identical content", "primary")
        self.dup_btn.clicked.connect(self._on_find_duplicates)
        tools_grid.addWidget(self.dup_btn, 0, 0)
        
        # Export Report Button
        self.export_btn = QuickActionButton("📊 Export Report", "Generate a detailed Markdown report", "secondary")
        self.export_btn.clicked.connect(self._on_export_report)
        tools_grid.addWidget(self.export_btn, 0, 1)
        
        tools_layout.addLayout(tools_grid)
        
        # Tool results area
        self.tool_results_frame = QFrame()
        self.tool_results_frame.setObjectName("glass-card")
        self.tool_results_layout = QVBoxLayout(self.tool_results_frame)
        
        self.tool_results_label = QLabel("Run a tool to see results...")
        self.tool_results_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.tool_results_label.setWordWrap(True)
        self.tool_results_layout.addWidget(self.tool_results_label)
        
        tools_layout.addWidget(self.tool_results_frame, 1)
        
        self.charts_tabs.addTab(tools_tab, "🛠️ Tools")
        
        # Insights section
        insights_frame = QFrame()
        insights_frame.setObjectName("glass-card")
        insights_layout = QVBoxLayout(insights_frame)
        
        insights_title = QLabel("💡 Insights")
        insights_title.setStyleSheet(f"font-size: 16px; font-weight: 600;")
        insights_layout.addWidget(insights_title)
        
        self.insights_text = QLabel("Select a folder to see insights...")
        self.insights_text.setWordWrap(True)
        self.insights_text.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.6;")
        insights_layout.addWidget(self.insights_text)
        
        right_layout.addWidget(insights_frame)
        
        right_scroll.setWidget(right_widget)
        self.splitter.addWidget(right_scroll)
        self.splitter.setSizes([350, 800])
        
        layout.addWidget(self.splitter, 1)
    
    def update_with_result(self, result: ScanResult):
        """Update dashboard with scan result."""
        self.current_result = result
        
        # Update title
        self.title_label.setText(f"📊 {result.root_folder.name}")
        
        # Update stat cards with animation
        self.stat_cards['files'].set_value(f"{result.total_files:,}")
        self.stat_cards['folders'].set_value(f"{result.total_folders:,}")
        self.stat_cards['size'].set_value(result.size_formatted)
        self.stat_cards['time'].set_value(f"{result.scan_time:.2f}s")
        
        # Update tree
        self.tree.populate(result.root_folder)
        
        # Build search index
        self.search_engine.build_index(result.root_folder)
        
        # Update charts
        analyzer = FolderAnalyzer(result)
        
        percentages = analyzer.get_category_percentages()
        self.pie_chart.update_data(percentages)
        self.treemap.update_data(percentages)
        
        folder_comparison = analyzer.get_folder_comparison()
        self.bar_chart.update_data(folder_comparison)
        
        ext_dist = analyzer.get_extension_distribution()
        self.ext_chart.update_data(ext_dist)
        
        # Update category pills
        self._update_category_pills(analyzer)
        
        # Update insights
        insight_gen = InsightGenerator(analyzer)
        self.insights_text.setText(insight_gen.generate_folder_insight())
    
    def _update_category_pills(self, analyzer: FolderAnalyzer):
        """Update category pills."""
        # Clear existing
        while self.pills_layout.count():
            item = self.pills_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add pills
        row, col = 0, 0
        for category in FileCategory:
            summary = analyzer.get_category_summary(category)
            if summary['file_count'] > 0:
                pill = CategoryPill(
                    category.value,
                    summary['file_count'],
                    summary['total_size'],
                    summary['percentage']
                )
                self.pills_layout.addWidget(pill, row, col)
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
    
    def _on_search(self, query: str):
        """Handle search input."""
        if len(query) >= 2:
            results = self.search_engine.search(query)
            if results:
                self.search_results_btn.setText(f"🔍 {len(results)}")
                self.search_results_btn.show()
                self.search_results = results
            else:
                self.search_results_btn.hide()
        else:
            self.search_results_btn.hide()
    
    def _show_search_results(self):
        """Show search results in a dialog or panel."""
        if not hasattr(self, 'search_results') or not self.search_results:
            return
        
        # Create results dialog
        from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Search Results ({len(self.search_results)} found)")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
            QListWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        
        header = QLabel(f"🔍 Found {len(self.search_results)} results")
        header.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        results_list = QListWidget()
        for result in self.search_results[:50]:  # Show first 50
            icon = "📁" if result.is_folder else "📄"
            item_text = f"{icon} {result.name}\n   📍 {result.path}\n   📦 {result.size}"
            item = QListWidgetItem(item_text)
            results_list.addItem(item)
        
        layout.addWidget(results_list)
        
        dialog.exec()
    
    def _on_file_selected(self, file_info):
        """Handle file selection for preview."""
        self.preview_widget.preview_file(
            str(file_info.path),
            file_info.size,
            file_info.category.value
        )

    def _on_find_duplicates(self):
        """Handle duplicate finder tool."""
        if not self.current_result:
            return
            
        detector = DuplicateDetector(self.current_result.root_folder)
        duplicates = detector.find_duplicates()
        
        if not duplicates:
            self.tool_results_label.setText("✅ No duplicate files found.")
            return
            
        # Format results
        res_text = f"## 🔍 Found {len(duplicates)} duplicate groups\n\n"
        total_wasted = 0
        
        for i, group in enumerate(duplicates[:10]):  # Show top 10
            group_size = group[0].size
            wasted = group_size * (len(group) - 1)
            total_wasted += wasted
            
            res_text += f"**{i+1}. {group[0].name}** ({group[0].size_formatted})\n"
            for file in group:
                res_text += f"  • `{file.path}`\n"
            res_text += "\n"
            
        if len(duplicates) > 10:
            res_text += f"... and {len(duplicates) - 10} more groups.\n\n"
            
        res_text += f"### 💾 Potential Space Savings: {format_size(total_wasted)}"
        self.tool_results_label.setText(res_text)

    def _on_export_report(self):
        """Handle report export."""
        if not self.current_result:
            return
            
        analyzer = FolderAnalyzer(self.current_result)
        reporter = MarkdownReporter(analyzer)
        report_md = reporter.generate_report()
        
        # Save dialog
        default_name = f"Report_{self.current_result.root_folder.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Analysis Report", default_name, "Markdown Files (*.md)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_md)
                QMessageBox.information(self, "Success", f"Report exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export report:\n{str(e)}")


class LoadingScreen(QWidget):
    """Loading screen with progress and stats."""
    
    cancel_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Spinner
        self.spinner = LoadingSpinner(60)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Status
        self.status_label = QLabel("Scanning...")
        self.status_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Stats
        self.stats_label = QLabel("Files found: 0")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        
        # Progress bar
        self.progress = AnimatedProgressBar()
        self.progress.setMaximumWidth(400)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        
        # Current file
        self.file_label = QLabel("")
        self.file_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        self.file_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.file_label)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary-btn")
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        layout.addWidget(self.cancel_btn, alignment=Qt.AlignCenter)
    
    def update_progress(self, current_path: str, files_scanned: int):
        """Update progress display."""
        self.stats_label.setText(f"Files found: {files_scanned:,}")
        self.file_label.setText(current_path[-60:] if len(current_path) > 60 else current_path)


class ModernMainWindow(QMainWindow):
    """Main window with modern AI-like interface."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Analyzer")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Set icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # State
        self.current_result: Optional[ScanResult] = None
        self.scanner_thread: Optional[ScannerThread] = None
        self.recent_manager = RecentFoldersManager()
        
        self._setup_ui()
        self._setup_menu()
    
    def _setup_ui(self):
        """Setup main UI."""
        # Central widget with stacked layout
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        
        # Welcome screen
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.browse_clicked.connect(self._on_browse)
        self.welcome_screen.recent_selected.connect(self._start_scan)
        self.central.addWidget(self.welcome_screen)
        
        # Loading screen
        self.loading_screen = LoadingScreen()
        self.loading_screen.cancel_clicked.connect(self._cancel_scan)
        self.central.addWidget(self.loading_screen)
        
        # Dashboard
        self.dashboard = DashboardWidget()
        self.dashboard.folder_selected.connect(self._on_folder_selected)
        self.central.addWidget(self.dashboard)
        
        # Show welcome screen
        self.central.setCurrentIndex(0)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet(f"color: {COLORS['text_muted']};")
    
    def _setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['surface']};
            }}
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_browse)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._on_refresh)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        back_action = QAction("Back to Welcome", self)
        back_action.triggered.connect(self._show_welcome)
        view_menu.addAction(back_action)
    
    def _on_browse(self):
        """Handle browse button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Analyze",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self._start_scan(folder)
    
    def _start_scan(self, folder_path: str):
        """Start scanning a folder."""
        # Cancel any existing scan
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.cancel()
            self.scanner_thread.wait()
        
        # Show loading screen
        self.central.setCurrentIndex(1)
        self.statusBar().showMessage(f"Scanning: {folder_path}")
        
        # Start scanner
        self.scanner_thread = ScannerThread(folder_path)
        self.scanner_thread.progress.connect(self._on_scan_progress)
        self.scanner_thread.scan_complete.connect(self._on_scan_complete)
        self.scanner_thread.error.connect(self._on_scan_error)
        self.scanner_thread.start()
    
    def _on_scan_progress(self, current_path: str, files_scanned: int):
        """Update progress during scan."""
        self.loading_screen.update_progress(current_path, files_scanned)
    
    def _on_scan_complete(self, result: ScanResult):
        """Handle scan completion."""
        self.current_result = result
        
        # Add to recent
        self.recent_manager.add_recent(
            str(result.root_folder.path),
            result.root_folder.name,
            result.size_formatted,
            result.total_files
        )
        
        # Update dashboard
        self.dashboard.update_with_result(result)
        
        # Show dashboard
        self.central.setCurrentIndex(2)
        
        # Update status
        self.statusBar().showMessage(
            f"✓ Scan complete: {result.total_files:,} files, {result.size_formatted}"
        )
    
    def _on_scan_error(self, error_msg: str):
        """Handle scan error."""
        self._show_welcome()
        QMessageBox.critical(self, "Scan Error", f"Failed to scan folder:\n{error_msg}")
        self.statusBar().showMessage(f"Error: {error_msg}")
    
    def _cancel_scan(self):
        """Cancel current scan."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.cancel()
            self.scanner_thread.wait()
        
        self._show_welcome()
        self.statusBar().showMessage("Scan cancelled")
    
    def _show_welcome(self):
        """Show welcome screen."""
        self.welcome_screen.refresh_recent()
        self.central.setCurrentIndex(0)
    
    def _on_refresh(self):
        """Refresh current scan."""
        if self.current_result:
            self._start_scan(str(self.current_result.root_folder.path))
        else:
            self._on_browse()
    
    def _on_folder_selected(self, folder: FolderInfo):
        """Handle folder selection in tree."""
        if self.current_result:
            self.dashboard.update_with_result(
                ScanResult(
                    root_folder=folder,
                    total_files=folder.file_count,
                    total_folders=folder.folder_count,
                    total_size=folder.total_size,
                    categories=folder.categories,
                    largest_files=[],
                    scan_time=0
                )
            )
    
    def closeEvent(self, event):
        """Handle window close."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.cancel()
            self.scanner_thread.wait()
        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(MODERN_STYLESHEET)
    
    # Set font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
