import time
from functools import wraps

class LatencyMonitor:
    @staticmethod
    def measure_latency(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            return result, latency_ms
        return wrapper

    @staticmethod
    def measure_latency_async(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            return result, latency_ms
        return wrapper
