"""Tests for UI Panel.

class MockObject:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None


Test-First Development for UI Panel widget
"""
from ui.panel import Panel
from ui.label import Label
from ui.button import Button
from core.color import Color


class TestPanel:
    """Test panel widget."""
    
    def test_initialization(self):
        """Test panel creation."""
        panel = Panel(x=10, y=20, width=300, height=200)
        
        assert panel.x == 10
        assert panel.y == 20
        assert panel.width == 300
        assert panel.height == 200
    
    def test_default_values(self):
        """Test panel defaults."""
        panel = Panel()
        
        assert panel.x == 0
        assert panel.y == 0
        assert panel.width == 100
        assert panel.height == 100
        assert panel.visible is True
    
    def test_add_child(self):
        """Test adding child widget."""
        panel = Panel()
        label = Label(text="Test")
        
        panel.add_child(label)
        
        assert label in panel.children
    
    def test_remove_child(self):
        """Test removing child widget."""
        panel = Panel()
        label = Label(text="Test")
        panel.add_child(label)
        
        panel.remove_child(label)
        
        assert label not in panel.children
    
    def test_add_multiple_children(self):
        """Test adding multiple children."""
        panel = Panel()
        label = Label()
        button = Button()
        
        panel.add_child(label)
        panel.add_child(button)
        
        assert len(panel.children) == 2
    
    def test_set_position(self):
        """Test setting position."""
        panel = Panel()
        panel.set_position(50, 60)
        
        assert panel.x == 50
        assert panel.y == 60
    
    def test_set_size(self):
        """Test setting size."""
        panel = Panel()
        panel.set_size(400, 300)
        
        assert panel.width == 400
        assert panel.height == 300
    
    def test_set_background_color(self):
        """Test setting background color."""
        panel = Panel()
        color = Color(0.2, 0.2, 0.2)
        panel.set_background_color(color)
        
        assert panel.background_color == color
    
    def test_set_border(self):
        """Test setting border."""
        panel = Panel()
        color = Color(1, 1, 1)
        panel.set_border(2, color)
        
        assert panel.border_width == 2
        assert panel.border_color.r == color.r
        assert panel.border_color.g == color.g
        assert panel.border_color.b == color.b
    
    def test_contains_point(self):
        """Test point inside panel."""
        panel = Panel(x=10, y=20, width=100, height=50)
        
        assert panel.contains(50, 40) is True
        assert panel.contains(5, 5) is False
    
    def test_get_absolute_position(self):
        """Test getting absolute position."""
        parent = Panel(x=10, y=10)
        child = Panel(x=20, y=30)
        parent.add_child(child)
        
        abs_x, abs_y = child.get_absolute_position()
        
        assert abs_x == 30  # 10 + 20
        assert abs_y == 40  # 10 + 30
    
    def test_clear_children(self):
        """Test clearing all children."""
        panel = Panel()
        panel.add_child(Label())
        panel.add_child(Button())
        
        panel.clear_children()
        
        assert len(panel.children) == 0
    
    def test_visibility_propagates(self):
        """Test visibility affects children."""
        panel = Panel()
        child = Label()
        panel.add_child(child)
        
        panel.hide()
        
        assert panel.visible is False
        assert child.visible is False
    
    def test_update_propagates(self):
        """Test update propagates to children."""
        panel = Panel()
        child = MockObject()
        panel.add_child(child)
        
        panel.update(0.016)
        
        child.update.assert_called_once_with(0.016)
    
    def test_set_padding(self):
        """Test setting padding."""
        panel = Panel()
        panel.set_padding(10, 20, 10, 20)
        
        assert panel.padding_top == 10
        assert panel.padding_right == 20
        assert panel.padding_bottom == 10
        assert panel.padding_left == 20
