"""
In-Memory Cache Manager (Quality Goal Q05 - Feature 3)
Eliminates disk I/O bottlenecks by serving aggregate dashboard metrics directly from RAM.
"""

import time
import threading
from typing import Any, Optional, Dict, Tuple
from src.config import CACHE_DEFAULT_TTL_SECONDS, CACHE_MAX_ENTRIES, SLA_MAX_CACHE_READ_MS


class CacheEntry:
    """Represents a cached value with timestamp and TTL."""
    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl_seconds: float):
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class CacheManager:
    """Thread-safe TTL in-memory cache with microsecond hit benchmarking."""

    def __init__(self, default_ttl: float = CACHE_DEFAULT_TTL_SECONDS, max_entries: int = CACHE_MAX_ENTRIES):
        self._store: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
        self._max_entries = max_entries
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Tuple[Optional[Any], float, bool]:
        """
        Retrieve value from cache.
        Returns: (value, latency_ms, is_hit)
        """
        start = time.perf_counter()
        with self._lock:
            entry = self._store.get(key)
            if entry is not None:
                if not entry.is_expired():
                    self._hits += 1
                    latency_ms = (time.perf_counter() - start) * 1000.0
                    return entry.value, latency_ms, True
                else:
                    # Stale entry eviction
                    del self._store[key]

            self._misses += 1
            latency_ms = (time.perf_counter() - start) * 1000.0
            return None, latency_ms, False

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Store key-value with TTL, enforcing maximum capacity eviction."""
        effective_ttl = ttl if ttl is not None else self._default_ttl
        with self._lock:
            if len(self._store) >= self._max_entries and key not in self._store:
                # Evict oldest entry
                oldest_key = min(self._store.keys(), key=lambda k: self._store[k].expires_at)
                del self._store[oldest_key]
            self._store[key] = CacheEntry(value, effective_ttl)

    def invalidate(self, prefix: str = "") -> int:
        """Invalidate keys matching prefix or all if empty."""
        with self._lock:
            if not prefix:
                count = len(self._store)
                self._store.clear()
                return count
            keys_to_del = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_del:
                del self._store[k]
            return len(keys_to_del)

    def get_stats(self) -> Dict[str, Any]:
        """Return cache health metrics for TQM performance auditing."""
        with self._lock:
            total = self._hits + self._misses
            hit_ratio = (self._hits / total * 100.0) if total > 0 else 0.0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total,
                "hit_ratio_percent": round(hit_ratio, 2),
                "active_entries": len(self._store),
                "sla_limit_ms": SLA_MAX_CACHE_READ_MS
            }


# Global singleton instance for system-wide cache sharing
global_cache = CacheManager()
