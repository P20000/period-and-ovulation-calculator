"""
Core package for Cycle & Mood Tracker.
Includes data models, scientific cycle calculator, storage manager, and platform detection.
"""

from .models import Profile, CycleRecord, DailyLog, PhaseInfo, PhaseType
from .calculator import CycleCalculator
from .storage import StorageManager
from .platform_detector import PlatformDetector, PlatformInfo

__all__ = [
    "Profile",
    "CycleRecord",
    "DailyLog",
    "PhaseInfo",
    "PhaseType",
    "CycleCalculator",
    "StorageManager",
    "PlatformDetector",
    "PlatformInfo",
]
