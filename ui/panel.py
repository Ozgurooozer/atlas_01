"""UI Panel System - Container widget.

Provides container for grouping and organizing UI elements.

Layer: 6 (UI)
Dependencies: core.color, ui.label, ui.button
"""
from typing import List, Any, Tuple, Optional
from core.color import Color


class Panel:
    """Container panel for UI widgets.
    
    Groups child widgets and provides styling options.
    """
    
    def __init__(self, x: float = 0, y: float = 0, 
                 width: float = 100, height: float = 100):
        """Initialize panel.
        
        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        
        self.children: List[Any] = []
        self._parent: Optional["Panel"] = None
        
        # Styling
        self.background_color = Color(0.15, 0.15, 0.15)
        self.border_color = Color(0.3, 0.3, 0.3)
        self.border_width = 1
        
        # Padding
        self.padding_top = 0
        self.padding_right = 0
        self.padding_bottom = 0
        self.padding_left = 0
    
    def add_child(self, child: Any) -> None:
        """Add child widget.
        
        Args:
            child: Widget to add
        """
        if child not in self.children:
            self.children.append(child)
            # Set parent reference if child is a panel
            if isinstance(child, Panel):
                child._parent = self
    
    def remove_child(self, child: Any) -> bool:
        """Remove child widget.
        
        Args:
            child: Widget to remove
            
        Returns:
            True if removed
        """
        if child in self.children:
            self.children.remove(child)
            if isinstance(child, Panel):
                child._parent = None
            return True
        return False
    
    def clear_children(self) -> None:
        """Remove all children."""
        for child in self.children:
            if isinstance(child, Panel):
                child._parent = None
        self.children.clear()
    
    def set_position(self, x: float, y: float) -> None:
        """Set panel position.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
    
    def set_size(self, width: float, height: float) -> None:
        """Set panel size.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
    
    def set_background_color(self, color: Color) -> None:
        """Set background color.
        
        Args:
            color: New background color
        """
        self.background_color = color
    
    def set_border(self, width: float, color: Color) -> None:
        """Set border.
        
        Args:
            width: Border width
            color: Border color
        """
        self.border_width = width
        self.border_color = color
    
    def set_padding(self, top: float, right: float, 
                    bottom: float, left: float) -> None:
        """Set padding.
        
        Args:
            top: Top padding
            right: Right padding
            bottom: Bottom padding
            left: Left padding
        """
        self.padding_top = top
        self.padding_right = right
        self.padding_bottom = bottom
        self.padding_left = left
    
    def contains(self, x: float, y: float) -> bool:
        """Check if point is inside panel.
        
        Args:
            x: Point X
            y: Point Y
            
        Returns:
            True if point inside
        """
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)
    
    def get_absolute_position(self) -> Tuple[float, float]:
        """Get absolute screen position.
        
        Returns:
            (x, y) absolute position
        """
        x, y = self.x, self.y
        parent = self._parent
        while parent:
            x += parent.x
            y += parent.y
            parent = parent._parent
        return (x, y)
    
    def show(self) -> None:
        """Show panel and children."""
        self.visible = True
        for child in self.children:
            if hasattr(child, 'visible'):
                child.visible = True
    
    def hide(self) -> None:
        """Hide panel and children."""
        self.visible = False
        for child in self.children:
            if hasattr(child, 'visible'):
                child.visible = False
    
    def update(self, dt: float) -> None:
        """Update panel and children.
        
        Args:
            dt: Delta time
        """
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(dt)
    
    def render(self, renderer) -> None:
        """Render panel and children.
        
        Args:
            renderer: Rendering context
        """
        if not self.visible:
            return
        
        # Render background
        # Render border
        # Render children
        pass
