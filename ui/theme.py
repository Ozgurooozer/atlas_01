"""UI Theme System - Styling and theming.

Provides color schemes and styling for UI components.

Layer: 6 (UI)
Dependencies: core.color
"""
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from core.color import Color


@dataclass
class ColorScheme:
    """Color scheme for UI theming.
    
    Defines a complete set of colors for UI styling.
    """
    primary: Color = field(default_factory=lambda: Color(0.3, 0.5, 0.8))
    secondary: Color = field(default_factory=lambda: Color(0.5, 0.3, 0.8))
    background: Color = field(default_factory=lambda: Color(0.15, 0.15, 0.15))
    surface: Color = field(default_factory=lambda: Color(0.2, 0.2, 0.2))
    text: Color = field(default_factory=lambda: Color(1, 1, 1))
    text_secondary: Color = field(default_factory=lambda: Color(0.7, 0.7, 0.7))
    accent: Color = field(default_factory=lambda: Color(1, 0.6, 0.2))
    error: Color = field(default_factory=lambda: Color(0.9, 0.2, 0.2))
    success: Color = field(default_factory=lambda: Color(0.2, 0.8, 0.3))
    warning: Color = field(default_factory=lambda: Color(1, 0.8, 0.2))
    
    @classmethod
    def dark(cls) -> "ColorScheme":
        """Create dark color scheme."""
        return cls(
            background=Color(0.1, 0.1, 0.1),
            surface=Color(0.15, 0.15, 0.15),
            text=Color(1, 1, 1),
            text_secondary=Color(0.7, 0.7, 0.7)
        )
    
    @classmethod
    def light(cls) -> "ColorScheme":
        """Create light color scheme."""
        return cls(
            primary=Color(0.2, 0.4, 0.7),
            background=Color(0.95, 0.95, 0.95),
            surface=Color(1, 1, 1),
            text=Color(0.1, 0.1, 0.1),
            text_secondary=Color(0.4, 0.4, 0.4)
        )


class Theme:
    """UI theme with colors and styling.
    
    Defines visual appearance for UI components.
    """
    
    def __init__(self, name: str = "default"):
        """Initialize theme.
        
        Args:
            name: Theme identifier
        """
        self.name = name
        self.colors = ColorScheme()
        self.font_family: str = "sans-serif"
        self.base_font_size: int = 16
        
        # Custom colors beyond default scheme
        self._custom_colors: Dict[str, Color] = {}
        
        # Font size scale factors
        self._font_scales = {
            "tiny": 0.625,
            "small": 0.75,
            "normal": 1.0,
            "large": 1.25,
            "xlarge": 1.5,
            "huge": 2.0
        }
    
    def set_font_family(self, family: str) -> None:
        """Set font family.
        
        Args:
            family: Font family name
        """
        self.font_family = family
    
    def set_base_font_size(self, size: int) -> None:
        """Set base font size.
        
        Args:
            size: Base font size in pixels
        """
        self.base_font_size = size
    
    def get_color(self, name: str) -> Optional[Color]:
        """Get color by name.
        
        Args:
            name: Color name
            
        Returns:
            Color or None if not found
        """
        # Check custom colors first
        if name in self._custom_colors:
            return self._custom_colors[name]
        
        # Check scheme colors
        return getattr(self.colors, name, None)
    
    def set_color(self, name: str, color: Color) -> None:
        """Set custom color.
        
        Args:
            name: Color name
            color: Color value
        """
        if hasattr(self.colors, name):
            setattr(self.colors, name, color)
        else:
            self._custom_colors[name] = color
    
    def get_font_size(self, scale: str = "normal") -> int:
        """Get font size for scale.
        
        Args:
            scale: Size scale name
            
        Returns:
            Font size in pixels
        """
        factor = self._font_scales.get(scale, 1.0)
        return int(self.base_font_size * factor)
    
    def set_font_scale(self, scale: str, factor: float) -> None:
        """Set font scale factor.
        
        Args:
            scale: Scale name
            factor: Scale factor
        """
        self._font_scales[scale] = factor


class ThemeManager:
    """Central theme management.
    
    Manages multiple themes and provides global access to current theme.
    """
    
    def __init__(self):
        """Initialize theme manager."""
        self._themes: Dict[str, Theme] = {}
        self._current: Theme = Theme("default")
        
        # Register default theme
        self.register(self._current)
    
    @property
    def themes(self) -> Dict[str, Theme]:
        """Get all registered themes."""
        return dict(self._themes)
    
    @property
    def current_theme(self) -> Theme:
        """Get current theme."""
        return self._current
    
    def register(self, theme: Theme) -> None:
        """Register a theme.
        
        Args:
            theme: Theme to register
        """
        self._themes[theme.name] = theme
    
    def set_theme(self, name: str) -> None:
        """Set current theme.
        
        Args:
            name: Theme name
            
        Raises:
            KeyError: If theme not found
        """
        if name not in self._themes:
            raise KeyError(f"Theme '{name}' not found")
        self._current = self._themes[name]
    
    def get_color(self, name: str) -> Optional[Color]:
        """Get color from current theme.
        
        Args:
            name: Color name
            
        Returns:
            Color or None
        """
        return self._current.get_color(name)
    
    def get_font_size(self, scale: str = "normal") -> int:
        """Get font size from current theme.
        
        Args:
            scale: Size scale
            
        Returns:
            Font size in pixels
        """
        return self._current.get_font_size(scale)
    
    def create_dark_theme(self, name: str) -> Theme:
        """Create and register dark theme.
        
        Args:
            name: Theme name
            
        Returns:
            Created theme
        """
        theme = Theme(name)
        theme.colors = ColorScheme.dark()
        self.register(theme)
        return theme
    
    def create_light_theme(self, name: str) -> Theme:
        """Create and register light theme.
        
        Args:
            name: Theme name
            
        Returns:
            Created theme
        """
        theme = Theme(name)
        theme.colors = ColorScheme.light()
        self.register(theme)
        return theme
    
    def apply_to(self, widget: Any) -> None:
        """Apply current theme to widget.
        
        Args:
            widget: Widget to style
        """
        if hasattr(widget, 'update_style'):
            widget.update_style(self._current)
        elif hasattr(widget, 'theme_applied'):
            widget.theme_applied = True
