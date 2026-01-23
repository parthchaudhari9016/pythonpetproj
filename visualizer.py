"""
Visualization components using Matplotlib embedded in PySide6.
Enhanced with interactive features and improved styling.
"""
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from models import FileCategory


# Catppuccin Mocha color palette for consistent theming
CATEGORY_COLORS = {
    FileCategory.DOCUMENTS: '#89b4fa',      # Blue
    FileCategory.MEDIA_IMAGES: '#cba6f7',   # Mauve
    FileCategory.MEDIA_AUDIO: '#94e2d5',    # Teal
    FileCategory.MEDIA_VIDEO: '#f38ba8',    # Red
    FileCategory.CODE: '#a6e3a1',           # Green
    FileCategory.ARCHIVES: '#fab387',       # Peach
    FileCategory.DATA: '#89dceb',           # Sky
    FileCategory.EXECUTABLES: '#f5c2e7',    # Pink
    FileCategory.OTHERS: '#94a3b8',         # Gray
}


class BaseChart(FigureCanvas):
    """Base class for all charts."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1e1e2e')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Dark theme styling
        self.fig.patch.set_facecolor('#1e1e2e')
    
    def clear(self):
        """Clear the figure."""
        self.fig.clear()
        self.draw()


class CategoryPieChart(BaseChart):
    """Pie chart showing category distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent, width=5, height=4)
    
    def update_data(self, categories: Dict[FileCategory, float]):
        """Update the chart with new data."""
        self.fig.clear()
        
        if not categories:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   color='#cdd6f4', fontsize=12)
            ax.axis('off')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Prepare data
        labels = [cat.value for cat in categories.keys()]
        sizes = list(categories.values())
        colors = [CATEGORY_COLORS.get(cat, '#95a5a6') for cat in categories.keys()]
        
        # Create pie chart with donut style
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=None,
            colors=colors,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
            pctdistance=0.75,
            startangle=90,
            wedgeprops=dict(width=0.5, edgecolor='#1e1e2e', linewidth=2)
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('#cdd6f4')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        # Add legend
        ax.legend(
            wedges, labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(0.9, 0, 0.5, 1),
            fontsize=8,
            title_fontsize=9,
            facecolor='#313244',
            edgecolor='#45475a',
            labelcolor='#cdd6f4'
        )
        
        ax.set_title('Storage by Category', color='#cdd6f4', fontsize=12, fontweight='bold', pad=10)
        
        self.fig.tight_layout()
        self.draw()


class FolderBarChart(BaseChart):
    """Horizontal bar chart comparing folder sizes."""
    
    def __init__(self, parent=None):
        super().__init__(parent, width=6, height=4)
    
    def update_data(self, folders: List[Tuple[str, int, str]]):
        """Update chart with folder comparison data."""
        self.fig.clear()
        
        if not folders:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'No subfolders found', ha='center', va='center', 
                   color='#cdd6f4', fontsize=12)
            ax.axis('off')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Prepare data (reverse for bottom-to-top display)
        names = [f[0][:20] + '...' if len(f[0]) > 20 else f[0] for f in folders][::-1]
        sizes = [f[1] for f in folders][::-1]
        size_labels = [f[2] for f in folders][::-1]
        
        # Create gradient colors
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(names)))
        
        # Create horizontal bar chart
        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, sizes, color=colors, edgecolor='#45475a', height=0.7)
        
        # Add size labels on bars
        for bar, label in zip(bars, size_labels):
            width = bar.get_width()
            ax.text(width + max(sizes) * 0.02, bar.get_y() + bar.get_height()/2, 
                   label, va='center', color='#cdd6f4', fontsize=8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, color='#cdd6f4', fontsize=9)
        ax.set_xlabel('Size (bytes)', color='#a6adc8', fontsize=9)
        ax.set_title('Top Folders by Size', color='#cdd6f4', fontsize=12, fontweight='bold')
        
        # Style axes
        ax.tick_params(colors='#6c7086')
        ax.spines['bottom'].set_color('#45475a')
        ax.spines['left'].set_color('#45475a')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Remove x-axis labels (we have size labels on bars)
        ax.set_xticklabels([])
        
        self.fig.tight_layout()
        self.draw()


class TopFilesChart(BaseChart):
    """Chart showing top largest files."""
    
    def __init__(self, parent=None):
        super().__init__(parent, width=6, height=4)
    
    def update_data(self, files: List[Tuple[str, str, str, str]]):
        """Update chart with largest files data."""
        self.fig.clear()
        
        if not files:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'No files found', ha='center', va='center', 
                   color='#cdd6f4', fontsize=12)
            ax.axis('off')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Prepare data
        names = [f[0][:25] + '...' if len(f[0]) > 25 else f[0] for f in files][::-1]
        size_labels = [f[1] for f in files][::-1]
        categories = [f[2] for f in files][::-1]
        
        # Parse sizes to bytes for chart
        def parse_size(size_str):
            parts = size_str.split()
            if len(parts) != 2:
                return 0
            value = float(parts[0])
            unit = parts[1].upper()
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
            return value * multipliers.get(unit, 1)
        
        sizes = [parse_size(s) for s in size_labels]
        
        # Get colors based on category
        cat_map = {cat.value: cat for cat in FileCategory}
        colors = [CATEGORY_COLORS.get(cat_map.get(c, FileCategory.OTHERS), '#95a5a6') for c in categories]
        
        # Create bar chart
        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, sizes, color=colors, edgecolor='#45475a', height=0.7)
        
        # Add size labels
        for bar, label in zip(bars, size_labels):
            width = bar.get_width()
            ax.text(width + max(sizes) * 0.02, bar.get_y() + bar.get_height()/2, 
                   label, va='center', color='#cdd6f4', fontsize=8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, color='#cdd6f4', fontsize=8)
        ax.set_title('Top 10 Largest Files', color='#cdd6f4', fontsize=12, fontweight='bold')
        
        # Style axes
        ax.tick_params(colors='#6c7086')
        ax.spines['bottom'].set_color('#45475a')
        ax.spines['left'].set_color('#45475a')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xticklabels([])
        
        self.fig.tight_layout()
        self.draw()


