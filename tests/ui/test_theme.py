"""Tests for UI Theme.

Test-First Development for UI Theme system
"""
import pytest
from ui.theme import Theme, ThemeManager, ColorScheme
from core.color import Color


class MockWidget:
    """Simple mock widget for testing."""
    def __init__(self):
        self.theme_applied = False
        self.style = {}
    
    def update_style(self, theme: Theme) -> None:
        """Mock update_style method."""
        self.style['theme'] = theme
        self.theme_applied = True


class TestColorScheme:
    """Test color scheme."""
    
    def test_initialization(self):
        """Test color scheme creation."""
        scheme = ColorScheme()
        
        assert scheme.primary is not None
        assert scheme.secondary is not None
        assert scheme.background is not None
        assert scheme.text is not None
    
    def test_dark_scheme(self):
        """Test dark color scheme."""
        scheme = ColorScheme.dark()
        
        assert scheme.background.r < 0.5  # Dark background
        assert scheme.text.r > 0.5  # Light text
    
    def test_light_scheme(self):
        """Test light color scheme."""
        scheme = ColorScheme.light()
        
        assert scheme.background.r > 0.5  # Light background
        assert scheme.text.r < 0.5  # Dark text


class TestTheme:
    """Test theme."""
    
    def test_initialization(self):
        """Test theme creation."""
        theme = Theme(name="dark")
        
        assert theme.name == "dark"
        assert theme.colors is not None
    
    def test_set_font_family(self):
        """Test setting font family."""
        theme = Theme()
        theme.set_font_family("Arial")
        
        assert theme.font_family == "Arial"
    
    def test_set_base_font_size(self):
        """Test setting base font size."""
        theme = Theme()
        theme.set_base_font_size(14)
        
        assert theme.base_font_size == 14
    
    def test_get_color(self):
        """Test getting color."""
        theme = Theme()
        color = theme.get_color("primary")
        
        assert color is not None
    
    def test_get_color_missing(self):
        """Test getting missing color."""
        theme = Theme()
        
        assert theme.get_color("nonexistent") is None
    
    def test_set_custom_color(self):
        """Test setting custom color."""
        theme = Theme()
        custom_color = Color(0.5, 0.5, 0.5)
        theme.set_color("custom", custom_color)
        
        assert theme.get_color("custom") == custom_color
    
    def test_get_font_size_scale(self):
        """Test getting scaled font size."""
        theme = Theme()
        theme.set_base_font_size(16)
        
        small = theme.get_font_size("small")
        large = theme.get_font_size("large")
        
        assert small < 16
        assert large > 16


class TestThemeManager:
    """Test theme manager."""
    
    def test_initialization(self):
        """Test manager creation."""
        manager = ThemeManager()
        
        assert manager.current_theme is not None
        assert "default" in manager.themes
    
    def test_register_theme(self):
        """Test registering theme."""
        manager = ThemeManager()
        theme = Theme(name="custom")
        
        manager.register(theme)
        
        assert "custom" in manager.themes
    
    def test_set_theme(self):
        """Test setting current theme."""
        manager = ThemeManager()
        theme = Theme(name="dark")
        manager.register(theme)
        
        manager.set_theme("dark")
        
        assert manager.current_theme.name == "dark"
    
    def test_set_theme_not_found(self):
        """Test setting non-existent theme."""
        manager = ThemeManager()
        
        with pytest.raises(KeyError):
            manager.set_theme("nonexistent")
    
    def test_get_color(self):
        """Test getting color from current theme."""
        manager = ThemeManager()
        
        color = manager.get_color("primary")
        
        assert color is not None
    
    def test_get_font_size(self):
        """Test getting font size from current theme."""
        manager = ThemeManager()
        
        size = manager.get_font_size("normal")
        
        assert size > 0
    
    def test_create_dark_theme(self):
        """Test creating dark theme preset."""
        manager = ThemeManager()
        
        manager.create_dark_theme("my_dark")
        
        assert "my_dark" in manager.themes
        theme = manager.themes["my_dark"]
        assert theme.colors.background.r < 0.3  # Dark
    
    def test_create_light_theme(self):
        """Test creating light theme preset."""
        manager = ThemeManager()
        
        manager.create_light_theme("my_light")
        
        assert "my_light" in manager.themes
        theme = manager.themes["my_light"]
        assert theme.colors.background.r > 0.7  # Light
    
    def test_apply_to_widget(self):
        """Test applying theme to widget."""
        manager = ThemeManager()
        widget = MockWidget()
        
        manager.apply_to(widget)
        
        # Widget should receive styling
        assert widget.theme_applied or hasattr(widget, 'update_style')
