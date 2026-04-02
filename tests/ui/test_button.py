"""Tests for UI Button.

class MockObject:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None

class MockCallback:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args = (args, kwargs)


Test-First Development for UI Button widget
"""
from ui.button import Button, ButtonState


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
        assert button.width == 100
        assert button.height == 30
        assert button.text == ""
        assert button.state == ButtonState.NORMAL
    
    def test_set_text(self):
        """Test setting text."""
        button = Button()
        button.set_text("New")
        
        assert button.text == "New"
    
    def test_set_position(self):
        """Test setting position."""
        button = Button()
        button.set_position(50, 60)
        
        assert button.x == 50
        assert button.y == 60
    
    def test_set_size(self):
        """Test setting size."""
        button = Button()
        button.set_size(200, 50)
        
        assert button.width == 200
        assert button.height == 50
    
    def test_on_click(self):
        """Test click callback."""
        button = Button()
        callback = MockCallback()
        
        button.on_click(callback)
        button.click()
        
        callback.assert_called_once()
    
    def test_click_disabled(self):
        """Test click when disabled."""
        button = Button()
        callback = MockCallback()
        button.on_click(callback)
        button.disable()
        
        button.click()
        
        callback.assert_not_called()
    
    def test_enable_disable(self):
        """Test enable and disable."""
        button = Button()
        
        button.disable()
        assert button.enabled is False
        assert button.state == ButtonState.DISABLED
        
        button.enable()
        assert button.enabled is True
        assert button.state == ButtonState.NORMAL
    
    def test_contains_point(self):
        """Test point inside button."""
        button = Button(x=10, y=20, width=100, height=30)
        
        assert button.contains(50, 30) is True
        assert button.contains(5, 5) is False
    
    def test_hover_enter_leave(self):
        """Test hover state changes."""
        button = Button()
        
        button.on_hover_enter()
        assert button.state == ButtonState.HOVER
        
        button.on_hover_leave()
        assert button.state == ButtonState.NORMAL
    
    def test_press_release(self):
        """Test press and release."""
        button = Button()
        
        button.on_press()
        assert button.state == ButtonState.PRESSED
        assert button.is_pressed is True
        
        button.on_release()
        assert button.state == ButtonState.HOVER
        assert button.is_pressed is False
    
    def test_multiple_callbacks(self):
        """Test multiple click callbacks."""
        button = Button()
        callback1 = MockObject()
        callback2 = MockObject()
        
        button.on_click(callback1)
        button.on_click(callback2)
        button.click()
        
        callback1.assert_called_once()
        callback2.assert_called_once()
    
    def test_remove_callback(self):
        """Test removing callback."""
        button = Button()
        callback = MockCallback()
        
        button.on_click(callback)
        button.off_click(callback)
        button.click()
        
        callback.assert_not_called()
    
    def test_update(self):
        """Test update does not crash."""
        button = Button()
        button.update(0.016)
    
    def test_visibility(self):
        """Test visibility toggle."""
        button = Button()
        
        assert button.visible is True
        
        button.hide()
        assert button.visible is False
        
        button.show()
        assert button.visible is True
