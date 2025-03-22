import json
import os
from pathlib import Path

class FileCache:
    cache_dir = Path("app_cache")
    cache_dir.mkdir(exist_ok=True)

    @staticmethod
    def _get_cache_path(key):
        return FileCache.cache_dir / f"{key}.json"

    @staticmethod
    async def set(key, data):
        cache_file = FileCache._get_cache_path(key)
        with open(cache_file, 'w') as f:
            json.dump(data, f)

    @staticmethod
    async def get(key):
        cache_file = FileCache._get_cache_path(key)
        if not cache_file.exists():
            return None

        with open(cache_file, 'r') as f:
            return json.load(f)

    @staticmethod
    async def delete(key):
        cache_file = FileCache._get_cache_path(key)
        if cache_file.exists():
            os.remove(cache_file)

    @staticmethod
    async def clear():
        """Clear all cached data"""
        for cache_file in FileCache.cache_dir.glob("*.json"):
            os.remove(cache_file)
