"""
Directory scanner with threading support.
"""
import os
import time
from pathlib import Path
from typing import Optional, Callable
from PySide6.QtCore import QThread, Signal

from models import (
    FileInfo, FolderInfo, ScanResult, CategoryStats,
    FileCategory, get_category, EXTENSION_CATEGORIES
)


class ScannerThread(QThread):
    """Background thread for scanning directories."""
    
    # Signals
    progress = Signal(str, int)  # current_path, files_scanned
    folder_scanned = Signal(object)  # FolderInfo
    scan_complete = Signal(object)  # ScanResult
    error = Signal(str)
    
    def __init__(self, root_path: str, parent=None):
        super().__init__(parent)
        self.root_path = Path(root_path)
        self._is_cancelled = False
        self._files_scanned = 0
    
    def cancel(self):
        """Request cancellation of the scan."""
        self._is_cancelled = True
    
    def run(self):
        """Execute the scan in background."""
        try:
            start_time = time.time()
            
            # Scan the directory tree
            root_folder = self._scan_folder(self.root_path)
            
            if self._is_cancelled:
                return
            
            # Build the scan result
            result = self._build_result(root_folder, time.time() - start_time)
            
            self.scan_complete.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _scan_folder(self, folder_path: Path, depth: int = 0) -> FolderInfo:
        """Recursively scan a folder."""
        folder_info = FolderInfo(
            path=folder_path,
            name=folder_path.name or str(folder_path)
        )
        
        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    if self._is_cancelled:
                        return folder_info
                    
                    try:
                        if entry.is_file(follow_symlinks=False):
                            file_info = self._scan_file(entry)
                            if file_info:
                                folder_info.files.append(file_info)
                                folder_info.file_count += 1
                                folder_info.total_size += file_info.size
                                
                                # Update category stats
                                self._update_category_stats(folder_info, file_info)
                                
                                self._files_scanned += 1
                                if self._files_scanned % 100 == 0:
                                    self.progress.emit(str(folder_path), self._files_scanned)
                        
                        elif entry.is_dir(follow_symlinks=False):
                            # Skip system/hidden folders
                            if entry.name.startswith('.') or entry.name in ['node_modules', '__pycache__', '.git']:
                                continue
                            
                            child_folder = self._scan_folder(Path(entry.path), depth + 1)
                            folder_info.children.append(child_folder)
                            folder_info.folder_count += 1 + child_folder.folder_count
                            folder_info.file_count += child_folder.file_count
                            folder_info.total_size += child_folder.total_size
                            
                            # Merge category stats
                            self._merge_category_stats(folder_info, child_folder)
                    
                    except (PermissionError, OSError):
                        continue
        
        except (PermissionError, OSError) as e:
            pass
        
        # Determine dominant category
        folder_info.dominant_category = self._get_dominant_category(folder_info)
        folder_info.is_scanned = True
        
        # Emit signal for UI update (only for top-level folders)
        if depth <= 1:
            self.folder_scanned.emit(folder_info)
        
        return folder_info
    
    def _scan_file(self, entry: os.DirEntry) -> Optional[FileInfo]:
        """Extract file information from a directory entry."""
        try:
            stat_info = entry.stat(follow_symlinks=False)
            path = Path(entry.path)
            extension = path.suffix.lower()
            
            return FileInfo(
                path=path,
                name=entry.name,
                extension=extension,
                size=stat_info.st_size,
                category=get_category(extension),
                modified_time=stat_info.st_mtime
            )
        except (PermissionError, OSError):
            return None
    
    def _update_category_stats(self, folder: FolderInfo, file: FileInfo):
        """Update category statistics for a folder."""
        if file.category not in folder.categories:
            folder.categories[file.category] = CategoryStats(category=file.category)
        
        stats = folder.categories[file.category]
        stats.file_count += 1
        stats.total_size += file.size
        
        # Track extensions
        ext = file.extension or '(no extension)'
        stats.extensions[ext] = stats.extensions.get(ext, 0) + 1
        
        # Track largest files (keep top 10)
        stats.largest_files.append(file)
        stats.largest_files.sort(key=lambda f: f.size, reverse=True)
        stats.largest_files = stats.largest_files[:10]
    
    def _merge_category_stats(self, parent: FolderInfo, child: FolderInfo):
        """Merge child folder's category stats into parent."""
        for category, child_stats in child.categories.items():
            if category not in parent.categories:
                parent.categories[category] = CategoryStats(category=category)
            
            parent_stats = parent.categories[category]
            parent_stats.file_count += child_stats.file_count
            parent_stats.total_size += child_stats.total_size
            
            # Merge extensions
            for ext, count in child_stats.extensions.items():
                parent_stats.extensions[ext] = parent_stats.extensions.get(ext, 0) + count
            
            # Merge largest files
            parent_stats.largest_files.extend(child_stats.largest_files)
            parent_stats.largest_files.sort(key=lambda f: f.size, reverse=True)
            parent_stats.largest_files = parent_stats.largest_files[:10]
    
    def _get_dominant_category(self, folder: FolderInfo) -> Optional[FileCategory]:
        """Determine the dominant file category in a folder."""
        if not folder.categories:
            return None
        
        # Find category with largest total size
        return max(folder.categories.items(), key=lambda x: x[1].total_size)[0]
    
    def _build_result(self, root_folder: FolderInfo, scan_time: float) -> ScanResult:
        """Build the final scan result."""
        # Collect all largest files
        all_files = []
        self._collect_all_files(root_folder, all_files)
        all_files.sort(key=lambda f: f.size, reverse=True)
        
        return ScanResult(
            root_folder=root_folder,
            total_files=root_folder.file_count,
            total_folders=root_folder.folder_count,
            total_size=root_folder.total_size,
            categories=root_folder.categories,
            largest_files=all_files[:20],
            scan_time=scan_time
        )
    
    def _collect_all_files(self, folder: FolderInfo, files_list: list):
        """Recursively collect all files from folder tree."""
        files_list.extend(folder.files)
        for child in folder.children:
            self._collect_all_files(child, files_list)
