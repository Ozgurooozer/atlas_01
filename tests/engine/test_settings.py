"""Tests for Settings System.

Test-First Development for Settings system
"""
import pytest
import os
import tempfile
from engine.settings import Settings, SettingsCategory, VideoSettings, AudioSettings, InputSettings


class TestSettingsCategory:
    """Test settings category."""
    
    def test_initialization(self):
        """Test category creation."""
        cat = SettingsCategory("video")
        assert cat.name == "video"
        assert cat.settings == {}
    
    def test_set_and_get(self):
        """Test setting and getting values."""
        cat = SettingsCategory("test")
        cat.set("resolution", (1920, 1080))
        
        assert cat.get("resolution") == (1920, 1080)
    
    def test_get_default(self):
        """Test getting with default."""
        cat = SettingsCategory("test")
        
        assert cat.get("missing", "default") == "default"
    
    def test_has_key(self):
        """Test checking key existence."""
        cat = SettingsCategory("test")
        cat.set("exists", True)
        
        assert cat.has("exists")
        assert not cat.has("missing")
    
    def test_remove(self):
        """Test removing setting."""
        cat = SettingsCategory("test")
        cat.set("temp", 123)
        cat.remove("temp")
        
        assert not cat.has("temp")
    
    def test_to_dict(self):
        """Test converting to dict."""
        cat = SettingsCategory("test")
        cat.set("a", 1)
        cat.set("b", "hello")
        
        d = cat.to_dict()
        assert d == {"a": 1, "b": "hello"}
    
    def test_from_dict(self):
        """Test loading from dict."""
        cat = SettingsCategory.from_dict("test", {"x": 10, "y": 20})
        
        assert cat.get("x") == 10
        assert cat.get("y") == 20


class TestVideoSettings:
    """Test video settings helper."""
    
    def test_initialization(self):
        """Test video settings creation."""
        vs = VideoSettings()
        
        assert vs.resolution == (1920, 1080)
        assert vs.fullscreen is False
        assert vs.vsync is True
    
    def test_set_resolution(self):
        """Test setting resolution."""
        vs = VideoSettings()
        vs.resolution = (1280, 720)
        
        assert vs.resolution == (1280, 720)
    
    def test_toggle_fullscreen(self):
        """Test toggling fullscreen."""
        vs = VideoSettings()
        vs.toggle_fullscreen()
        
        assert vs.fullscreen is True


class TestAudioSettings:
    """Test audio settings helper."""
    
    def test_initialization(self):
        """Test audio settings creation."""
        au = AudioSettings()
        
        assert au.master_volume == 1.0
        assert au.sfx_volume == 1.0
        assert au.music_volume == 0.8
    
    def test_set_master_volume(self):
        """Test setting master volume."""
        au = AudioSettings()
        au.master_volume = 0.5
        
        assert au.master_volume == 0.5
    
    def test_volume_clamped(self):
        """Test volume clamping."""
        au = AudioSettings()
        au.master_volume = 1.5
        
        assert au.master_volume == 1.0
        
        au.master_volume = -0.5
        assert au.master_volume == 0.0


class TestInputSettings:
    """Test input settings helper."""
    
    def test_initialization(self):
        """Test input settings creation."""
        inp = InputSettings()
        
        assert inp.mouse_sensitivity == 1.0
        assert inp.invert_y is False
    
    def test_rebind_key(self):
        """Test key rebinding."""
        inp = InputSettings()
        inp.rebind("jump", "space")
        
        assert inp.get_binding("jump") == "space"
    
    def test_get_binding_default(self):
        """Test getting default binding."""
        inp = InputSettings()
        
        assert inp.get_binding("move_up") == "w"


class TestSettings:
    """Test main settings manager."""
    
    def test_initialization(self):
        """Test settings creation."""
        s = Settings()
        
        assert s.video is not None
        assert s.audio is not None
        assert s.input is not None
    
    def test_get_category(self):
        """Test getting category."""
        s = Settings()
        cat = s.get_category("video")
        
        assert cat.name == "video"
    
    def test_get_category_missing(self):
        """Test getting missing category."""
        s = Settings()
        
        with pytest.raises(KeyError):
            s.get_category("missing")
    
    def test_set_and_get(self):
        """Test setting and getting."""
        s = Settings()
        s.set("video", "brightness", 0.8)
        
        assert s.get("video", "brightness") == 0.8
    
    def test_save_and_load(self):
        """Test saving and loading settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            
            # Save
            s1 = Settings()
            s1.set("video", "resolution", (1280, 720))
            s1.save(path)
            
            assert os.path.exists(path)
            
            # Load
            s2 = Settings()
            s2.load(path)
            
            assert s2.get("video", "resolution") == [1280, 720]
    
    def test_reset_to_defaults(self):
        """Test resetting to defaults."""
        s = Settings()
        s.set("video", "brightness", 0.5)
        s.reset_to_defaults()
        
        # Should be back to default
        # VideoSettings initializes with defaults
        assert s.video.brightness == 1.0
    
    def test_apply_changes_callback(self):
        """Test apply changes callback."""
        s = Settings()
        called = []
        
        def on_apply():
            called.append(True)
        
        s.register_apply_callback(on_apply)
        s.apply_changes()
        
        assert len(called) == 1
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        s = Settings()
        cats = s.get_all_categories()
        
        assert "video" in cats
        assert "audio" in cats
        assert "input" in cats
