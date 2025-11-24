# app/routers/__init__.py
"""
API routers for the vacation planner.
"""
from . import plans
from . import bookings

__all__ = ["plans", "bookings"]