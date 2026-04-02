"""Tests for UI Button.

Test-First Development for UI Button widget
"""
from ui.button import Button, ButtonState


class MockObject:
    """Simple mock for testing."""

    def __init__(self):
        self.call_count = 0
        self.call_args = None

    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            self.call_count += 1
            self.call_args = (args, kwargs)
            return None

        return mock_method


class MockCallback:
    """Simple mock for testing."""

    def __init__(self):
        self.call_count = 0
        self.call_args = None

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args = (args, kwargs)


class TestButtonState:
    """Test button state enum."""

    def test_state_values(self):
        """Test state enum values."""
        assert ButtonState.NORMAL.value == "normal"
        assert ButtonState.HOVER.value == "hover"
        assert ButtonState.PRESSED.value == "pressed"
        assert ButtonState.DISABLED.value == "disabled"


class TestButton:
    """Test button widget."""

    def test_initialization(self):
        """Test button creation."""
        button = Button(x=10, y=20, width=100, height=30, text="Click")

        assert button.x == 10
        assert button.y == 20
        assert button.width == 100
        assert button.height == 30
        assert button.text == "Click"

    def test_default_values(self):
        """Test button defaults."""
        button = Button()

        assert button.x == 0
        assert button.y == 0
        assert button.width == 80
        assert button.height == 24
        assert button.text == ""
        assert button.state == ButtonState.NORMAL

    def test_click_triggers_callback(self):
        """Test click triggers callback."""
        callback = MockCallback()
        button = Button(on_click=callback)

        button.click()

        assert callback.call_count == 1

    def test_hover_changes_state(self):
        """Test hover changes state to HOVER."""
        button = Button()
        button.enabled = True

        button.on_hover_enter()

        assert button.state == ButtonState.HOVER

    def test_unhover_changes_state(self):
        """Test unhover changes state to NORMAL."""
        button = Button()
        button.state = ButtonState.HOVER

        button.on_hover_exit()

        assert button.state == ButtonState.NORMAL

    def test_press_changes_state(self):
        """Test press changes state to PRESSED."""
        button = Button()
        button.enabled = True

        button.on_press()

        assert button.state == ButtonState.PRESSED

    def test_release_changes_state(self):
        """Test release changes state to NORMAL."""
        button = Button()
        button.state = ButtonState.PRESSED

        button.on_release()

        assert button.state == ButtonState.NORMAL

    def test_disabled_ignores_interaction(self):
        """Test disabled button ignores interaction."""
        callback = MockCallback()
        button = Button(enabled=False, on_click=callback)

        button.click()

        assert callback.call_count == 0
        assert button.state == ButtonState.DISABLED
