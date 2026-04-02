"""
Tests for Input subsystem.

Input provides keyboard and mouse input handling.
Uses headless implementation for CI compatibility.

Layer: 2 (Engine)
"""

from engine.subsystem import ISubsystem
from engine.input.input_handler import IInput, InputHandler


class TestInputInterface:
    """Test that InputHandler implements IInput."""

    def test_input_is_subsystem(self):
        """InputHandler should be a ISubsystem."""
        assert issubclass(InputHandler, ISubsystem)

    def test_input_implements_iinput(self):
        """InputHandler should implement IInput interface."""
        assert issubclass(InputHandler, IInput)


class TestInputName:
    """Test Input name property."""

    def test_input_has_name(self):
        """Input should have name property."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "name")

    def test_input_name_is_input(self):
        """Input name should be 'input'."""
        input_handler = InputHandler()
        assert input_handler.name == "input"


class TestInputInitialization:
    """Test Input initialization."""

    def test_input_has_initialize(self):
        """Input should have initialize method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "initialize")
        assert callable(input_handler.initialize)

    def test_input_initialize_accepts_engine(self):
        """Input initialize should accept engine parameter."""
        input_handler = InputHandler()
        input_handler.initialize(None)  # Should not raise


class TestInputTick:
    """Test Input tick functionality."""

    def test_input_has_tick(self):
        """Input should have tick method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "tick")
        assert callable(input_handler.tick)

    def test_input_tick_updates_state(self):
        """Input tick should update input state."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        input_handler.tick(0.016)  # Should not raise


class TestInputShutdown:
    """Test Input shutdown."""

    def test_input_has_shutdown(self):
        """Input should have shutdown method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "shutdown")
        assert callable(input_handler.shutdown)


class TestKeyboardInput:
    """Test keyboard input functionality."""

    def test_input_has_is_key_pressed(self):
        """Input should have is_key_pressed method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "is_key_pressed")

    def test_is_key_pressed_returns_bool(self):
        """is_key_pressed should return bool."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        result = input_handler.is_key_pressed("a")
        assert isinstance(result, bool)

    def test_input_has_is_key_just_pressed(self):
        """Input should have is_key_just_pressed method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "is_key_just_pressed")

    def test_input_has_is_key_just_released(self):
        """Input should have is_key_just_released method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "is_key_just_released")

    def test_input_can_simulate_key_press(self):
        """Input can simulate key press for testing."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        input_handler.simulate_key_press("a")
        assert input_handler.is_key_pressed("a") is True

    def test_input_can_simulate_key_release(self):
        """Input can simulate key release for testing."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        input_handler.simulate_key_press("a")
        input_handler.simulate_key_release("a")
        assert input_handler.is_key_pressed("a") is False


class TestMouseInput:
    """Test mouse input functionality."""

    def test_input_has_get_mouse_position(self):
        """Input should have get_mouse_position method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "get_mouse_position")

    def test_get_mouse_position_returns_tuple(self):
        """get_mouse_position should return tuple."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        pos = input_handler.get_mouse_position()
        assert isinstance(pos, tuple)
        assert len(pos) == 2

    def test_input_has_is_mouse_button_pressed(self):
        """Input should have is_mouse_button_pressed method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "is_mouse_button_pressed")

    def test_input_can_simulate_mouse_position(self):
        """Input can simulate mouse position for testing."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        input_handler.simulate_mouse_position(100, 200)
        assert input_handler.get_mouse_position() == (100, 200)

    def test_input_can_simulate_mouse_button(self):
        """Input can simulate mouse button for testing."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        input_handler.simulate_mouse_button_press("left")
        assert input_handler.is_mouse_button_pressed("left") is True


class TestInputEnabled:
    """Test Input enabled state."""

    def test_input_has_enabled(self):
        """Input should have enabled property."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "enabled")

    def test_input_enabled_by_default(self):
        """Input should be enabled by default."""
        input_handler = InputHandler()
        assert input_handler.enabled is True


class TestInputClear:
    """Test Input clearing."""

    def test_input_has_clear(self):
        """Input should have clear method."""
        input_handler = InputHandler()
        assert hasattr(input_handler, "clear")
        assert callable(input_handler.clear)

    def test_clear_resets_key_states(self):
        """Clear should reset all key states."""
        input_handler = InputHandler()
        input_handler.initialize(None)
        input_handler.simulate_key_press("a")
        input_handler.clear()
        assert input_handler.is_key_pressed("a") is False
