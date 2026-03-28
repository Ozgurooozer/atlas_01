"""
Input Subsystem.

Provides keyboard and mouse input handling.
Uses pyglet input in production, simulated input for testing.

Layer: 2 (Engine)
Dependencies: engine.subsystem
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Optional, Set, Tuple, TYPE_CHECKING

from engine.subsystem import ISubsystem

if TYPE_CHECKING:
    from engine.engine import Engine


class IInput(ISubsystem):
    """
    Interface for input subsystems.

    Extends ISubsystem with input-specific methods.
    """

    @abstractmethod
    def is_key_pressed(self, key: str) -> bool:
        """Check if key is currently pressed."""
        pass

    @abstractmethod
    def is_key_just_pressed(self, key: str) -> bool:
        """Check if key was just pressed this frame."""
        pass

    @abstractmethod
    def is_key_just_released(self, key: str) -> bool:
        """Check if key was just released this frame."""
        pass

    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        pass

    @abstractmethod
    def is_mouse_button_pressed(self, button: str) -> bool:
        """Check if mouse button is pressed."""
        pass


class InputHandler(IInput):
    """
    Input handler implementation.

    Provides keyboard and mouse input handling:
    - Key state tracking (pressed, just pressed, just released)
    - Mouse position and button tracking
    - Simulation methods for testing

    Example:
        >>> input_handler = InputHandler()
        >>> input_handler.initialize(engine)
        >>> if input_handler.is_key_pressed("a"):
        ...     player.move_left()
        >>> x, y = input_handler.get_mouse_position()

    Attributes:
        enabled: Whether input is active
    """

    def __init__(self):
        """Create a new InputHandler."""
        self._enabled: bool = True
        self._keys_pressed: Set[str] = set()
        self._keys_just_pressed: Set[str] = set()
        self._keys_just_released: Set[str] = set()
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._mouse_buttons_pressed: Set[str] = set()

    @property
    def name(self) -> str:
        """Get subsystem name."""
        return "input"

    @property
    def enabled(self) -> bool:
        """Get whether input is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether input is enabled."""
        self._enabled = value

    def initialize(self, engine: Optional["Engine"]) -> None:
        """
        Initialize the input handler.

        Args:
            engine: Reference to the Engine (can be None for testing)
        """
        pass

    def tick(self, dt: float) -> None:
        """
        Update input state.

        Clears just_pressed and just_released sets each frame.

        Args:
            dt: Delta time in seconds
        """
        if not self._enabled:
            return

        # Clear frame-specific states
        self._keys_just_pressed.clear()
        self._keys_just_released.clear()

    def shutdown(self) -> None:
        """Clean up input resources."""
        self._keys_pressed.clear()
        self._keys_just_pressed.clear()
        self._keys_just_released.clear()
        self._mouse_buttons_pressed.clear()

    def is_key_pressed(self, key: str) -> bool:
        """
        Check if key is currently pressed.

        Args:
            key: Key name (e.g., "a", "space", "up")

        Returns:
            True if key is pressed
        """
        return key.lower() in self._keys_pressed

    def is_key_just_pressed(self, key: str) -> bool:
        """
        Check if key was just pressed this frame.

        Args:
            key: Key name

        Returns:
            True if key was just pressed
        """
        return key.lower() in self._keys_just_pressed

    def is_key_just_released(self, key: str) -> bool:
        """
        Check if key was just released this frame.

        Args:
            key: Key name

        Returns:
            True if key was just released
        """
        return key.lower() in self._keys_just_released

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.

        Returns:
            (x, y) tuple of mouse position
        """
        return self._mouse_position

    def is_mouse_button_pressed(self, button: str) -> bool:
        """
        Check if mouse button is pressed.

        Args:
            button: Button name ("left", "right", "middle")

        Returns:
            True if button is pressed
        """
        return button.lower() in self._mouse_buttons_pressed

    # Simulation methods for testing
    def simulate_key_press(self, key: str) -> None:
        """
        Simulate a key press (for testing).

        Args:
            key: Key name
        """
        key = key.lower()
        if key not in self._keys_pressed:
            self._keys_pressed.add(key)
            self._keys_just_pressed.add(key)

    def simulate_key_release(self, key: str) -> None:
        """
        Simulate a key release (for testing).

        Args:
            key: Key name
        """
        key = key.lower()
        if key in self._keys_pressed:
            self._keys_pressed.remove(key)
            self._keys_just_released.add(key)

    def simulate_mouse_position(self, x: int, y: int) -> None:
        """
        Simulate mouse position (for testing).

        Args:
            x: X position
            y: Y position
        """
        self._mouse_position = (x, y)

    def simulate_mouse_button_press(self, button: str) -> None:
        """
        Simulate mouse button press (for testing).

        Args:
            button: Button name
        """
        self._mouse_buttons_pressed.add(button.lower())

    def simulate_mouse_button_release(self, button: str) -> None:
        """
        Simulate mouse button release (for testing).

        Args:
            button: Button name
        """
        button = button.lower()
        if button in self._mouse_buttons_pressed:
            self._mouse_buttons_pressed.remove(button)

    def clear(self) -> None:
        """Clear all input states."""
        self._keys_pressed.clear()
        self._keys_just_pressed.clear()
        self._keys_just_released.clear()
        self._mouse_buttons_pressed.clear()
