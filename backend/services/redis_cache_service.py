"""
STEP 9.5: REDIS CACHE SERVICE (Python Async Port)
High-Performance Distributed Caching & Invalidation Layer
SIH 2026 - APIx Project
"""

import json
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Union

# Ensure backend root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RedisCacheService")


class RedisCacheService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.host = cfg.get("host") or os.getenv("REDIS_HOST", "localhost")
        self.port = int(cfg.get("port") or os.getenv("REDIS_PORT", 6379))
        self.db = int(cfg.get("db") or os.getenv("REDIS_DB", 0))
        self.password = cfg.get("password") or os.getenv("REDIS_PASSWORD", None)

        self.client: Any = None
        self.is_connected: bool = False
        self._memory_fallback: Dict[str, Any] = {}

        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }

    async def connect(self) -> Any:
        """Connect to Redis server asynchronously with in-memory fallback."""
        if self.is_connected and self.client is not None:
            logger.info("✅ Redis already connected")
            return self.client

        if redis is None:
            logger.warning("⚠️ 'redis' package not installed. Operating in in-memory fallback mode.")
            self.is_connected = False
            return None

        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0
            )
            await self.client.ping()
            self.is_connected = True
            logger.info(f"✅ Redis connected successfully on {self.host}:{self.port}/{self.db}")
            return self.client
        except Exception as err:
            logger.warning(f"⚠️ Redis connection unavailable ({err}). Using fallback cache.")
            self.is_connected = False
            self.stats["errors"] += 1
            return None

    async def disconnect(self) -> None:
        """Disconnect and close Redis connection pool."""
        if self.client and self.is_connected:
            await self.client.aclose()
            self.is_connected = False
            logger.info("✅ Redis disconnected")

    # ============ CORE PRIMITIVES ============

    async def set(self, key: str, value: Any, expiration_seconds: Optional[int] = 3600) -> bool:
        """Serialize and cache a value with optional TTL."""
        try:
            serialized = json.dumps(value, default=str)
            if self.is_connected and self.client is not None:
                if expiration_seconds:
                    await self.client.setex(key, expiration_seconds, serialized)
                else:
                    await self.client.set(key, serialized)
            else:
                self._memory_fallback[key] = serialized

            self.stats["sets"] += 1
            return True
        except Exception as err:
            logger.error(f"Error setting cache for key '{key}': {err}")
            self.stats["errors"] += 1
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve and deserialize a cached value."""
        try:
            val_str = None
            if self.is_connected and self.client is not None:
                val_str = await self.client.get(key)
            else:
                val_str = self._memory_fallback.get(key)

            if val_str is None:
                self.stats["misses"] += 1
                return None

            self.stats["hits"] += 1
            return json.loads(val_str)
        except Exception as err:
            logger.error(f"Error getting cache for key '{key}': {err}")
            self.stats["errors"] += 1
            return None

    async def delete(self, key: str) -> bool:
        """Delete a single key from cache."""
        try:
            if self.is_connected and self.client is not None:
                await self.client.delete(key)
            else:
                self._memory_fallback.pop(key, None)

            self.stats["deletes"] += 1
            return True
        except Exception as err:
            logger.error(f"Error deleting cache key '{key}': {err}")
            self.stats["errors"] += 1
            return False

    # ============ DOMAIN-SPECIFIC CACHE METHODS ============

    async def cache_index_data(self, date_str: str, index_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache computed APIx Laspeyres index payload."""
        return await self.set(f"apix:index:{date_str}", index_data, ttl)

    async def get_cached_index_data(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached APIx daily index payload."""
        return await self.get(f"apix:index:{date_str}")

    async def cache_route_data(self, route: str, data: Any, ttl: int = 7200) -> bool:
        """Cache DGCA basket route statistics (TTL: 2 hours)."""
        return await self.set(f"apix:route:{route.upper()}", data, ttl)

    async def get_cached_route_data(self, route: str) -> Optional[Any]:
        """Retrieve cached DGCA route telemetry."""
        return await self.get(f"apix:route:{route.upper()}")

    async def cache_fare_stats(self, route: str, advance_window: str, stats: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache lead-time fare elasticity metrics."""
        return await self.set(f"apix:stats:{route.upper()}:{advance_window}", stats, ttl)

    async def get_cached_fare_stats(self, route: str, advance_window: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached lead-time fare elasticity metrics."""
        return await self.get(f"apix:stats:{route.upper()}:{advance_window}")

    async def cache_dashboard_data(self, user_id: str, data: Any, ttl: int = 900) -> bool:
        """Cache aggregated dashboard view (15-minute TTL)."""
        return await self.set(f"apix:dashboard:{user_id}", data, ttl)

    async def get_cached_dashboard_data(self, user_id: str) -> Optional[Any]:
        """Retrieve cached aggregated dashboard view."""
        return await self.get(f"apix:dashboard:{user_id}")

    # ============ CACHE INVALIDATION PATTERNS ============

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a specific glob pattern."""
        deleted_count = 0
        try:
            if self.is_connected and self.client is not None:
                keys = await self.client.keys(pattern)
                if keys:
                    deleted_count = await self.client.delete(*keys)
            else:
                import fnmatch
                to_delete = [k for k in self._memory_fallback if fnmatch.fnmatch(k, pattern)]
                for k in to_delete:
                    del self._memory_fallback[k]
                deleted_count = len(to_delete)

            self.stats["deletes"] += deleted_count
            return deleted_count
        except Exception as err:
            logger.error(f"Error invalidating pattern '{pattern}': {err}")
            self.stats["errors"] += 1
            return 0

    async def invalidate_index_cache(self) -> int:
        return await self.invalidate_pattern("apix:index:*")

    async def invalidate_route_cache(self) -> int:
        return await self.invalidate_pattern("apix:route:*")

    async def invalidate_dashboard_cache(self) -> int:
        return await self.invalidate_pattern("apix:dashboard:*")

    async def invalidate_all(self) -> int:
        """Flush entire cache database."""
        try:
            if self.is_connected and self.client is not None:
                await self.client.flushdb()
            else:
                self._memory_fallback.clear()
            logger.info("✅ All cache invalidated")
            return -1
        except Exception as err:
            logger.error(f"Error invalidating all cache: {err}")
            self.stats["errors"] += 1
            return 0

    # ============ TELEMETRY & HEALTH CHECKS ============

    def get_stats(self) -> Dict[str, Any]:
        """Return cache hit-rate and performance counters."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = round((self.stats["hits"] / total * 100), 2) if total > 0 else 0.0
        return {
            **self.stats,
            "totalRequests": total,
            "hitRate": f"{hit_rate}%",
            "status": "connected" if self.is_connected else "in-memory-fallback",
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform ping verification for system probes."""
        if not self.is_connected or self.client is None:
            return {"status": "fallback", "connected": False}
        try:
            await self.client.ping()
            return {"status": "healthy", "connected": True}
        except Exception as err:
            return {"status": "unhealthy", "error": str(err)}

    def reset_stats(self) -> None:
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }


# Singleton Pattern
_cache_instance: Optional[RedisCacheService] = None


async def get_redis_cache(config: Optional[Dict[str, Any]] = None) -> RedisCacheService:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCacheService(config)
        await _cache_instance.connect()
    return _cache_instance


redis_cache = RedisCacheService()