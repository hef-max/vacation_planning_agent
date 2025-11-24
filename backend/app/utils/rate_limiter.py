"""
Rate Limiter untuk Gemini API
Menangani rate limiting dan automatic retry dengan exponential backoff
"""
import time
import functools
from typing import Callable, Any
from app.utils.logger import logger


class RateLimiter:
    """Simple rate limiter with exponential backoff"""
    
    def __init__(self, max_retries: int = 5, base_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.last_request_time = 0
        self.min_interval = 1.0  # Minimum 1 second between requests
    
    def wait_if_needed(self):
        """Wait if we're making requests too quickly"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def with_retry(self, func: Callable) -> Callable:
        """Decorator to add retry logic with exponential backoff"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(self.max_retries):
                try:
                    # Wait before making request
                    self.wait_if_needed()
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Success - reset backoff
                    return result
                    
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Check if it's a rate limit error
                    if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
                        if attempt < self.max_retries - 1:
                            # Calculate exponential backoff
                            delay = self.base_delay * (2 ** attempt)
                            logger.warning(
                                f"Rate limit hit (attempt {attempt + 1}/{self.max_retries}). "
                                f"Retrying in {delay:.1f}s..."
                            )
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"Rate limit exceeded after {self.max_retries} attempts")
                            raise
                    else:
                        # Non-rate-limit error, raise immediately
                        raise
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper


# Global rate limiter instance
_rate_limiter = RateLimiter(max_retries=5, base_delay=2.0)


def with_rate_limit(func: Callable) -> Callable:
    """Decorator to apply rate limiting to a function"""
    return _rate_limiter.with_retry(func)


# Rate limit presets for different tiers
class RateLimitPresets:
    """Predefined rate limit configurations"""
    
    FREE_TIER = {
        "max_retries": 5,
        "base_delay": 2.0,
        "min_interval": 1.0,
        "requests_per_minute": 15
    }
    
    PAID_TIER = {
        "max_retries": 3,
        "base_delay": 1.0,
        "min_interval": 0.1,
        "requests_per_minute": 60
    }
    
    @staticmethod
    def get_limiter(tier: str = "free") -> RateLimiter:
        """Get a rate limiter configured for the specified tier"""
        if tier.lower() == "paid":
            config = RateLimitPresets.PAID_TIER
        else:
            config = RateLimitPresets.FREE_TIER
        
        limiter = RateLimiter(
            max_retries=config["max_retries"],
            base_delay=config["base_delay"]
        )
        limiter.min_interval = config["min_interval"]
        return limiter