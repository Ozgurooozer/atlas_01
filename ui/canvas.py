"""
Canvas Container.

Canvas is the root container for UI widgets.
It manages the UI hierarchy and provides widget finding.

Layer: 6 (UI)
Dependencies: ui.widget
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from ui.widget import Widget

if TYPE_CHECKING:
    pass


class Canvas(Widget):
    """
    Root container for UI widgets.

    A Canvas is the top-level widget that:
    - Has no parent (always root)
    - Manages size of the UI viewport
    - Provides widget finding utilities

    Example:
        >>> canvas = Canvas(name="MainCanvas")
        >>> canvas.set_size(1920, 1080)
        >>> canvas.add_widget(button)
        >>> canvas.tick(0.016)

    Attributes:
        Inherits all attributes from Widget
    """

    def __init__(self, name: str = None):
        """
        Create a new Canvas.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)

    @property
    def parent(self) -> None:
        """Canvas never has a parent. Always returns None."""
        return None

    @parent.setter
    def parent(self, value) -> None:
        """Setting parent on Canvas is ignored."""
        pass  # Canvas is always root

    def set_size(self, width: int, height: int) -> None:
        """
        Set the canvas size.

        Args:
            width: Width in pixels
            height: Height in pixels
        """
        self._width = max(0, int(width))
        self._height = max(0, int(height))

    def add_widget(self, widget: Widget) -> None:
        """
        Add a widget to this canvas.

        Args:
            widget: Widget to add
        """
        self.add_child(widget)

    def remove_widget(self, widget: Widget) -> None:
        """
        Remove a widget from this canvas.

        Args:
            widget: Widget to remove
        """
        self.remove_child(widget)

    def find_widget_by_name(self, name: str) -> Optional[Widget]:
        """
        Find a widget by name.

        Searches recursively through children.

        Args:
            name: Widget name to search for

        Returns:
            Widget with matching name, or None if not found
        """
        return self._find_by_name_recursive(name, self._children)

    def _find_by_name_recursive(self, name: str, widgets: List[Widget]) -> Optional[Widget]:
        """
        Recursively search for widget by name.

        Args:
            name: Widget name to search for
            widgets: List of widgets to search

        Returns:
            Widget with matching name, or None
        """
        for widget in widgets:
            if widget.name == name:
                return widget
            # Search children recursively
            found = self._find_by_name_recursive(name, widget.children)
            if found:
                return found
        return None

    def find_widget_at_point(self, x: int, y: int) -> Optional[Widget]:
        """
        Find the topmost widget at a point.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Widget at point, or None if no widget found
        """
        # Search in reverse order (topmost first)
        for widget in reversed(self._children):
            found = self._find_at_point_recursive(x, y, widget)
            if found:
                return found
        return None

    def _find_at_point_recursive(self, x: int, y: int, widget: Widget) -> Optional[Widget]:
        """
        Recursively find widget at point.

        Args:
            x: X coordinate (screen space)
            y: Y coordinate (screen space)
            widget: Widget to check

        Returns:
            Widget at point, or None
        """
        # Check if point is in widget bounds
        if not widget.contains_point(x, y):
            return None

        # Check children first (children are on top)
        for child in reversed(widget.children):
            found = self._find_at_point_recursive(x, y, child)
            if found:
                return found

        # If no child contains point, return this widget
        if widget.visible:
            return widget

        return None

    def clear(self) -> None:
        """
        Remove all widgets from this canvas.

        Clears all children and their parent references.
        """
        for child in self._children[:]:  # Copy to avoid modification during iteration
            self.remove_widget(child)

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}"
            f"(name={self._name!r}, "
            f"size=({self._width}x{self._height}), "
            f"children={len(self._children)})"
        )
