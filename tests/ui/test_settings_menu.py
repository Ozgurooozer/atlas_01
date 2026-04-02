"""Tests for Settings Menu UI.

Test-First Development for Settings Menu
"""
import pytest
from ui.settings_menu import SettingsMenu, SettingsSlider, SettingsToggle, SettingsDropdown
from engine.settings import Settings


class TestSettingsSlider:
    """Test settings slider control."""
    
    def test_initialization(self):
        """Test slider creation."""
        slider = SettingsSlider("Volume", 0.0, 1.0, 0.5)
        
        assert slider.label == "Volume"
        assert slider.min_value == 0.0
        assert slider.max_value == 1.0
        assert slider.value == 0.5
    
    def test_set_value(self):
        """Test setting value."""
        slider = SettingsSlider("Test", 0, 100, 50)
        slider.set_value(75)
        
        assert slider.value == 75
    
    def test_value_clamped(self):
        """Test value clamping."""
        slider = SettingsSlider("Test", 0, 100, 50)
        slider.set_value(150)
        
        assert slider.value == 100
    
    def test_on_change_callback(self):
        """Test change callback."""
        called = []
        slider = SettingsSlider("Test", 0, 100, 50)
        
        def on_change(val):
            called.append(val)
        
        slider.on_change = on_change
        slider.set_value(80)
        
        assert 80 in called


class TestSettingsToggle:
    """Test settings toggle control."""
    
    def test_initialization(self):
        """Test toggle creation."""
        toggle = SettingsToggle("Fullscreen", True)
        
        assert toggle.label == "Fullscreen"
        assert toggle.value is True
    
    def test_toggle(self):
        """Test toggling value."""
        toggle = SettingsToggle("Test", False)
        toggle.toggle()
        
        assert toggle.value is True
    
    def test_on_change_callback(self):
        """Test change callback."""
        called = []
        toggle = SettingsToggle("Test", False)
        
        def on_change(val):
            called.append(val)
        
        toggle.on_change = on_change
        toggle.toggle()
        
        assert True in called


class TestSettingsDropdown:
    """Test settings dropdown control."""
    
    def test_initialization(self):
        """Test dropdown creation."""
        options = ["Low", "Medium", "High"]
        dropdown = SettingsDropdown("Quality", options, "Medium")
        
        assert dropdown.label == "Quality"
        assert dropdown.options == options
        assert dropdown.value == "Medium"
    
    def test_set_value(self):
        """Test setting value."""
        dropdown = SettingsDropdown("Res", ["720p", "1080p"], "720p")
        dropdown.set_value("1080p")
        
        assert dropdown.value == "1080p"
    
    def test_invalid_value(self):
        """Test setting invalid value."""
        dropdown = SettingsDropdown("Test", ["A", "B"], "A")
        
        with pytest.raises(ValueError):
            dropdown.set_value("Invalid")


class TestSettingsMenu:
    """Test settings menu."""
    
    def test_initialization(self):
        """Test menu creation."""
        settings = Settings()
        menu = SettingsMenu(settings)
        
        assert menu.settings == settings
        assert menu.visible is False
    
    def test_show_hide(self):
        """Test show and hide."""
        settings = Settings()
        menu = SettingsMenu(settings)
        
        menu.show()
        assert menu.visible is True
        
        menu.hide()
        assert menu.visible is False
    
    def test_toggle(self):
        """Test toggle visibility."""
        settings = Settings()
        menu = SettingsMenu(settings)
        
        menu.toggle()
        assert menu.visible is True
        
        menu.toggle()
        assert menu.visible is False
    
    def test_add_control(self):
        """Test adding control."""
        settings = Settings()
        menu = SettingsMenu(settings)
        slider = SettingsSlider("Volume", 0, 1, 0.5)
        
        menu.add_control("audio", slider)
        
        assert len(menu.get_controls("audio")) == 1
    
    def test_create_video_tab(self):
        """Test creating video tab."""
        settings = Settings()
        menu = SettingsMenu(settings)
        
        menu.create_video_tab()
        
        assert "video" in menu.tabs
        assert len(menu.get_controls("video")) > 0
    
    def test_create_audio_tab(self):
        """Test creating audio tab."""
        settings = Settings()
        menu = SettingsMenu(settings)
        
        menu.create_audio_tab()
        
        assert "audio" in menu.tabs
        assert len(menu.get_controls("audio")) > 0
    
    def test_switch_tab(self):
        """Test switching tabs."""
        settings = Settings()
        menu = SettingsMenu(settings)
        menu.create_video_tab()
        menu.create_audio_tab()
        
        menu.switch_tab("audio")
        
        assert menu.current_tab == "audio"
    
    def test_apply_settings(self):
        """Test applying settings."""
        settings = Settings()
        menu = SettingsMenu(settings)
        
        called = []
        def on_apply():
            called.append(True)
        
        menu.on_apply = on_apply
        menu.apply_settings()
        
        assert len(called) == 1
    
    def test_reset_to_defaults(self):
        """Test reset to defaults."""
        settings = Settings()
        settings.video.brightness = 0.5
        menu = SettingsMenu(settings)
        
        menu.reset_to_defaults()
        
        assert settings.video.brightness == 1.0
    
    def test_save_settings(self):
        """Test save settings."""
        import tempfile
        import os
        
        settings = Settings()
        menu = SettingsMenu(settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            menu.save_path = path
            menu.save_settings()
            
            assert os.path.exists(path)
    
    def test_load_settings(self):
        """Test load settings."""
        import tempfile
        import os
        
        settings = Settings()
        settings.video.brightness = 0.3
        
        menu = SettingsMenu(settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            settings.save(path)
            
            # Reset
            settings.video.brightness = 1.0
            
            menu.save_path = path
            menu.load_settings()
            
            assert settings.video.brightness == 0.3
