"""Settings Menu UI - Interactive settings interface.

Provides visual controls for video, audio, and input settings.

Layer: 6 (UI)
Dependencies: ui.panel, ui.button, ui.label, engine.settings
"""
from typing import List, Dict, Callable, Any, Optional
from engine.settings import Settings


class SettingsSlider:
    """Slider control for numeric settings."""
    
    def __init__(self, label: str, min_val: float, max_val: float, default: float):
        """Initialize slider.
        
        Args:
            label: Display label
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
        """
        self.label = label
        self.min_value = min_val
        self.max_value = max_val
        self._value = default
        self.on_change: Optional[Callable[[float], None]] = None
    
    @property
    def value(self) -> float:
        """Get current value."""
        return self._value
    
    def set_value(self, val: float) -> None:
        """Set value with clamping.
        
        Args:
            val: New value
        """
        self._value = max(self.min_value, min(self.max_value, val))
        if self.on_change:
            self.on_change(self._value)


class SettingsToggle:
    """Toggle control for boolean settings."""
    
    def __init__(self, label: str, default: bool = False):
        """Initialize toggle.
        
        Args:
            label: Display label
            default: Default state
        """
        self.label = label
        self._value = default
        self.on_change: Optional[Callable[[bool], None]] = None
    
    @property
    def value(self) -> bool:
        """Get current state."""
        return self._value
    
    def toggle(self) -> None:
        """Toggle the value."""
        self._value = not self._value
        if self.on_change:
            self.on_change(self._value)


class SettingsDropdown:
    """Dropdown control for selection settings."""
    
    def __init__(self, label: str, options: List[str], default: str):
        """Initialize dropdown.
        
        Args:
            label: Display label
            options: Available options
            default: Default selection
        """
        self.label = label
        self.options = options
        if default not in options:
            raise ValueError(f"Default '{default}' not in options")
        self._value = default
        self.on_change: Optional[Callable[[str], None]] = None
    
    @property
    def value(self) -> str:
        """Get current selection."""
        return self._value
    
    def set_value(self, val: str) -> None:
        """Set selection.
        
        Args:
            val: Selected option
            
        Raises:
            ValueError: If option not available
        """
        if val not in self.options:
            raise ValueError(f"Invalid option '{val}'")
        self._value = val
        if self.on_change:
            self.on_change(self._value)


