"""UI Label System - Text display widget.

Provides text rendering and display for UI.

Layer: 6 (UI)
Dependencies: core.color, core.vec
"""
from enum import Enum, auto
from typing import Tuple, Optional
from core.color import Color


class TextAlign(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class Label:
    """Text label widget.
    
    Displays text with customizable appearance.
    """
    
    def __init__(self, x: float = 0, y: float = 0, text: str = "",
                 font_size: int = 16):
        """Initialize label.
        
        Args:
            x: X position
            y: Y position
            text: Label text
            font_size: Font size in pixels
        """
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = Color(1, 1, 1)
        self.alignment = TextAlign.LEFT
        self.visible = True
        self.max_width: Optional[float] = None
        self._char_width = 0.6  # Approximation
    
    def set_text(self, text: str) -> None:
        """Set label text.
        
        Args:
            text: New text content
        """
        self.text = text
    
    def set_position(self, x: float, y: float) -> None:
        """Set label position.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
    
    def set_color(self, color: Color) -> None:
        """Set text color.
        
        Args:
            color: New color
        """
        self.color = color
    
    def set_font_size(self, size: int) -> None:
        """Set font size.
        
        Args:
            size: New font size
        """
        self.font_size = size
    
    def set_alignment(self, align: TextAlign) -> None:
        """Set text alignment.
        
        Args:
            align: New alignment
        """
        self.alignment = align
    
    def set_max_width(self, width: Optional[float]) -> None:
        """Set maximum width for text.
        
        Args:
            width: Max width or None for unlimited
        """
        self.max_width = width
    
    def get_size(self) -> Tuple[float, float]:
        """Calculate label size.
        
        Returns:
            (width, height) tuple
        """
        display_text = self.get_display_text()
        width = len(display_text) * self.font_size * self._char_width
        height = self.font_size * 1.2
        return (width, height)
    
    @property
    def is_truncated(self) -> bool:
        """Check if text is truncated."""
        if self.max_width is None:
            return False
        full_width = len(self.text) * self.font_size * self._char_width
        return full_width > self.max_width
    
    def get_display_text(self) -> str:
        """Get text to display (handles truncation).
        
        Returns:
            Display text
        """
        if self.max_width is None:
            return self.text
        
        max_chars = int(self.max_width / (self.font_size * self._char_width))
        
        if len(self.text) <= max_chars:
            return self.text
        
        # Truncate with ellipsis
        if max_chars > 3:
            return self.text[:max_chars - 3] + "..."
        return self.text[:max_chars]
    
    def show(self) -> None:
        """Show the label."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide the label."""
        self.visible = False
    
    def update(self, dt: float) -> None:
        """Update label (no-op for static label).
        
        Args:
            dt: Delta time
        """
        pass  # Static label, nothing to update
    
    def render(self, renderer) -> None:
        """Render the label.
        
        Args:
            renderer: Rendering context
        """
        if not self.visible:
            return
        
        # Rendering would be implemented by specific renderer
        pass
