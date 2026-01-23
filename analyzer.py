"""
File analysis and statistics calculation.
"""
from typing import Dict, List, Tuple, Optional
from models import (
    FolderInfo, ScanResult, CategoryStats, FileInfo,
    FileCategory, format_size, CATEGORY_DESCRIPTIONS
)


class FolderAnalyzer:
    """Analyzes folder contents and generates statistics."""
    
    def __init__(self, scan_result: ScanResult):
        self.result = scan_result
    
    def get_category_percentages(self) -> Dict[FileCategory, float]:
        """Calculate percentage of storage used by each category."""
        if self.result.total_size == 0:
            return {}
        
        percentages = {}
        for category, stats in self.result.categories.items():
            percentages[category] = (stats.total_size / self.result.total_size) * 100
        
        return percentages
    
    def get_category_summary(self, category: FileCategory) -> Dict:
        """Get detailed summary for a category."""
        if category not in self.result.categories:
            return {
                'file_count': 0,
                'total_size': '0 B',
                'percentage': 0,
                'extensions': [],
                'largest_files': []
            }
        
        stats = self.result.categories[category]
        percentage = (stats.total_size / self.result.total_size * 100) if self.result.total_size > 0 else 0
        
        return {
            'file_count': stats.file_count,
            'total_size': stats.size_formatted,
            'total_size_bytes': stats.total_size,
            'percentage': round(percentage, 1),
            'extensions': stats.most_common_extensions,
            'largest_files': [(f.name, f.size_formatted, str(f.path)) for f in stats.largest_files[:5]],
            'description': CATEGORY_DESCRIPTIONS.get(category, "")
        }
    
    def get_folder_comparison(self) -> List[Tuple[str, int, str]]:
        """Get folder sizes for comparison chart."""
        folders = []
        
        for child in self.result.root_folder.children:
            folders.append((child.name, child.total_size, child.size_formatted))
        
        # Sort by size descending
        folders.sort(key=lambda x: x[1], reverse=True)
        return folders[:10]  # Top 10 folders
    
    def get_top_files(self, count: int = 10) -> List[Tuple[str, str, str, str]]:
        """Get the largest files."""
        return [
            (f.name, f.size_formatted, f.category.value, str(f.path))
            for f in self.result.largest_files[:count]
        ]
    
    def get_extension_distribution(self) -> Dict[str, int]:
        """Get file count by extension."""
        extension_counts = {}
        
        for category, stats in self.result.categories.items():
            for ext, count in stats.extensions.items():
                extension_counts[ext] = extension_counts.get(ext, 0) + count
        
        # Sort and return top 15
        sorted_exts = sorted(extension_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_exts[:15])
    
    def get_overview_stats(self) -> Dict:
        """Get overview statistics for the scanned folder."""
        return {
            'total_files': self.result.total_files,
            'total_folders': self.result.total_folders,
            'total_size': self.result.size_formatted,
            'total_size_bytes': self.result.total_size,
            'scan_time': f"{self.result.scan_time:.2f}s",
            'categories_count': len(self.result.categories),
            'path': str(self.result.root_folder.path)
        }


class InsightGenerator:
    """Generates human-readable insights about folder contents."""
    
    WARNING_THRESHOLDS = {
        'large_file_mb': 500,  # Files larger than 500MB
        'high_percentage': 60,  # Category using more than 60%
        'many_files': 1000,  # More than 1000 files in category
    }
    
    def __init__(self, analyzer: FolderAnalyzer):
        self.analyzer = analyzer
    
    def generate_folder_insight(self, folder: Optional[FolderInfo] = None) -> str:
        """Generate insight text for a folder."""
        if folder is None:
            folder = self.analyzer.result.root_folder
        
        if folder.file_count == 0:
            return "📁 This folder is empty or contains only subdirectories."
        
        insights = []
        
        # Dominant category insight
        if folder.dominant_category:
            cat_name = folder.dominant_category.value
            if folder.dominant_category in folder.categories:
                stats = folder.categories[folder.dominant_category]
                percentage = (stats.total_size / folder.total_size * 100) if folder.total_size > 0 else 0
                
                insights.append(
                    f"📊 **Dominant Category: {cat_name}**\n"
                    f"This folder is primarily composed of {cat_name.lower()} files, "
                    f"occupying {percentage:.1f}% of the total storage ({stats.size_formatted})."
                )
        
        # Size insight
        insights.append(
            f"\n📦 **Storage Overview**\n"
            f"Contains {folder.file_count:,} files across {folder.folder_count:,} subfolders, "
            f"totaling {folder.size_formatted}."
        )
        
        # Category breakdown
        if len(folder.categories) > 1:
            breakdown = []
            for cat, stats in sorted(folder.categories.items(), key=lambda x: x[1].total_size, reverse=True):
                pct = (stats.total_size / folder.total_size * 100) if folder.total_size > 0 else 0
                breakdown.append(f"  • {cat.value}: {stats.file_count} files ({pct:.1f}%)")
            
            insights.append("\n📋 **Category Breakdown**\n" + "\n".join(breakdown[:5]))
        
        return "\n".join(insights)
    
    def generate_warnings(self, folder: Optional[FolderInfo] = None) -> List[str]:
        """Generate warning messages for potential issues."""
        if folder is None:
            folder = self.analyzer.result.root_folder
        
        warnings = []
        
        # Check for very large files
        for cat, stats in folder.categories.items():
            for file in stats.largest_files[:3]:
                if file.size > self.WARNING_THRESHOLDS['large_file_mb'] * 1024 * 1024:
                    warnings.append(
                        f"⚠️ **Large File Detected**: '{file.name}' is {file.size_formatted}. "
                        f"Consider archiving or moving if not frequently accessed."
                    )
        
        # Check for dominant categories
        for cat, stats in folder.categories.items():
            pct = (stats.total_size / folder.total_size * 100) if folder.total_size > 0 else 0
            if pct > self.WARNING_THRESHOLDS['high_percentage']:
                warnings.append(
                    f"📈 **High Storage Usage**: {cat.value} files use {pct:.1f}% of this folder. "
                    f"{CATEGORY_DESCRIPTIONS.get(cat, '')}"
                )
        
        # Check for many small files
        for cat, stats in folder.categories.items():
            if stats.file_count > self.WARNING_THRESHOLDS['many_files']:
                avg_size = stats.total_size / stats.file_count if stats.file_count > 0 else 0
                if avg_size < 100 * 1024:  # Less than 100KB average
                    warnings.append(
                        f"📁 **Many Small Files**: {stats.file_count:,} {cat.value.lower()} files detected. "
                        f"Consider consolidating or archiving if possible."
                    )
        
        return warnings
    
    def generate_category_insight(self, category: FileCategory) -> str:
        """Generate detailed insight for a specific category."""
        summary = self.analyzer.get_category_summary(category)
        
        if summary['file_count'] == 0:
            return f"No {category.value.lower()} files found in this folder."
        
        insight = f"## {category.value}\n\n"
        insight += f"**{summary['description']}**\n\n"
        insight += f"📊 **Statistics**\n"
        insight += f"  • Total Files: {summary['file_count']:,}\n"
        insight += f"  • Total Size: {summary['total_size']} ({summary['percentage']}% of folder)\n"
        
        if summary['extensions']:
            insight += f"\n📎 **Common Extensions**\n"
            for ext, count in summary['extensions']:
                insight += f"  • {ext}: {count} files\n"
        
        if summary['largest_files']:
            insight += f"\n📁 **Largest Files**\n"
            for name, size, path in summary['largest_files']:
                insight += f"  • {name} ({size})\n"
        
        return insight
