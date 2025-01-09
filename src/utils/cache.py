from functools import wraps
import time
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired"""
        if key in self._cache:
            item = self._cache[key]
            if item['expiry'] > time.time():
                return item['value']
            else:
                del self._cache[key]
        return None
        
    def set(self, key: str, value: Any, timeout: int = 300) -> None:
        """Set value in cache with expiration"""
        self._cache[key] = {
            'value': value,
            'expiry': time.time() + timeout
        }
        
    def delete(self, key: str) -> None:
        """Remove item from cache"""
        if key in self._cache:
            del self._cache[key]
            
    def clear(self) -> None:
        """Clear all items from cache"""
        self._cache.clear()
        
    def has(self, key: str) -> bool:
        """Check if key exists in cache and hasn't expired"""
        return bool(self.get(key))
        
    def cleanup(self) -> None:
        """Remove expired items from cache"""
        now = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expiry'] <= now
        ]
        for key in expired_keys:
            del self._cache[key]
            
    def memoize(self, timeout: int = 300):
        """Decorator to memoize function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create a cache key from function name and arguments
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Check cache first
                result = self.get(key)
                if result is not None:
                    logger.debug(f"Cache hit for key: {key}")
                    return result
                    
                # If not in cache, execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(key, result, timeout)
                logger.debug(f"Cached result for key: {key}")
                
                return result
            return wrapper
        return decorator

# Create a global cache instance
cache = Cache()