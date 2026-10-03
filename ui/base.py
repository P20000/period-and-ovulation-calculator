"""
Abstract base application interface for cross-platform UI backends.
"""

from abc import ABC, abstractmethod
from typing import Optional
from core.storage import StorageManager
from core.models import Profile


class BaseApp:
    """Interface that all platform GUI backends implement."""

    def __init__(self, storage_manager: Optional[StorageManager] = None):
        self.storage = storage_manager or StorageManager()
        self.profiles = self.storage.load_profiles()
        self.current_profile: Optional[Profile] = None
        
        # Set default active profile if available
        if self.profiles:
            first_key = next(iter(self.profiles))
            self.current_profile = self.profiles[first_key]

    def run(self) -> int:
        """Starts the application main loop."""
        raise NotImplementedError("Subclasses must implement run()")

    def set_current_profile(self, profile_name: str) -> bool:
        """Switches the active profile."""
        key = profile_name.lower()
        if key in self.profiles:
            self.current_profile = self.profiles[key]
            self.on_profile_changed(self.current_profile)
            return True
        return False

    def on_profile_changed(self, profile: Profile) -> None:
        """Hook called when the active profile changes."""
        pass
