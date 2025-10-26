import time
from typing import Any, Dict, Optional, Tuple

class TTLCache:
    """Simple in-memory TTL cache (process-local)."""
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 512):
        self.ttl = ttl_seconds
        self.max = max_size
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        ts, val = item
        if (time.time() - ts) > self.ttl:
            # expired
            self._store.pop(key, None)
            return None
        return val

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max:
            # naive eviction (oldest)
            oldest_key = min(self._store.keys(), key=lambda k: self._store[k][0])
            self._store.pop(oldest_key, None)
        self._store[key] = (time.time(), value)


def make_key(*parts: Any) -> str:
    return "|".join(str(p) for p in parts)

try:
    import requests_cache  # type: ignore
except Exception:
    requests_cache = None


def install_http_cache(cache_name: str = "http_cache", expire_seconds: int = 86400) -> None:
    """Install requests-cache globally if available."""
    if requests_cache is None:
        return
    try:
        requests_cache.install_cache(cache_name, expire_after=expire_seconds)
    except Exception:
        # best-effort; ignore failures
        pass
