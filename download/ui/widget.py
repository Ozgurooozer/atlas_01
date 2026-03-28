"""
Widget Base Class.

Widget is the base class for all UI elements.
It provides position, size, visibility, and hierarchy.

Layer: 6 (UI)
Dependencies: core.object, core.reflection
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.object import Object
from core.reflection import reflect

if TYPE_CHECKING:
    pass


class Widget(Object):
    """
    Base class for all UI widgets.

    A Widget is a UI element with:
    - Position (x, y)
    - Size (width, height)
    - Visibility
    - Enabled state
    - Parent-child hierarchy

    Example:
        >>> widget = Widget(name="Button")
        >>> widget.x = 100
        >>> widget.y = 200
        >>> widget.width = 150
        >>> widget.height = 50
        >>> widget.tick(0.016)

    Attributes:
        x: X position
        y: Y position
        width: Widget width
        height: Widget height
        enabled: Whether the widget is interactive
        visible: Whether the widget is rendered
        parent: Parent widget
        children: List of child widgets
    """

    def __init__(self, name: str = None):
        """
        Create a new Widget.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._x: int = 0
        self._y: int = 0
        self._width: int = 100
        self._height: int = 100
        self._enabled: bool = True
        self._visible: bool = True
        self._parent: Optional["Widget"] = None
        self._children: List["Widget"] = []

    # Position properties
    @reflect("int", category="Layout", description="X position")
    def x(self) -> int:
        """Get X position."""
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        """Set X position."""
        self._x = int(value)

    @reflect("int", category="Layout", description="Y position")
    def y(self) -> int:
        """Get Y position."""
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        """Set Y position."""
        self._y = int(value)

    # Size properties
    @reflect("int", category="Layout", min=0, description="Width")
    def width(self) -> int:
        """Get width."""
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        """Set width."""
        self._width = max(0, int(value))

    @reflect("int", category="Layout", min=0, description="Height")
    def height(self) -> int:
        """Get height."""
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        """Set height."""
        self._height = max(0, int(value))

    # State properties
    @property
    def enabled(self) -> bool:
        """Get whether widget is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether widget is enabled."""
        self._enabled = value

    @property
    def visible(self) -> bool:
        """Get whether widget is visible."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set whether widget is visible."""
        self._visible = value

    # Hierarchy properties
    @property
    def parent(self) -> Optional["Widget"]:
        """Get parent widget."""
        return self._parent

    @parent.setter
    def parent(self, value: Optional["Widget"]) -> None:
        """Set parent widget."""
        self._parent = value

    @property
    def children(self) -> List["Widget"]:
        """Get list of child widgets."""
        return self._children

    # Hierarchy methods
    def add_child(self, child: "Widget") -> None:
        """
        Add a child widget.

        Sets the child's parent to this widget.

        Args:
            child: Widget to add as child
        """
        if child not in self._children:
            self._children.append(child)
            child._parent = self

    def remove_child(self, child: "Widget") -> None:
        """
        Remove a child widget.

        Clears the child's parent.

        Args:
            child: Widget to remove
        """
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    # Lifecycle hooks
    def on_tick(self, delta_time: float) -> None:
        """
        Called each frame.

        Override in subclasses to implement per-frame logic.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    def on_draw(self) -> None:
        """
        Called when the widget should be drawn.

        Override in subclasses to implement rendering.
        """
        pass

    # Main methods
    def tick(self, delta_time: float) -> None:
        """
        Update this widget for one frame.

        Calls on_tick if enabled, then ticks all children.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self._enabled:
            return

        self.on_tick(delta_time)

        for child in self._children:
            child.tick(delta_time)

    # Bounds checking
    def contains_point(self, x: int, y: int) -> bool:
        """
        Check if a point is inside this widget's bounds.

        Args:
            x: X coordinate to check
            y: Y coordinate to check

        Returns:
            True if point is inside widget bounds
        """
        return (
            self._x <= x < self._x + self._width
            and self._y <= y < self._y + self._height
        )

    # Serialization
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this Widget to a dictionary.

        Returns:
            Dictionary containing widget data
        """
        data = super().serialize()
        data["x"] = self._x
        data["y"] = self._y
        data["width"] = self._width
        data["height"] = self._height
        data["enabled"] = self._enabled
        data["visible"] = self._visible
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this Widget from a dictionary.

        Args:
            data: Dictionary containing widget data
        """
        super().deserialize(data)
        if "x" in data:
            self._x = int(data["x"])
        if "y" in data:
            self._y = int(data["y"])
        if "width" in data:
            self._width = max(0, int(data["width"]))
        if "height" in data:
            self._height = max(0, int(data["height"]))
        if "enabled" in data:
            self._enabled = data["enabled"]
        if "visible" in data:
            self._visible = data["visible"]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}"
            f"(name={self._name!r}, "
            f"pos=({self._x}, {self._y}), "
            f"size=({self._width}x{self._height}))"
        )
