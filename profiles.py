import json
import os
import time
from pathlib import Path

class ProfileManager:
    def __init__(self, profile_dir="profiles"):
        """Initialize profile manager with a directory for storing profiles"""
        self.profile_dir = Path(profile_dir)
        self.profile_file = self.profile_dir / "profiles.json"
        self._ensure_profile_directory()

    def _ensure_profile_directory(self):
        """Create profile directory and initial profiles.json if they don't exist"""
        try:
            self.profile_dir.mkdir(exist_ok=True)
            if not self.profile_file.exists():
                self._save_profiles({})
        except Exception as e:
            raise RuntimeError(f"Failed to initialize profile directory: {str(e)}")

    def _load_profiles(self):
        """Load profiles from JSON file"""
        try:
            if self.profile_file.exists():
                with open(self.profile_file, 'r') as f:
                    return json.load(f)
            return {}
        except json.JSONDecodeError:
            # If file is corrupted, backup and create new
            backup_file = self.profile_file.with_suffix('.json.bak')
            self.profile_file.rename(backup_file)
            return {}
        except Exception as e:
            raise RuntimeError(f"Failed to load profiles: {str(e)}")

    def _save_profiles(self, profiles):
        """Save profiles to JSON file"""
        try:
            with open(self.profile_file, 'w') as f:
                json.dump(profiles, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to save profiles: {str(e)}")

    def create_profile(self, profile_id):
        """Create a new profile with default settings"""
        profiles = self._load_profiles()
        if profile_id in profiles:
            raise ValueError(f"Profile {profile_id} already exists")

        new_profile = {
            'created_at': time.time(),
            'last_used': time.time(),
            'cookies': [],
            'settings': {
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': None,
                'language': 'en-US',
                'timezone': 'UTC',
                'geolocation': None
            }
        }

        profiles[profile_id] = new_profile
        self._save_profiles(profiles)
        return new_profile

    def get_profile(self, profile_id):
        """Retrieve a profile by ID"""
        profiles = self._load_profiles()
        profile = profiles.get(profile_id)
        if not profile:
            # Create new profile if it doesn't exist
            profile = self.create_profile(profile_id)
        return profile

    def update_profile(self, profile_id, updates):
        """Update specific profile fields"""
        profiles = self._load_profiles()
        if profile_id not in profiles:
            raise ValueError(f"Profile {profile_id} does not exist")

        # Update nested dictionary
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d:
                    d[k] = update_dict(d[k], v)
                else:
                    d[k] = v
            return d

        profiles[profile_id] = update_dict(profiles[profile_id], updates)
        profiles[profile_id]['last_used'] = time.time()
        self._save_profiles(profiles)
        return profiles[profile_id]

    def update_cookies(self, profile_id, cookies):
        """Update cookies for a specific profile"""
        profiles = self._load_profiles()
        if profile_id not in profiles:
            raise ValueError(f"Profile {profile_id} does not exist")

        profiles[profile_id]['cookies'] = cookies
        profiles[profile_id]['last_used'] = time.time()
        self._save_profiles(profiles)

    def delete_profile(self, profile_id):
        """Delete a profile"""
        profiles = self._load_profiles()
        if profile_id in profiles:
            del profiles[profile_id]
            self._save_profiles(profiles)
            return True
        return False

    def list_profiles(self):
        """List all available profiles"""
        profiles = self._load_profiles()
        return list(profiles.keys())

    def cleanup_old_profiles(self, max_age_days=30):
        """Remove profiles that haven't been used in the specified number of days"""
        profiles = self._load_profiles()
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60

        profiles_to_keep = {}
        for profile_id, profile in profiles.items():
            if current_time - profile['last_used'] < max_age_seconds:
                profiles_to_keep[profile_id] = profile

        if len(profiles_to_keep) != len(profiles):
            self._save_profiles(profiles_to_keep)

        return len(profiles) - len(profiles_to_keep)  # Return number of deleted profiles