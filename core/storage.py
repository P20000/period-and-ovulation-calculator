"""
Storage manager responsible for persisting and loading user profiles and logs.
Implements atomic writes, automated backups, and schema evolution.
"""

import json
import os
import shutil
import tempfile
from datetime import date
from typing import Dict, List, Optional
from .models import Profile, DailyLog, CycleRecord


DEFAULT_DATA_FILE = "girlfriend_data.json"


class StorageManager:
    """Encapsulates data persistence operations with safety guarantees."""

    def __init__(self, file_path: str = DEFAULT_DATA_FILE):
        self.file_path = os.path.abspath(file_path)
        self.backup_path = f"{self.file_path}.bak"

    def load_profiles(self) -> Dict[str, Profile]:
        """Loads and parses all profiles from storage."""
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            profiles_dict: Dict[str, Profile] = {}
            raw_profiles = data.get("profiles", {})

            for name, pdata in raw_profiles.items():
                if isinstance(pdata, dict):
                    # Ensure name is consistent
                    if "name" not in pdata:
                        pdata["name"] = name
                    profiles_dict[name.lower()] = Profile.from_dict(pdata)

            return profiles_dict

        except (json.JSONDecodeError, OSError) as e:
            # Attempt recovery from backup if main file is corrupted
            if os.path.exists(self.backup_path):
                try:
                    with open(self.backup_path, "r", encoding="utf-8") as bf:
                        data = json.load(bf)
                    profiles_dict = {}
                    for name, pdata in data.get("profiles", {}).items():
                        if isinstance(pdata, dict):
                            profiles_dict[name.lower()] = Profile.from_dict(pdata)
                    return profiles_dict
                except Exception:
                    pass
            print(f"[StorageManager] Error loading data: {e}")
            return {}

    def save_profiles(self, profiles: Dict[str, Profile]) -> bool:
        """Saves profiles to disk using atomic write and maintains a backup."""
        data_to_save = {
            "version": "2.0",
            "profiles": {name: prof.to_dict() for name, prof in profiles.items()}
        }

        # Step 1: Create backup of current file if it exists
        if os.path.exists(self.file_path):
            try:
                shutil.copy2(self.file_path, self.backup_path)
            except OSError as e:
                print(f"[StorageManager] Failed to create backup: {e}")

        # Step 2: Atomic write using temporary file in same directory
        dir_name = os.path.dirname(self.file_path) or "."
        try:
            with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
                json.dump(data_to_save, tf, indent=4, ensure_ascii=False)
                temp_name = tf.name

            # Replace original file atomically
            os.replace(temp_name, self.file_path)
            return True
        except Exception as e:
            print(f"[StorageManager] Error saving profiles: {e}")
            if 'temp_name' in locals() and os.path.exists(temp_name):
                try:
                    os.remove(temp_name)
                except OSError:
                    pass
            return False

    def save_profile(self, profile: Profile) -> bool:
        """Upserts a single profile."""
        profiles = self.load_profiles()
        profiles[profile.name.lower()] = profile
        return self.save_profiles(profiles)

    def delete_profile(self, profile_name: str) -> bool:
        """Deletes a profile by name."""
        profiles = self.load_profiles()
        key = profile_name.lower()
        if key in profiles:
            del profiles[key]
            return self.save_profiles(profiles)
        return False

    def log_daily_entry(self, profile_name: str, daily_log: DailyLog) -> bool:
        """Appends or updates a daily log entry for a specific profile."""
        profiles = self.load_profiles()
        key = profile_name.lower()
        if key in profiles:
            date_str = daily_log.log_date.isoformat()
            profiles[key].daily_logs[date_str] = daily_log
            return self.save_profiles(profiles)
        return False
