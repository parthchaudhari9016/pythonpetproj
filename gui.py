"""
Main GUI components for the File Analyzer application.
Enhanced with proper tree visualization and sectioned layout.
"""
import sys
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QFileDialog,
    QScrollArea, QFrame, QGridLayout, QTextEdit, QProgressBar,
    QStatusBar, QGroupBox, QSizePolicy, QTabWidget, QHeaderView,
    QStackedWidget
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QColor, QBrush, QIcon

from models import FolderInfo, ScanResult, FileCategory, format_size, CATEGORY_DESCRIPTIONS
from scanner import ScannerThread
from analyzer import FolderAnalyzer, InsightGenerator
from visualizer import (
    CategoryPieChart, FolderBarChart, TopFilesChart, ExtensionChart,
    SizeDistributionChart, FileTypeTreemap
)
from styles import DARK_STYLESHEET, COLORS


class StatCard(QFrame):
    """A card widget displaying a statistic with enhanced visual effects."""
    
    def __init__(self, title: str, value: str = "0", icon: str = "📊", parent=None):
        super().__init__(parent)
        self.setObjectName("stat-card")
        self.setMinimumHeight(100)
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)
        
        # Icon + Value row
        top_layout = QHBoxLayout()
        
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        top_layout.addWidget(self.icon_label)
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat-value")
        self.value_label.setAlignment(Qt.AlignRight)
        self.value_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #89b4fa;")
        top_layout.addWidget(self.value_label, 1)
        
        layout.addLayout(top_layout)
        
        # Title label with improved styling
        self.title_label = QLabel(title)
        self.title_label.setObjectName("stat-label")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 11px; color: #a6adc8; text-transform: uppercase; letter-spacing: 0.5px;")
        
        layout.addWidget(self.title_label)
        
        # Add hover effect
        self.setStyleSheet("""
            QFrame#stat-card {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 12px;
                padding: 10px;
                transition: all 0.3s ease;
            }
            QFrame#stat-card:hover {
                background-color: #45475a;
                border: 1px solid #89b4fa;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(137, 180, 250, 0.15);
            }
        """)
    
    def set_value(self, value: str):
        """Update the displayed value with animation effect."""
        self.value_label.setText(value)
    
    def set_icon(self, icon: str):
        """Update the icon."""
        self.icon_label.setText(icon)
    
    def set_title(self, title: str):
        """Update the title."""
        self.title_label.setText(title)


class ChartContainer(QGroupBox):
    """A container widget for charts with improved layout and styling."""
    
    def __init__(self, title: str, chart: FigureCanvas, parent=None):
        super().__init__(title, parent)
        self.setObjectName("chart-container")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        # Add chart
        self.chart = chart
        self.chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.chart)
        
        # Add container styling
        self.setStyleSheet("""
            QGroupBox#chart-container {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 12px;
                margin-top: 15px;
                padding: 15px;
                padding-top: 25px;
                font-weight: bold;
                font-size: 13px;
                color: #cdd6f4;
            }
            QGroupBox#chart-container::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 10px;
                background-color: #313244;
                color: #cdd6f4;
            }
            QGroupBox#chart-container:hover {
                border-color: #89b4fa;
            }
        """)


