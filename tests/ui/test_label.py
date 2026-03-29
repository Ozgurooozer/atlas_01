"""Tests for UI Label.

Test-First Development for UI Label widget
"""
import pytest
from ui.label import Label, TextAlign
from core.color import Color


class TestTextAlign:
    """Test text alignment enum."""
    
    def test_alignment_values(self):
        """Test alignment enum values."""
        assert TextAlign.LEFT.value == "left"
        assert TextAlign.CENTER.value == "center"
        assert TextAlign.RIGHT.value == "right"


class TestLabel:
    """Test label widget."""
    
    def test_initialization(self):
        """Test label creation."""
        label = Label(x=10, y=20, text="Hello")
        
        assert label.x == 10
        assert label.y == 20
        assert label.text == "Hello"
    
    def test_default_values(self):
        """Test label defaults."""
        label = Label()
        
        assert label.x == 0
        assert label.y == 0
        assert label.text == ""
        assert label.font_size == 16
    
    def test_set_text(self):
        """Test setting text."""
        label = Label()
        label.set_text("New text")
        
        assert label.text == "New text"
    
    def test_set_position(self):
        """Test setting position."""
        label = Label()
        label.set_position(100, 200)
        
        assert label.x == 100
        assert label.y == 200
    
    def test_set_color(self):
        """Test setting color."""
        label = Label()
        color = Color(1, 0, 0)
        label.set_color(color)
        
        assert label.color == color
    
    def test_set_font_size(self):
        """Test setting font size."""
        label = Label()
        label.set_font_size(24)
        
        assert label.font_size == 24
    
    def test_set_alignment(self):
        """Test setting alignment."""
        label = Label()
        label.set_alignment(TextAlign.CENTER)
        
        assert label.alignment == TextAlign.CENTER
    
    def test_get_size(self):
        """Test getting label size."""
        label = Label(text="Hello", font_size=16)
        width, height = label.get_size()
        
        assert width > 0
        assert height > 0
    
    def test_visibility(self):
        """Test visibility toggle."""
        label = Label()
        
        assert label.visible is True
        
        label.hide()
        assert label.visible is False
        
        label.show()
        assert label.visible is True
    
    def test_update_does_nothing(self):
        """Test update does nothing for static label."""
        label = Label()
        label.update(0.016)  # Should not raise
    
    def test_set_width_constraint(self):
        """Test setting width constraint."""
        label = Label(text="Long text here")
        label.set_max_width(50)
        
        assert label.max_width == 50
        assert label.is_truncated is True
    
    def test_get_display_text(self):
        """Test getting display text."""
        label = Label(text="Hello World")
        label.set_max_width(30)
        
        display = label.get_display_text()
        
        assert len(display) < len("Hello World")
