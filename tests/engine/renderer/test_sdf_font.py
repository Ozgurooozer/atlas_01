"""Tests for SDF Font system.

Test-First Development for FAZ 12.5 - SDF Fonts
"""
import pytest
from engine.renderer.sdf_font import (
    SDFGlyph, SDFFont, SDFTextRenderer, SDFFontManager
)
from core.vec import Vec2
from core.color import Color


class TestSDFGlyph:
    """Test SDF glyph data structure."""
    
    def test_creation(self):
        """Test glyph creation."""
        sdf_data = [0.5] * (16 * 16)
        glyph = SDFGlyph(
            codepoint=65,  # 'A'
            width=20.0,
            height=24.0,
            offset_x=0.0,
            offset_y=4.0,
            advance=18.0,
            sdf_data=sdf_data,
            sdf_size=16
        )
        
        assert glyph.codepoint == 65
        assert glyph.width == 20.0
        assert glyph.height == 24.0
        assert glyph.sdf_size == 16
    
    def test_distance_sampling(self):
        """Test SDF distance sampling."""
        # Create gradient SDF data
        sdf_data = []
        for y in range(32):
            for x in range(32):
                # Distance from center
                dx = x - 16
                dy = y - 16
                dist = ((dx * dx + dy * dy) ** 0.5) / 16
                sdf_data.append(dist)
        
        glyph = SDFGlyph(65, 32, 32, 0, 0, 32, sdf_data, 32)
        
        # Center should be near 0 (inside glyph)
        center_dist = glyph.get_distance(0.5, 0.5)
        assert center_dist < 0.5
        
        # Corner should be near 1 (outside glyph)
        corner_dist = glyph.get_distance(0.0, 0.0)
        assert corner_dist > 0.5


class TestSDFFont:
    """Test SDF font system."""
    
    def test_initialization(self):
        """Test font initialization."""
        font = SDFFont(size=32.0, sdf_radius=8.0)
        
        assert font.size == 32.0
        assert font.sdf_radius == 8.0
        assert font.line_height > font.size
    
    def test_basic_glyphs_generated(self):
        """Test that basic ASCII glyphs are generated."""
        font = SDFFont(size=32.0)
        
        # Check common characters exist
        assert font.get_glyph(ord('A')) is not None
        assert font.get_glyph(ord('a')) is not None
        assert font.get_glyph(ord('0')) is not None
        assert font.get_glyph(ord(' ')) is not None
    
    def test_measure_text(self):
        """Test text measurement."""
        font = SDFFont(size=32.0)
        
        # Measure "Hello"
        width = font.measure_text("Hello")
        assert width > 0
        
        # Empty string
        empty_width = font.measure_text("")
        assert empty_width == 0.0
        
        # Single character
        single_width = font.measure_text("A")
        assert single_width > 0
    
    def test_measure_longer_text(self):
        """Test that longer text is wider."""
        font = SDFFont(size=32.0)
        
        short = font.measure_text("Hi")
        long = font.measure_text("Hello World")
        
        assert long > short


class TestSDFTextRenderer:
    """Test SDF text rendering."""
    
    def test_initialization(self):
        """Test renderer initialization."""
        font = SDFFont(size=32.0)
        renderer = SDFTextRenderer(font)
        
        assert renderer.font == font
        assert renderer.outline_width == 0.5
    
    def test_outline_settings(self):
        """Test outline customization."""
        font = SDFFont(size=32.0)
        renderer = SDFTextRenderer(font)
        
        renderer.outline_color = Color(1, 0, 0)
        renderer.outline_width = 1.0
        
        assert renderer.outline_color.r == 1.0
        assert renderer.outline_color.g == 0.0
        assert renderer.outline_color.b == 0.0
        assert renderer.outline_width == 1.0


class TestSDFFontManager:
    """Test font manager."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = SDFFontManager()
        
        assert manager.default_font is None
        assert len(manager.fonts) == 0
    
    def test_load_font(self):
        """Test font loading."""
        manager = SDFFontManager()
        
        font = manager.load_font("main", 32.0)
        
        assert font is not None
        assert font.size == 32.0
        assert manager.default_font == font
        assert "main" in manager.fonts
    
    def test_get_font(self):
        """Test font retrieval."""
        manager = SDFFontManager()
        
        font = manager.load_font("main", 32.0)
        retrieved = manager.get_font("main")
        
        assert retrieved == font
    
    def test_get_missing_font(self):
        """Test getting missing font returns default."""
        manager = SDFFontManager()
        default = manager.load_font("default", 32.0)
        
        missing = manager.get_font("nonexistent")
        assert missing == default
    
    def test_measure_with_font(self):
        """Test measuring text with specific font."""
        manager = SDFFontManager()
        manager.load_font("body", 16.0)
        
        width = manager.measure_text("Test", "body")
        assert width > 0