class FolderTreeWidget(QTreeWidget):
    """Enhanced tree widget for folder navigation with icons and colors."""
    
    folder_selected = Signal(object)  # Emits FolderInfo
    
    # Category colors for visual distinction
    CATEGORY_COLORS = {
        FileCategory.DOCUMENTS: "#3498db",
        FileCategory.MEDIA_IMAGES: "#9b59b6",
        FileCategory.MEDIA_AUDIO: "#1abc9c",
        FileCategory.MEDIA_VIDEO: "#e74c3c",
        FileCategory.CODE: "#2ecc71",
        FileCategory.ARCHIVES: "#f39c12",
        FileCategory.DATA: "#00bcd4",
        FileCategory.EXECUTABLES: "#e91e63",
        FileCategory.OTHERS: "#95a5a6",
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(['📁 Name', '📦 Size', '📄 Files', '🏷️ Type'])
        self.setAnimated(True)
        self.setIndentation(25)
        self.setAlternatingRowColors(False)
        self.setRootIsDecorated(True)
        self.setExpandsOnDoubleClick(True)
        
        # Enable better column sizing
        header = self.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Store folder info mapping
        self._folder_map: Dict[int, FolderInfo] = {}
        
        # Connect selection
        self.itemClicked.connect(self._on_item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
    
    def populate(self, root_folder: FolderInfo):
        """Populate the tree with folder data."""
        self.clear()
        self._folder_map.clear()
        
        # Add root item
        root_item = self._create_folder_item(root_folder, is_root=True)
        self.addTopLevelItem(root_item)
        
        # Recursively add children
        self._add_children(root_item, root_folder)
        
        # Expand root
        root_item.setExpanded(True)
    
    def _create_folder_item(self, folder: FolderInfo, is_root: bool = False) -> QTreeWidgetItem:
        """Create a tree item for a folder with visual enhancements."""
        # Determine folder icon based on content
        if is_root:
            icon = "🏠"
        elif folder.folder_count > 5:
            icon = "📚"
        elif folder.dominant_category == FileCategory.MEDIA_IMAGES:
            icon = "🖼️"
        elif folder.dominant_category == FileCategory.MEDIA_VIDEO:
            icon = "🎬"
        elif folder.dominant_category == FileCategory.MEDIA_AUDIO:
            icon = "🎵"
        elif folder.dominant_category == FileCategory.CODE:
            icon = "💻"
        elif folder.dominant_category == FileCategory.DOCUMENTS:
            icon = "📄"
        elif folder.dominant_category == FileCategory.ARCHIVES:
            icon = "📦"
        elif folder.dominant_category == FileCategory.DATA:
            icon = "📊"
        else:
            icon = "📁"
        
        item = QTreeWidgetItem([
            f"{icon} {folder.name}",
            folder.size_formatted,
            f"{folder.file_count:,}",
            folder.dominant_category.value if folder.dominant_category else "-"
        ])
        
        # Color the type column based on category
        if folder.dominant_category and folder.dominant_category in self.CATEGORY_COLORS:
            color = QColor(self.CATEGORY_COLORS[folder.dominant_category])
            item.setForeground(3, QBrush(color))
        
        # Store folder info reference
        item_id = id(item)
        self._folder_map[item_id] = folder
        item.setData(0, Qt.UserRole, item_id)
        
        # Add tooltip with more info
        tooltip = f"Path: {folder.path}\nFiles: {folder.file_count:,}\nFolders: {folder.folder_count:,}\nSize: {folder.size_formatted}"
        item.setToolTip(0, tooltip)
        
        return item
    
    def _add_children(self, parent_item: QTreeWidgetItem, parent_folder: FolderInfo):
        """Recursively add child folders sorted by size."""
        # Sort children by size (largest first)
        sorted_children = sorted(parent_folder.children, key=lambda f: f.total_size, reverse=True)
        
        for child in sorted_children:
            child_item = self._create_folder_item(child)
            parent_item.addChild(child_item)
            
            # Add grandchildren for depth
            if child.children:
                self._add_children(child_item, child)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        item_id = item.data(0, Qt.UserRole)
        if item_id and item_id in self._folder_map:
            self.folder_selected.emit(self._folder_map[item_id])
    
    def _on_item_expanded(self, item: QTreeWidgetItem):
        """Handle item expansion - auto-resize columns."""
        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)


class CategoryCard(QFrame):
    """A card showing category statistics."""
    
    def __init__(self, category: FileCategory, parent=None):
        super().__init__(parent)
        self.category = category
        self.setObjectName("stat-card")
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        # Category name with icon
        icons = {
            FileCategory.DOCUMENTS: "📄",
            FileCategory.MEDIA_IMAGES: "🖼️",
            FileCategory.MEDIA_AUDIO: "🎵",
            FileCategory.MEDIA_VIDEO: "🎬",
            FileCategory.CODE: "💻",
            FileCategory.ARCHIVES: "📦",
            FileCategory.DATA: "📊",
            FileCategory.EXECUTABLES: "⚙️",
            FileCategory.OTHERS: "📎",
        }
        
        self.name_label = QLabel(f"{icons.get(category, '📁')} {category.value}")
        self.name_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {COLORS['text']};")
        layout.addWidget(self.name_label)
        
        # File count
        self.count_label = QLabel("0 files")
        self.count_label.setStyleSheet(f"color: {COLORS['subtext0']}; font-size: 11px;")
        layout.addWidget(self.count_label)
        
        # Size
        self.size_label = QLabel("0 B")
        self.size_label.setStyleSheet(f"color: {COLORS['blue']}; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.size_label)
        
        # Percentage bar
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet(f"color: {COLORS['subtext0']}; font-size: 10px;")
        layout.addWidget(self.percent_label)
    
    def update_stats(self, file_count: int, total_size: str, percentage: float):
        """Update the card with new statistics."""
        self.count_label.setText(f"{file_count:,} files")
        self.size_label.setText(total_size)
        self.percent_label.setText(f"{percentage:.1f}% of total")


class VisualizationSection(QFrame):
    """Section containing all visualization charts in tabs with enhanced styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Section header
        header = QLabel("📊 Visual Analytics")
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 10px; color: {COLORS['text']};")
        layout.addWidget(header)
        
        # Tab widget for charts with enhanced styling
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #45475a;
                border-radius: 8px;
                background-color: #313244;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #a6adc8;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #45475a;
                color: #89b4fa;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # Category pie chart
        self.pie_chart = CategoryPieChart()
        self.tabs.addTab(self.pie_chart, "📊 Category Distribution")
        
        # Folder comparison
        self.folder_chart = FolderBarChart()
        self.tabs.addTab(self.folder_chart, "📁 Folder Sizes")
        
        # Top files
        self.files_chart = TopFilesChart()
        self.tabs.addTab(self.files_chart, "📄 Largest Files")
        
        # Extension distribution
        self.ext_chart = ExtensionChart()
        self.tabs.addTab(self.ext_chart, "🏷️ Extensions")
        
        # File size distribution (new)
        self.size_dist_chart = SizeDistributionChart()
        self.tabs.addTab(self.size_dist_chart, "📏 Size Distribution")
        
        # File type treemap (new)
        self.treemap_chart = FileTypeTreemap()
        self.tabs.addTab(self.treemap_chart, "🌳 Category Treemap")
        
        layout.addWidget(self.tabs)
    
    def update_charts(self, analyzer: FolderAnalyzer):
        """Update all charts with new data."""
        percentages = analyzer.get_category_percentages()
        self.pie_chart.update_data(percentages)
        
        folder_comparison = analyzer.get_folder_comparison()
        self.folder_chart.update_data(folder_comparison)
        
        top_files = analyzer.get_top_files(10)
        self.files_chart.update_data(top_files)
        
        ext_dist = analyzer.get_extension_distribution()
        self.ext_chart.update_data(ext_dist)
        
        # Update new charts
        file_sizes = analyzer.get_file_sizes()
        self.size_dist_chart.update_data(file_sizes)
        
        self.treemap_chart.update_data(percentages)


class CategorySection(QFrame):
    """Section showing category breakdown."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Section header
        header = QLabel("📋 Category Breakdown")
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; padding-bottom: 10px; color: {COLORS['text']};")
        layout.addWidget(header)
        
        # Grid of category cards
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.category_cards: Dict[FileCategory, CategoryCard] = {}
        
        row, col = 0, 0
        for category in FileCategory:
            card = CategoryCard(category)
            self.category_cards[category] = card
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        layout.addLayout(grid)
    
    def update_categories(self, analyzer: FolderAnalyzer):
        """Update all category cards."""
        for category, card in self.category_cards.items():
            summary = analyzer.get_category_summary(category)
            card.update_stats(
                summary['file_count'],
                summary['total_size'],
                summary['percentage']
            )


class InsightsSection(QFrame):
    """Section showing insights and warnings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Insights group
        insights_header = QLabel("💡 Insights & Notes")
        insights_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text']};")
        layout.addWidget(insights_header)
        
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMinimumHeight(120)
        self.insights_text.setPlaceholderText("Analysis insights will appear here...")
        layout.addWidget(self.insights_text)
        
        # Warnings group
        warnings_header = QLabel("⚠️ Warnings & Recommendations")
        warnings_header.setStyleSheet(f"font-size: 16px; font-weight: bold; margin-top: 15px; color: {COLORS['text']};")
        layout.addWidget(warnings_header)
        
        self.warnings_text = QTextEdit()
        self.warnings_text.setReadOnly(True)
        self.warnings_text.setMinimumHeight(100)
        self.warnings_text.setPlaceholderText("No warnings to display.")
        layout.addWidget(self.warnings_text)
    
    def update_insights(self, insight_gen: InsightGenerator, folder: Optional[FolderInfo] = None):
        """Update insights and warnings."""
        insight = insight_gen.generate_folder_insight(folder)
        self.insights_text.setMarkdown(insight)
        
        warnings = insight_gen.generate_warnings(folder)
        if warnings:
            self.warnings_text.setMarkdown("\n\n".join(warnings))
        else:
            self.warnings_text.setMarkdown("✅ **No issues detected.**\n\nThis folder appears to be well-organized.")


class AnalyticsPanel(QScrollArea):
    """Main analytics display panel with separate sections."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        self._create_sections()
        self.setWidget(self.container)
    
    def _create_sections(self):
        """Create all analytics sections."""
        # ===== HEADER SECTION =====
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        self.header_label = QLabel("📊 Folder Analytics")
        self.header_label.setObjectName("title")
        header_layout.addWidget(self.header_label)
        
        self.path_label = QLabel("Select a folder to begin analysis")
        self.path_label.setObjectName("subtitle")
        self.path_label.setWordWrap(True)
        header_layout.addWidget(self.path_label)
        
        self.layout.addWidget(header_frame)
        
        # ===== STATS CARDS ROW =====
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.total_files_card = StatCard("Total Files", "0", "📄")
        self.total_folders_card = StatCard("Subfolders", "0", "📁")
        self.total_size_card = StatCard("Total Size", "0 B", "💾")
        self.scan_time_card = StatCard("Scan Time", "0s", "⏱️")
        
        stats_layout.addWidget(self.total_files_card)
        stats_layout.addWidget(self.total_folders_card)
        stats_layout.addWidget(self.total_size_card)
        stats_layout.addWidget(self.scan_time_card)
        
        self.layout.addWidget(stats_frame)
        
        # ===== VISUALIZATION SECTION =====
        self.viz_section = VisualizationSection()
        self.layout.addWidget(self.viz_section)
        
        # ===== CATEGORY SECTION =====
        self.category_section = CategorySection()
        self.layout.addWidget(self.category_section)
        
        # ===== INSIGHTS SECTION =====
        self.insights_section = InsightsSection()
        self.layout.addWidget(self.insights_section)
        
        # Add stretch at the end
        self.layout.addStretch()
    
    def update_with_result(self, result: ScanResult):
        """Update all sections with scan result."""
        # Update header
        self.header_label.setText(f"📊 Analysis: {result.root_folder.name}")
        self.path_label.setText(str(result.root_folder.path))
        
        # Update stats cards
        self.total_files_card.set_value(f"{result.total_files:,}")
        self.total_folders_card.set_value(f"{result.total_folders:,}")
        self.total_size_card.set_value(result.size_formatted)
        self.scan_time_card.set_value(f"{result.scan_time:.2f}s")
        
        # Create analyzer and insight generator
        analyzer = FolderAnalyzer(result)
        insight_gen = InsightGenerator(analyzer)
        
        # Update sections
        self.viz_section.update_charts(analyzer)
        self.category_section.update_categories(analyzer)
        self.insights_section.update_insights(insight_gen)
    
    def update_with_folder(self, folder: FolderInfo, parent_result: ScanResult):
        """Update analytics for a specific folder."""
        # Create a temporary result for this folder
        folder_result = ScanResult(
            root_folder=folder,
            total_files=folder.file_count,
            total_folders=folder.folder_count,
            total_size=folder.total_size,
            categories=folder.categories,
            largest_files=[],
            scan_time=0
        )
        
        # Collect largest files from this folder
        def collect_files(f: FolderInfo, file_list: list):
            file_list.extend(f.files)
            for child in f.children:
                collect_files(child, file_list)
        
        all_files = []
        collect_files(folder, all_files)
        all_files.sort(key=lambda x: x.size, reverse=True)
        folder_result.largest_files = all_files[:20]
        
        # Update header for selected folder
        self.header_label.setText(f"📊 Folder: {folder.name}")
        self.path_label.setText(str(folder.path))
        
        # Update stats cards
        self.total_files_card.set_value(f"{folder.file_count:,}")
        self.total_folders_card.set_value(f"{folder.folder_count:,}")
        self.total_size_card.set_value(folder.size_formatted)
        self.scan_time_card.set_value("-")
        
        # Create analyzer and insight generator
        analyzer = FolderAnalyzer(folder_result)
        insight_gen = InsightGenerator(analyzer)
        
        # Update sections
        self.viz_section.update_charts(analyzer)
        self.category_section.update_categories(analyzer)
        self.insights_section.update_insights(insight_gen, folder)


class TreeSection(QFrame):
    """Section containing the folder tree with header."""
    
    folder_selected = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🌲 Folder Structure")
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 10px; color: {COLORS['text']};")
        layout.addWidget(header)
        
        # Tree widget
        self.tree = FolderTreeWidget()
        self.tree.folder_selected.connect(self.folder_selected.emit)
        layout.addWidget(self.tree)
    
    def populate(self, root_folder: FolderInfo):
        """Populate the tree."""
        self.tree.populate(root_folder)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Analyzer - Visual Storage Explorer")
        self.setMinimumSize(1300, 850)
        self.resize(1500, 950)
        
        # Set custom window icon
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback to PNG
            png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
            if os.path.exists(png_path):
                self.setWindowIcon(QIcon(png_path))
        
        # State
        self.current_result: Optional[ScanResult] = None
        self.scanner_thread: Optional[ScannerThread] = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # ===== TOP TOOLBAR =====
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("card")
        toolbar_frame.setStyleSheet("""
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #313244, stop:0.5 #3b3d54, stop:1 #313244);
                border: 1px solid #45475a;
                border-radius: 12px;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(20, 12, 20, 12)
        
        # Logo container
        logo_container = QFrame()
        logo_container.setStyleSheet("background: transparent; border: none;")
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(12)
        
        # Logo icon with glow effect
        logo_icon = QLabel("🔍")
        logo_icon.setStyleSheet("""
            font-size: 32px;
            background: transparent;
        """)
        logo_layout.addWidget(logo_icon)
        
        # App name and tagline
        name_container = QFrame()
        name_container.setStyleSheet("background: transparent; border: none;")
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(0)
        
        app_title = QLabel("File Analyzer")
        app_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: #cdd6f4;
            background: transparent;
            letter-spacing: 1px;
        """)
        name_layout.addWidget(app_title)
        
        app_tagline = QLabel("Visual Storage Explorer")
        app_tagline.setStyleSheet(f"""
            font-size: 11px;
            color: #89b4fa;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        name_layout.addWidget(app_tagline)
        
        logo_layout.addWidget(name_container)
        
        # Version badge
        version_badge = QLabel("v1.0")
        version_badge.setStyleSheet("""
            background-color: #89b4fa;
            color: #1e1e2e;
            font-size: 9px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 8px;
        """)
        logo_layout.addWidget(version_badge)
        
        toolbar_layout.addWidget(logo_container)
        toolbar_layout.addStretch()
        
        self.select_btn = QPushButton("📁  Browse Folder")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #89b4fa, stop:1 #74c7ec);
                color: #1e1e2e;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #74c7ec, stop:1 #89dceb);
            }
            QPushButton:pressed {
                background: #b4befe;
            }
            QPushButton:disabled {
                background: #585b70;
                color: #6c7086;
            }
        """)
        self.select_btn.setMinimumWidth(180)
        self.select_btn.setMinimumHeight(44)
        toolbar_layout.addWidget(self.select_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumWidth(200)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #45475a;
                border: none;
                border-radius: 8px;
                height: 24px;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #89b4fa, stop:1 #a6e3a1);
                border-radius: 7px;
            }
        """)
        toolbar_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to analyze")
        self.status_label.setStyleSheet(f"color: {COLORS['subtext0']}; padding-left: 15px; font-size: 12px;")
        toolbar_layout.addWidget(self.status_label)
        
        main_layout.addWidget(toolbar_frame)
        
        # ===== MAIN SPLITTER =====
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Tree section
        self.tree_section = TreeSection()
        self.tree_section.setMinimumWidth(350)
        
        # Right panel - Analytics
        self.analytics_panel = AnalyticsPanel()
        
        # Add to splitter
        self.splitter.addWidget(self.tree_section)
        self.splitter.addWidget(self.analytics_panel)
        self.splitter.setSizes([400, 900])
        
        main_layout.addWidget(self.splitter, 1)
        
        # Status bar
        self.statusBar().showMessage("Welcome to File Analyzer - Select a folder to begin")
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.select_btn.clicked.connect(self._on_select_folder)
        self.tree_section.folder_selected.connect(self._on_folder_selected)
    
    @Slot()
    def _on_select_folder(self):
        """Handle folder selection."""
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
        
        # Update UI
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText(f"Scanning: {folder_path}")
        self.statusBar().showMessage("Scanning in progress...")
        
        # Start scanner
        self.scanner_thread = ScannerThread(folder_path)
        self.scanner_thread.progress.connect(self._on_scan_progress)
        self.scanner_thread.scan_complete.connect(self._on_scan_complete)
        self.scanner_thread.error.connect(self._on_scan_error)
        self.scanner_thread.start()
    
    @Slot(str, int)
    def _on_scan_progress(self, current_path: str, files_scanned: int):
        """Update progress during scan."""
        self.status_label.setText(f"Scanned {files_scanned:,} files...")
    
    @Slot(object)
    def _on_scan_complete(self, result: ScanResult):
        """Handle scan completion."""
        self.current_result = result
        
        # Update UI
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✅ Scan complete: {result.total_files:,} files")
        self.statusBar().showMessage(
            f"Analysis complete - {result.total_files:,} files, {result.size_formatted}, scanned in {result.scan_time:.2f}s"
        )
        
        # Populate tree and analytics
        self.tree_section.populate(result.root_folder)
        self.analytics_panel.update_with_result(result)
    
    @Slot(str)
    def _on_scan_error(self, error_msg: str):
        """Handle scan error."""
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ Error: {error_msg}")
        self.statusBar().showMessage(f"Scan failed: {error_msg}")
    
    @Slot(object)
    def _on_folder_selected(self, folder: FolderInfo):
        """Handle folder selection in tree."""
        if self.current_result:
            self.analytics_panel.update_with_folder(folder, self.current_result)
            self.statusBar().showMessage(
                f"Viewing: {folder.name} - {folder.file_count:,} files, {folder.size_formatted}"
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
    app.setStyle('Fusion')  # Modern look
    app.setStyleSheet(DARK_STYLESHEET)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