class ExtensionChart(BaseChart):
    """Bar chart showing extension distribution with improved visuals."""
    
    def __init__(self, parent=None):
        super().__init__(parent, width=6, height=3)
    
    def update_data(self, extensions: Dict[str, int]):
        """Update chart with extension distribution."""
        self.fig.clear()
        
        if not extensions:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'No extension data', ha='center', va='center', 
                   color='#cdd6f4', fontsize=12)
            ax.axis('off')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Prepare data - sort by count descending
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:12]
        exts = [ext for ext, count in sorted_exts]
        counts = [count for ext, count in sorted_exts]
        
        # Create gradient colors using Catppuccin inspired palette
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(exts)))
        
        # Create bar chart with enhanced styling
        x_pos = np.arange(len(exts))
        bars = ax.bar(x_pos, counts, color=colors, edgecolor='#45475a', width=0.7)
        
        # Add count labels on top of bars with improved visibility
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts) * 0.02,
                   str(count), ha='center', color='#cdd6f4', fontsize=8, fontweight='bold')
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(exts, rotation=45, ha='right', color='#cdd6f4', fontsize=8)
        ax.set_ylabel('File Count', color='#a6adc8', fontsize=9)
        ax.set_title('Top File Extensions', color='#cdd6f4', fontsize=12, fontweight='bold', pad=10)
        
        # Style axes with enhanced visibility
        ax.tick_params(colors='#6c7086')
        ax.spines['bottom'].set_color('#45475a')
        ax.spines['left'].set_color('#45475a')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add subtle grid for readability
        ax.yaxis.grid(True, color='#313244', linestyle='-', linewidth=0.3)
        
        self.fig.tight_layout()
        self.draw()


class SizeDistributionChart(BaseChart):
    """Histogram showing file size distribution for better storage analysis."""
    
    def __init__(self, parent=None):
        super().__init__(parent, width=6, height=3.5)
    
    def update_data(self, file_sizes: List[int]):
        """Update chart with file size distribution data."""
        self.fig.clear()
        
        if not file_sizes:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'No size distribution data', ha='center', va='center', 
                   color='#cdd6f4', fontsize=12)
            ax.axis('off')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Convert bytes to MB for readability
        sizes_mb = [size / (1024 * 1024) for size in file_sizes if size > 0]
        
        # Create histogram with log scale for better distribution
        n, bins, patches = ax.hist(sizes_mb, bins=10, color='#89b4fa', edgecolor='#45475a', linewidth=1.5)
        
        # Color gradient for bins
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(patches)))
        for patch, color in zip(patches, colors):
            patch.set_facecolor(color)
        
        # Add count labels on top of each bin
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        for count, x in zip(n, bin_centers):
            if count > 0:
                ax.text(x, count + max(n) * 0.02, f'{int(count)}', 
                       ha='center', va='bottom', color='#cdd6f4', fontsize=8)
        
        ax.set_xlabel('File Size (MB)', color='#a6adc8', fontsize=9)
        ax.set_ylabel('Number of Files', color='#a6adc8', fontsize=9)
        ax.set_title('File Size Distribution', color='#cdd6f4', fontsize=12, fontweight='bold', pad=10)
        
        # Style axes
        ax.tick_params(colors='#6c7086')
        ax.spines['bottom'].set_color('#45475a')
        ax.spines['left'].set_color('#45475a')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add grid for better readability
        ax.yaxis.grid(True, color='#313244', linestyle='-', linewidth=0.3)
        
        self.fig.tight_layout()
        self.draw()


class FileTypeTreemap(BaseChart):
    """Treemap visualization showing file type distribution by size."""
    
    def __init__(self, parent=None):
        super().__init__(parent, width=7, height=4)
    
    def update_data(self, categories: Dict[FileCategory, float]):
        """Update chart with category size distribution for treemap."""
        self.fig.clear()
        
        if not categories:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'No category data', ha='center', va='center', 
                   color='#cdd6f4', fontsize=12)
            ax.axis('off')
            self.draw()
            return
        
        try:
            import squarify  # Check if squarify is available
        except ImportError:
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e2e')
            ax.text(0.5, 0.5, 'Treemap library not installed', ha='center', va='center', 
                   color='#f38ba8', fontsize=11)
            ax.axis('off')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Prepare data
        labels = [f"{cat.value}\n{size:.1f}%" for cat, size in categories.items()]
        sizes = list(categories.values())
        colors = [CATEGORY_COLORS.get(cat, '#94a3b8') for cat in categories.keys()]
        
        # Create treemap
        squarify.plot(
            sizes=sizes,
            label=labels,
            color=colors,
            alpha=0.8,
            edgecolor='#1e1e2e',
            linewidth=2
        )
        
        # Customize labels
        ax.set_title('Storage Distribution by Category', color='#cdd6f4', fontsize=12, fontweight='bold', pad=10)
        ax.axis('off')
        
        self.fig.tight_layout()
        self.draw()
