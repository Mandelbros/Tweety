import json
import os
from pathlib import Path

class FileCache:
    def __init__(self, cache_dir="app_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def _get_cache_path(self, key):
        return self.cache_dir / f"{key}.json"
        
    async def set(self, key, data):
        cache_file = self._get_cache_path(key)
        with open(cache_file, 'w') as f:
            json.dump(data, f)
            
    async def get(self, key):
        cache_file = self._get_cache_path(key)
        if not cache_file.exists():
            return None
            
        with open(cache_file, 'r') as f:
            return json.load(f)
            
    async def delete(self, key):
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            os.remove(cache_file)
            
    async def clear(self):
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.json"):
            os.remove(cache_file)