class SettingsMenu:
    """Main settings menu interface.
    
    Tabbed interface with video, audio, and input settings.
    """
    
    def __init__(self, settings: Settings):
        """Initialize settings menu.
        
        Args:
            settings: Settings manager instance
        """
        self.settings = settings
        self._visible = False
        self._current_tab = "video"
        self._tabs: Dict[str, List[Any]] = {}
        self._controls: Dict[str, List[Any]] = {}
        
        self.on_apply: Optional[Callable[[], None]] = None
        self.save_path: str = "settings.json"
    
    @property
    def visible(self) -> bool:
        """Get visibility state."""
        return self._visible
    
    @property
    def current_tab(self) -> str:
        """Get current tab."""
        return self._current_tab
    
    @property
    def tabs(self) -> List[str]:
        """Get available tabs."""
        return list(self._tabs.keys())
    
    def show(self) -> None:
        """Show the menu."""
        self._visible = True
    
    def hide(self) -> None:
        """Hide the menu."""
        self._visible = False
    
    def toggle(self) -> None:
        """Toggle visibility."""
        self._visible = not self._visible
    
    def add_control(self, tab: str, control: Any) -> None:
        """Add control to a tab.
        
        Args:
            tab: Tab name
            control: Control instance
        """
        if tab not in self._controls:
            self._controls[tab] = []
        self._controls[tab].append(control)
    
    def get_controls(self, tab: str) -> List[Any]:
        """Get controls for a tab.
        
        Args:
            tab: Tab name
            
        Returns:
            List of controls
        """
        return list(self._controls.get(tab, []))
    
    def create_video_tab(self) -> None:
        """Create video settings tab."""
        tab_name = "video"
        self._tabs[tab_name] = []
        self._controls[tab_name] = []
        
        # Resolution dropdown
        res = SettingsDropdown(
            "Resolution",
            ["1280x720", "1920x1080", "2560x1440", "3840x2160"],
            f"{self.settings.video.resolution[0]}x{self.settings.video.resolution[1]}"
        )
        res.on_change = self._on_resolution_change
        self.add_control(tab_name, res)
        
        # Fullscreen toggle
        fs = SettingsToggle("Fullscreen", self.settings.video.fullscreen)
        fs.on_change = self._on_fullscreen_change
        self.add_control(tab_name, fs)
        
        # VSync toggle
        vsync = SettingsToggle("VSync", self.settings.video.vsync)
        vsync.on_change = self._on_vsync_change
        self.add_control(tab_name, vsync)
        
        # FPS limit slider
        fps = SettingsSlider("Target FPS", 30, 240, float(self.settings.video.target_fps))
        fps.on_change = self._on_fps_change
        self.add_control(tab_name, fps)
        
        # Brightness slider
        bright = SettingsSlider("Brightness", 0.0, 2.0, self.settings.video.brightness)
        bright.on_change = self._on_brightness_change
        self.add_control(tab_name, bright)
        
        # Show FPS toggle
        show_fps = SettingsToggle("Show FPS", self.settings.video.show_fps)
        show_fps.on_change = self._on_show_fps_change
        self.add_control(tab_name, show_fps)
    
    def create_audio_tab(self) -> None:
        """Create audio settings tab."""
        tab_name = "audio"
        self._tabs[tab_name] = []
        self._controls[tab_name] = []
        
        # Master volume
        master = SettingsSlider("Master Volume", 0.0, 1.0, self.settings.audio.master_volume)
        master.on_change = lambda v: setattr(self.settings.audio, "master_volume", v)
        self.add_control(tab_name, master)
        
        # SFX volume
        sfx = SettingsSlider("SFX Volume", 0.0, 1.0, self.settings.audio.sfx_volume)
        sfx.on_change = lambda v: setattr(self.settings.audio, "sfx_volume", v)
        self.add_control(tab_name, sfx)
        
        # Music volume
        music = SettingsSlider("Music Volume", 0.0, 1.0, self.settings.audio.music_volume)
        music.on_change = lambda v: setattr(self.settings.audio, "music_volume", v)
        self.add_control(tab_name, music)
        
        # Mute on focus loss
        mute = SettingsToggle("Mute on Focus Loss", self.settings.audio.mute_on_focus_loss)
        mute.on_change = lambda v: setattr(self.settings.audio, "mute_on_focus_loss", v)
        self.add_control(tab_name, mute)
    
    def switch_tab(self, tab: str) -> None:
        """Switch to a tab.
        
        Args:
            tab: Tab name
        """
        if tab in self._tabs:
            self._current_tab = tab
    
    def apply_settings(self) -> None:
        """Apply all settings changes."""
        self.settings.apply_changes()
        if self.on_apply:
            self.on_apply()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings.reset_to_defaults()
        # Recreate tabs with new defaults
        self._tabs.clear()
        self._controls.clear()
        self.create_video_tab()
        self.create_audio_tab()
    
    def save_settings(self) -> None:
        """Save settings to file."""
        self.settings.save(self.save_path)
    
    def load_settings(self) -> None:
        """Load settings from file."""
        self.settings.load(self.save_path)
        # Update controls with loaded values
        self._tabs.clear()
        self._controls.clear()
        self.create_video_tab()
        self.create_audio_tab()
    
    # Video setting handlers
    def _on_resolution_change(self, val: str) -> None:
        """Handle resolution change."""
        w, h = val.split("x")
        self.settings.video.resolution = (int(w), int(h))
    
    def _on_fullscreen_change(self, val: bool) -> None:
        """Handle fullscreen change."""
        self.settings.video.fullscreen = val
    
    def _on_vsync_change(self, val: bool) -> None:
        """Handle vsync change."""
        self.settings.video.vsync = val
    
    def _on_fps_change(self, val: float) -> None:
        """Handle FPS change."""
        self.settings.video.target_fps = int(val)
    
    def _on_brightness_change(self, val: float) -> None:
        """Handle brightness change."""
        self.settings.video.brightness = val
    
    def _on_show_fps_change(self, val: bool) -> None:
        """Handle show FPS change."""
        self.settings.video.show_fps = val
