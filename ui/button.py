"""UI Button System - Interactive button widget.

Provides clickable button with state management.

Layer: 6 (UI)
Dependencies: core.color
"""
from enum import Enum
from typing import Callable, List
from core.color import Color


class ButtonState(Enum):
    """Button visual states."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"


Callback = Callable[[], None]


class Button:
    """Interactive button widget.
    
    Supports click callbacks and visual state changes.
    """
    
    def __init__(self, x: float = 0, y: float = 0, 
                 width: float = 100, height: float = 30,
                 text: str = ""):
        """Initialize button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button label
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        
        self._state = ButtonState.NORMAL
        self._enabled = True
        self.visible = True
        self._pressed = False
        
        # Colors for each state
        self.colors = {
            ButtonState.NORMAL: Color(0.3, 0.5, 0.8),
            ButtonState.HOVER: Color(0.4, 0.6, 0.9),
            ButtonState.PRESSED: Color(0.2, 0.4, 0.7),
            ButtonState.DISABLED: Color(0.5, 0.5, 0.5)
        }
        
        self._callbacks: List[Callback] = []
    
    @property
    def state(self) -> ButtonState:
        """Get current button state."""
        return self._state
    
    @property
    def enabled(self) -> bool:
        """Get enabled state."""
        return self._enabled
    
    @property
    def is_pressed(self) -> bool:
        """Check if button is currently pressed."""
        return self._pressed
    
    def set_text(self, text: str) -> None:
        """Set button text.
        
        Args:
            text: New button label
        """
        self.text = text
    
    def set_position(self, x: float, y: float) -> None:
        """Set button position.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
    
    def set_size(self, width: float, height: float) -> None:
        """Set button size.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
    
    def contains(self, x: float, y: float) -> bool:
        """Check if point is inside button.
        
        Args:
            x: Point X
            y: Point Y
            
        Returns:
            True if point inside button
        """
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)
    
    def on_click(self, callback: Callback) -> None:
        """Register click callback.
        
        Args:
            callback: Function to call on click
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def off_click(self, callback: Callback) -> None:
        """Unregister click callback.
        
        Args:
            callback: Function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def click(self) -> None:
        """Trigger button click."""
        if not self._enabled:
            return
        
        for callback in self._callbacks:
            try:
                callback()
            except Exception:
                pass
    
    def on_hover_enter(self) -> None:
        """Called when mouse enters button."""
        if self._enabled and not self._pressed:
            self._state = ButtonState.HOVER
    
    def on_hover_leave(self) -> None:
        """Called when mouse leaves button."""
        if self._enabled:
            self._state = ButtonState.NORMAL
            self._pressed = False
    
    def on_press(self) -> None:
        """Called when button is pressed."""
        if self._enabled:
            self._state = ButtonState.PRESSED
            self._pressed = True
    
    def on_release(self) -> None:
        """Called when button is released."""
        if self._enabled:
            if self._pressed:
                self.click()
            self._state = ButtonState.HOVER
            self._pressed = False
    
    def enable(self) -> None:
        """Enable button interaction."""
        self._enabled = True
        self._state = ButtonState.NORMAL
    
    def disable(self) -> None:
        """Disable button interaction."""
        self._enabled = False
        self._state = ButtonState.DISABLED
        self._pressed = False
    
    def show(self) -> None:
        """Show the button."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide the button."""
        self.visible = False
    
    def update(self, dt: float) -> None:
        """Update button state.
        
        Args:
            dt: Delta time
        """
        pass  # State is event-driven
    
    def get_color(self) -> Color:
        """Get color for current state."""
        return self.colors.get(self._state, self.colors[ButtonState.NORMAL])
    
    def render(self, renderer) -> None:
        """Render the button.
        
        Args:
            renderer: Rendering context
        """
        if not self.visible:
            return
        
        # Rendering would be implemented by specific renderer
        pass
