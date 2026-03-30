"""Tests for UI Layout.

Test-First Development for UI Layout system
"""
import pytest
from unittest.mock import MagicMock
from ui.layout import Layout, HorizontalLayout, VerticalLayout, GridLayout
from ui.label import Label
from ui.button import Button
from ui.panel import Panel


class ConcreteLayout(Layout):
    """Concrete layout for testing base class."""
    def arrange(self, container):
        pass


class TestLayout:
    """Test base layout."""
    
    def test_initialization(self):
        """Test layout creation."""
        layout = ConcreteLayout()
        assert layout.spacing == 0
        assert layout.padding == 0
    
    def test_set_spacing(self):
        """Test setting spacing."""
        layout = ConcreteLayout()
        layout.set_spacing(10)
        
        assert layout.spacing == 10
    
    def test_set_padding(self):
        """Test setting padding."""
        layout = ConcreteLayout()
        layout.set_padding(5)
        
        assert layout.padding == 5
    
    def test_arrange_raises(self):
        """Test base arrange raises NotImplementedError."""
        layout = ConcreteLayout()
        container = MagicMock()
        
        # Concrete implementation should not raise
        layout.arrange(container)  # Should pass without error


class TestHorizontalLayout:
    """Test horizontal layout."""
    
    def test_initialization(self):
        """Test horizontal layout creation."""
        layout = HorizontalLayout()
        assert layout.spacing == 0
    
    def test_arrange_single_child(self):
        """Test arranging single child."""
        layout = HorizontalLayout()
        panel = Panel(x=0, y=0, width=200, height=100)
        child = Label(x=0, y=0)
        panel.add_child(child)
        
        layout.arrange(panel)
        
        assert child.x == 0
        assert child.y == 0
    
    def test_arrange_multiple_children(self):
        """Test arranging multiple children horizontally."""
        layout = HorizontalLayout(spacing=10)
        panel = Panel(x=0, y=0, width=400, height=100)
        child1 = Label(x=0, y=0, text="A")
        child2 = Label(x=0, y=0, text="B")
        panel.add_child(child1)
        panel.add_child(child2)
        
        layout.arrange(panel)
        
        assert child1.x == 0
        assert child2.x > child1.x  # Second child to the right
    
    def test_arrange_with_padding(self):
        """Test arranging with padding."""
        layout = HorizontalLayout(padding=20)
        panel = Panel(x=0, y=0, width=400, height=100)
        child = Label()
        panel.add_child(child)
        
        layout.arrange(panel)
        
        assert child.x == 20  # Padded from left


class TestVerticalLayout:
    """Test vertical layout."""
    
    def test_initialization(self):
        """Test vertical layout creation."""
        layout = VerticalLayout()
        assert layout.spacing == 0
    
    def test_arrange_multiple_children(self):
        """Test arranging children vertically."""
        layout = VerticalLayout(spacing=10)
        panel = Panel(x=0, y=0, width=200, height=300)
        child1 = Label(x=0, y=0, text="A")
        child2 = Label(x=0, y=0, text="B")
        panel.add_child(child1)
        panel.add_child(child2)
        
        layout.arrange(panel)
        
        assert child1.y == 0
        assert child2.y > child1.y  # Second child below
    
    def test_arrange_with_padding(self):
        """Test arranging with padding."""
        layout = VerticalLayout(padding=15)
        panel = Panel(x=0, y=0, width=200, height=300)
        child = Label()
        panel.add_child(child)
        
        layout.arrange(panel)
        
        assert child.y == 15  # Padded from top


class TestGridLayout:
    """Test grid layout."""
    
    def test_initialization(self):
        """Test grid layout creation."""
        layout = GridLayout(columns=3, rows=2)
        
        assert layout.columns == 3
        assert layout.rows == 2
    
    def test_arrange_grid(self):
        """Test arranging in grid."""
        layout = GridLayout(columns=2, rows=2, spacing=5)
        panel = Panel(x=0, y=0, width=200, height=200)
        
        children = [Label() for _ in range(4)]
        for child in children:
            panel.add_child(child)
        
        layout.arrange(panel)
        
        # First row
        assert children[0].y == children[1].y  # Same row
        assert children[0].x < children[1].x  # Second column to right
        
        # Second row below first
        assert children[2].y > children[0].y
    
    def test_arrange_with_cell_size(self):
        """Test arranging with fixed cell size."""
        layout = GridLayout(columns=2, rows=1, cell_width=50, cell_height=30)
        panel = Panel(x=0, y=0, width=200, height=100)
        child1 = Label()
        child2 = Label()
        panel.add_child(child1)
        panel.add_child(child2)
        
        layout.arrange(panel)
        
        assert child2.x - child1.x == 50  # Cell width spacing
