"""
Fast search engine for files and folders with indexing.
"""
from typing import List, Optional, Callable
import fnmatch
import re
from dataclasses import dataclass

from models import FileInfo, FolderInfo


@dataclass
class SearchResult:
    """A search result."""
    name: str
    path: str
    size: str
    type: str
    is_folder: bool
    match_score: float


class FileSearchEngine:
    """Fast file search with caching and indexing."""
    
    def __init__(self):
        self._file_index: List[FileInfo] = []
        self._folder_index: List[FolderInfo] = []
        self._is_indexed = False
    
    def build_index(self, root_folder: FolderInfo):
        """Build search index from folder tree."""
        self._file_index.clear()
        self._folder_index.clear()
        
        def traverse(folder: FolderInfo):
            self._folder_index.append(folder)
            self._file_index.extend(folder.files)
            for child in folder.children:
                traverse(child)
        
        traverse(root_folder)
        self._is_indexed = True
    
    def search(self, 
               query: str, 
               file_types: Optional[List[str]] = None,
               min_size: Optional[int] = None,
               max_size: Optional[int] = None) -> List[SearchResult]:
        """
        Search files and folders.
        
        Supports:
        - Simple substring matching
        - Glob patterns (e.g., *.py, test_*)
        - Regex patterns (if query starts with /)
        """
        if not self._is_indexed or not query:
            return []
        
        results = []
        query_lower = query.lower()
        
        # Determine search mode
        is_regex = query.startswith('/') and len(query) > 1
        is_glob = '*' in query or '?' in query
        
        if is_regex:
            try:
                pattern = re.compile(query[1:], re.IGNORECASE)
                match_func = lambda s: bool(pattern.search(s))
            except re.error:
                match_func = lambda s: query_lower in s.lower()
        elif is_glob:
            match_func = lambda s: fnmatch.fnmatch(s.lower(), query_lower)
        else:
            match_func = lambda s: query_lower in s.lower()
        
        # Search files
        for file in self._file_index:
            # Apply filters
            if file_types and file.extension.lower() not in file_types:
                continue
            if min_size is not None and file.size < min_size:
                continue
            if max_size is not None and file.size > max_size:
                continue
            
            # Check name match
            if match_func(file.name):
                score = self._calculate_score(file.name, query)
                results.append(SearchResult(
                    name=file.name,
                    path=str(file.path),
                    size=file.size_formatted,
                    type=file.extension or "Unknown",
                    is_folder=False,
                    match_score=score
                ))
        
        # Search folders
        for folder in self._folder_index:
            if match_func(folder.name):
                score = self._calculate_score(folder.name, query)
                results.append(SearchResult(
                    name=folder.name,
                    path=str(folder.path),
                    size=folder.size_formatted,
                    type="Folder",
                    is_folder=True,
                    match_score=score
                ))
        
        # Sort by match score
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results[:100]  # Limit results
    
    def _calculate_score(self, name: str, query: str) -> float:
        """Calculate match score for ranking."""
        name_lower = name.lower()
        query_lower = query.lower()
        
        score = 0.0
        
        # Exact match gets highest score
        if name_lower == query_lower:
            score = 1.0
        # Starts with query
        elif name_lower.startswith(query_lower):
            score = 0.8
        # Contains query as word
        elif f" {query_lower}" in name_lower or f"_{query_lower}" in name_lower:
            score = 0.6
        # Contains query
        elif query_lower in name_lower:
            score = 0.4
        
        # Boost shorter names (more specific matches)
        score += max(0, (50 - len(name)) / 100)
        
        return score
    
    def find_duplicates(self) -> List[List[FileInfo]]:
        """Find duplicate files by size and name."""
        if not self._is_indexed:
            return []
        
        # Group by size first (fast)
        size_groups: dict = {}
        for file in self._file_index:
            key = (file.size, file.name.lower())
            if key not in size_groups:
                size_groups[key] = []
            size_groups[key].append(file)
        
        # Return groups with duplicates
        return [files for files in size_groups.values() if len(files) > 1]
    
    def find_large_files(self, threshold_mb: int = 100) -> List[FileInfo]:
        """Find files larger than threshold."""
        if not self._is_indexed:
            return []
        
        threshold_bytes = threshold_mb * 1024 * 1024
        return [f for f in self._file_index if f.size > threshold_bytes]
    
    def find_old_files(self, days: int = 365) -> List[FileInfo]:
        """Find files not modified in the last N days."""
        if not self._is_indexed:
            return []
        
        import time
        cutoff = time.time() - (days * 24 * 3600)
        return [f for f in self._file_index if f.modified_time < cutoff]
    
    def clear(self):
        """Clear the index."""
        self._file_index.clear()
        self._folder_index.clear()
        self._is_indexed = False
