"""
Data models for the File Analyzer application.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class FileCategory(Enum):
    """Categories for file classification."""
    DOCUMENTS = "Documents"
    MEDIA_IMAGES = "Images"
    MEDIA_AUDIO = "Audio"
    MEDIA_VIDEO = "Video"
    CODE = "Code"
    ARCHIVES = "Archives"
    DATA = "Data"
    EXECUTABLES = "Executables"
    OTHERS = "Others"


# Extension to category mapping
EXTENSION_CATEGORIES: Dict[str, FileCategory] = {
    # Documents
    '.pdf': FileCategory.DOCUMENTS,
    '.doc': FileCategory.DOCUMENTS,
    '.docx': FileCategory.DOCUMENTS,
    '.txt': FileCategory.DOCUMENTS,
    '.md': FileCategory.DOCUMENTS,
    '.rtf': FileCategory.DOCUMENTS,
    '.odt': FileCategory.DOCUMENTS,
    '.xls': FileCategory.DOCUMENTS,
    '.xlsx': FileCategory.DOCUMENTS,
    '.ppt': FileCategory.DOCUMENTS,
    '.pptx': FileCategory.DOCUMENTS,
    
    # Images
    '.jpg': FileCategory.MEDIA_IMAGES,
    '.jpeg': FileCategory.MEDIA_IMAGES,
    '.png': FileCategory.MEDIA_IMAGES,
    '.gif': FileCategory.MEDIA_IMAGES,
    '.bmp': FileCategory.MEDIA_IMAGES,
    '.svg': FileCategory.MEDIA_IMAGES,
    '.webp': FileCategory.MEDIA_IMAGES,
    '.ico': FileCategory.MEDIA_IMAGES,
    '.tiff': FileCategory.MEDIA_IMAGES,
    '.psd': FileCategory.MEDIA_IMAGES,
    
    # Audio
    '.mp3': FileCategory.MEDIA_AUDIO,
    '.wav': FileCategory.MEDIA_AUDIO,
    '.flac': FileCategory.MEDIA_AUDIO,
    '.aac': FileCategory.MEDIA_AUDIO,
    '.ogg': FileCategory.MEDIA_AUDIO,
    '.wma': FileCategory.MEDIA_AUDIO,
    '.m4a': FileCategory.MEDIA_AUDIO,
    
    # Video
    '.mp4': FileCategory.MEDIA_VIDEO,
    '.avi': FileCategory.MEDIA_VIDEO,
    '.mkv': FileCategory.MEDIA_VIDEO,
    '.mov': FileCategory.MEDIA_VIDEO,
    '.wmv': FileCategory.MEDIA_VIDEO,
    '.flv': FileCategory.MEDIA_VIDEO,
    '.webm': FileCategory.MEDIA_VIDEO,
    '.m4v': FileCategory.MEDIA_VIDEO,
    
    # Code
    '.py': FileCategory.CODE,
    '.js': FileCategory.CODE,
    '.ts': FileCategory.CODE,
    '.jsx': FileCategory.CODE,
    '.tsx': FileCategory.CODE,
    '.html': FileCategory.CODE,
    '.css': FileCategory.CODE,
    '.scss': FileCategory.CODE,
    '.sass': FileCategory.CODE,
    '.less': FileCategory.CODE,
    '.java': FileCategory.CODE,
    '.cpp': FileCategory.CODE,
    '.c': FileCategory.CODE,
    '.h': FileCategory.CODE,
    '.hpp': FileCategory.CODE,
    '.cs': FileCategory.CODE,
    '.go': FileCategory.CODE,
    '.rs': FileCategory.CODE,
    '.rb': FileCategory.CODE,
    '.php': FileCategory.CODE,
    '.swift': FileCategory.CODE,
    '.kt': FileCategory.CODE,
    '.scala': FileCategory.CODE,
    '.vue': FileCategory.CODE,
    '.sql': FileCategory.CODE,
    '.sh': FileCategory.CODE,
    '.bat': FileCategory.CODE,
    '.ps1': FileCategory.CODE,
    
    # Archives
    '.zip': FileCategory.ARCHIVES,
    '.rar': FileCategory.ARCHIVES,
    '.7z': FileCategory.ARCHIVES,
    '.tar': FileCategory.ARCHIVES,
    '.gz': FileCategory.ARCHIVES,
    '.bz2': FileCategory.ARCHIVES,
    '.xz': FileCategory.ARCHIVES,
    '.iso': FileCategory.ARCHIVES,
    
    # Data
    '.csv': FileCategory.DATA,
    '.json': FileCategory.DATA,
    '.xml': FileCategory.DATA,
    '.yaml': FileCategory.DATA,
    '.yml': FileCategory.DATA,
    '.sqlite': FileCategory.DATA,
    '.db': FileCategory.DATA,
    '.parquet': FileCategory.DATA,
    
    # Executables
    '.exe': FileCategory.EXECUTABLES,
    '.msi': FileCategory.EXECUTABLES,
    '.dll': FileCategory.EXECUTABLES,
    '.app': FileCategory.EXECUTABLES,
    '.dmg': FileCategory.EXECUTABLES,
    '.deb': FileCategory.EXECUTABLES,
    '.rpm': FileCategory.EXECUTABLES,
}


# Category descriptions for insights
CATEGORY_DESCRIPTIONS: Dict[FileCategory, str] = {
    FileCategory.DOCUMENTS: "Text documents, spreadsheets, and presentations used for written content and reports.",
    FileCategory.MEDIA_IMAGES: "Image files including photos, graphics, icons, and design assets.",
    FileCategory.MEDIA_AUDIO: "Audio files including music, podcasts, sound effects, and recordings.",
    FileCategory.MEDIA_VIDEO: "Video files including movies, clips, recordings, and multimedia content.",
    FileCategory.CODE: "Source code files used in software development across various programming languages.",
    FileCategory.ARCHIVES: "Compressed files and archives containing bundled or backed-up data.",
    FileCategory.DATA: "Structured data files used for storage, configuration, and data exchange.",
    FileCategory.EXECUTABLES: "Executable programs and installers for various operating systems.",
    FileCategory.OTHERS: "Miscellaneous files that don't fit into standard categories.",
}


@dataclass
class FileInfo:
    """Information about a single file."""
    path: Path
    name: str
    extension: str
    size: int  # in bytes
    category: FileCategory
    modified_time: float = 0.0
    
    @property
    def size_formatted(self) -> str:
        """Return human-readable file size."""
        return format_size(self.size)


@dataclass
class CategoryStats:
    """Statistics for a file category."""
    category: FileCategory
    file_count: int = 0
    total_size: int = 0
    extensions: Dict[str, int] = field(default_factory=dict)  # ext -> count
    largest_files: List[FileInfo] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        """Placeholder - will be calculated by analyzer."""
        return 0.0
    
    @property
    def size_formatted(self) -> str:
        return format_size(self.total_size)
    
    @property
    def most_common_extensions(self) -> List[tuple]:
        """Return top 5 most common extensions."""
        sorted_exts = sorted(self.extensions.items(), key=lambda x: x[1], reverse=True)
        return sorted_exts[:5]


@dataclass
class FolderInfo:
    """Information about a folder and its contents."""
    path: Path
    name: str
    file_count: int = 0
    folder_count: int = 0
    total_size: int = 0
    categories: Dict[FileCategory, CategoryStats] = field(default_factory=dict)
    children: List['FolderInfo'] = field(default_factory=list)
    files: List[FileInfo] = field(default_factory=list)
    dominant_category: Optional[FileCategory] = None
    is_scanned: bool = False
    
    @property
    def size_formatted(self) -> str:
        return format_size(self.total_size)


@dataclass
class ScanResult:
    """Complete result of a folder scan."""
    root_folder: FolderInfo
    total_files: int = 0
    total_folders: int = 0
    total_size: int = 0
    categories: Dict[FileCategory, CategoryStats] = field(default_factory=dict)
    largest_files: List[FileInfo] = field(default_factory=list)
    scan_time: float = 0.0
    
    @property
    def size_formatted(self) -> str:
        return format_size(self.total_size)


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def get_category(extension: str) -> FileCategory:
    """Get the category for a file extension."""
    ext_lower = extension.lower()
    return EXTENSION_CATEGORIES.get(ext_lower, FileCategory.OTHERS)
