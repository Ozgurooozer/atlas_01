"""Settings System - Configuration management.

Provides persistent settings with categories for video, audio, input.

Layer: 2 (Engine)
Dependencies: core.color
"""
import json
import os
from typing import Dict, Any, Optional, Callable, Tuple, List
from dataclasses import dataclass, field, asdict


class SettingsCategory:
    """Category of related settings.
    
    Groups settings like video, audio, input.
    """
    
    def __init__(self, name: str):
        """Initialize category.
        
        Args:
            name: Category identifier
        """
        self.name = name
        self._settings: Dict[str, Any] = {}
    
    @property
    def settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary."""
        return dict(self._settings)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value.
        
        Args:
            key: Setting name
            value: Setting value
        """
        self._settings[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting name
            default: Default if not found
            
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if setting exists.
        
        Args:
            key: Setting name
            
        Returns:
            True if exists
        """
        return key in self._settings
    
    def remove(self, key: str) -> None:
        """Remove a setting.
        
        Args:
            key: Setting name
        """
        if key in self._settings:
            del self._settings[key]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return dict(self._settings)
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "SettingsCategory":
        """Create from dictionary.
        
        Args:
            name: Category name
            data: Settings data
            
        Returns:
            Settings category
        """
        cat = cls(name)
        cat._settings = dict(data)
        return cat


@dataclass
class VideoSettings:
    """Video configuration settings."""
    resolution: Tuple[int, int] = (1920, 1080)
    fullscreen: bool = False
    vsync: bool = True
    target_fps: int = 60
    brightness: float = 1.0
    gamma: float = 1.0
    show_fps: bool = False
    
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        self.fullscreen = not self.fullscreen


@dataclass
class AudioSettings:
    """Audio configuration settings."""
    master_volume: float = 1.0
    sfx_volume: float = 1.0
    music_volume: float = 0.8
    voice_volume: float = 1.0
    mute_on_focus_loss: bool = False
    
    def _clamp_volume(self, value: float) -> float:
        """Clamp volume to 0-1 range."""
        return max(0.0, min(1.0, value))
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Clamp volume values."""
        if "volume" in name and isinstance(value, (int, float)):
            value = self._clamp_volume(float(value))
        super().__setattr__(name, value)


@dataclass
class InputSettings:
    """Input configuration settings."""
    mouse_sensitivity: float = 1.0
    invert_y: bool = False
    invert_x: bool = False
    key_bindings: Dict[str, str] = field(default_factory=lambda: {
        "move_up": "w",
        "move_down": "s",
        "move_left": "a",
        "move_right": "d",
        "jump": "space",
        "attack": "mouse_left",
        "dodge": "shift",
        "interact": "e",
        "menu": "escape"
    })
    
    def rebind(self, action: str, key: str) -> None:
        """Rebind an action to a key.
        
        Args:
            action: Action name
            key: New key binding
        """
        self.key_bindings[action] = key
    
    def get_binding(self, action: str) -> Optional[str]:
        """Get key binding for action.
        
        Args:
            action: Action name
            
        Returns:
            Key binding or None
        """
        return self.key_bindings.get(action)


class Settings:
    """Central settings manager.
    
    Manages all game settings with persistence.
    """
    
    def __init__(self):
        """Initialize settings with defaults."""
        self._categories: Dict[str, SettingsCategory] = {}
        self._apply_callbacks: List[Callable[[], None]] = []
        
        # Create default categories
        self._video_cat = SettingsCategory("video")
        self._audio_cat = SettingsCategory("audio")
        self._input_cat = SettingsCategory("input")
        
        self._categories["video"] = self._video_cat
        self._categories["audio"] = self._audio_cat
        self._categories["input"] = self._input_cat
        
        # Initialize with defaults
        self._video = VideoSettings()
        self._audio = AudioSettings()
        self._input = InputSettings()
        
        self._sync_to_categories()
    
    def _sync_to_categories(self) -> None:
        """Sync dataclass settings to categories."""
        self._video_cat._settings = asdict(self._video)
        self._audio_cat._settings = asdict(self._audio)
        self._input_cat._settings = asdict(self._input)
    
    def _sync_from_categories(self) -> None:
        """Sync categories back to dataclasses."""
        self._video = VideoSettings(**self._video_cat._settings)
        self._audio = AudioSettings(**self._audio_cat._settings)
        self._input = InputSettings(**self._input_cat._settings)
    
    @property
    def video(self) -> VideoSettings:
        """Get video settings."""
        return self._video
    
    @property
    def audio(self) -> AudioSettings:
        """Get audio settings."""
        return self._audio
    
    @property
    def input(self) -> InputSettings:
        """Get input settings."""
        return self._input
    
    def get_category(self, name: str) -> SettingsCategory:
        """Get a settings category.
        
        Args:
            name: Category name
            
        Returns:
            Settings category
            
        Raises:
            KeyError: If category not found
        """
        if name not in self._categories:
            raise KeyError(f"Category '{name}' not found")
        return self._categories[name]
    
    def get_all_categories(self) -> Dict[str, SettingsCategory]:
        """Get all categories."""
        return dict(self._categories)
    
    def set(self, category: str, key: str, value: Any) -> None:
        """Set a setting value.
        
        Args:
            category: Category name
            key: Setting name
            value: Setting value
        """
        cat = self.get_category(category)
        cat.set(key, value)
        
        # Sync back to dataclass
        if category == "video":
            self._video = VideoSettings(**cat._settings)
        elif category == "audio":
            self._audio = AudioSettings(**cat._settings)
        elif category == "input":
            self._input = InputSettings(**cat._settings)
    
    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            category: Category name
            key: Setting name
            default: Default value
            
        Returns:
            Setting value or default
        """
        cat = self.get_category(category)
        return cat.get(key, default)
    
    def save(self, path: str) -> None:
        """Save settings to file.
        
        Args:
            path: File path
        """
        # Sync from dataclasses to categories before saving
        self._sync_to_categories()
        
        data = {
            name: cat.to_dict()
            for name, cat in self._categories.items()
        }
        
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str) -> None:
        """Load settings from file.
        
        Args:
            path: File path
        """
        if not os.path.exists(path):
            return
        
        with open(path, "r") as f:
            data = json.load(f)
        
        for name, cat_data in data.items():
            if name in self._categories:
                self._categories[name]._settings = cat_data
        
        self._sync_from_categories()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self._video = VideoSettings()
        self._audio = AudioSettings()
        self._input = InputSettings()
        self._sync_to_categories()
    
    def register_apply_callback(self, callback: Callable[[], None]) -> None:
        """Register callback for when settings are applied.
        
        Args:
            callback: Function to call
        """
        self._apply_callbacks.append(callback)
    
    def apply_changes(self) -> None:
        """Apply all pending changes and notify listeners."""
        for callback in self._apply_callbacks:
            callback()
