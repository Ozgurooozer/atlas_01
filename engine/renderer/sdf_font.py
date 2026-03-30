"""SDF (Signed Distance Field) Font System.

Provides high-quality, scalable text rendering for 2.5D games.

Layer: 2 (Engine)
Dependencies: core.vec, core.color
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.vec import Vec2
from core.color import Color


@dataclass
class SDFGlyph:
    """Single SDF glyph data."""
    
    codepoint: int
    width: float
    height: float
    offset_x: float
    offset_y: float
    advance: float
    sdf_data: List[float]  # Distance field values
    sdf_size: int = 32
    
    def get_distance(self, u: float, v: float) -> float:
        """Sample SDF at normalized UV coordinates."""
        x = int(u * (self.sdf_size - 1))
        y = int(v * (self.sdf_size - 1))
        idx = y * self.sdf_size + x
        if 0 <= idx < len(self.sdf_data):
            return self.sdf_data[idx]
        return 1.0


class SDFFont:
    """SDF Font for high-quality text rendering."""
    
    def __init__(self, size: float = 32.0, sdf_radius: float = 8.0):
        """Initialize SDF font.
        
        Args:
            size: Base font size in pixels
            sdf_radius: SDF sampling radius for edge detection
        """
        self.size = size
        self.sdf_radius = sdf_radius
        self.glyphs: Dict[int, SDFGlyph] = {}
        self.line_height = size * 1.2
        self.kerning: Dict[Tuple[int, int], float] = {}
        
        # Generate basic ASCII glyphs
        self._generate_basic_glyphs()
    
    def _generate_basic_glyphs(self) -> None:
        """Generate basic ASCII glyph data."""
        # Simplified: create placeholder SDF data for ASCII 32-126
        for cp in range(32, 127):
            # Create fake SDF data (solid block for now)
            sdf = [0.5] * (32 * 32)  # Neutral distance field
            
            glyph = SDFGlyph(
                codepoint=cp,
                width=0.6 * self.size,
                height=0.8 * self.size,
                offset_x=0.0,
                offset_y=0.0,
                advance=0.6 * self.size,
                sdf_data=sdf,
                sdf_size=32
            )
            self.glyphs[cp] = glyph
    
    def get_glyph(self, codepoint: int) -> Optional[SDFGlyph]:
        """Get glyph for codepoint."""
        return self.glyphs.get(codepoint)
    
    def get_kerning(self, left: int, right: int) -> float:
        """Get kerning between two glyphs."""
        return self.kerning.get((left, right), 0.0)
    
    def measure_text(self, text: str) -> float:
        """Measure text width in pixels."""
        width = 0.0
        prev_cp = None
        
        for char in text:
            cp = ord(char)
            glyph = self.get_glyph(cp)
            
            if glyph:
                # Add kerning
                if prev_cp is not None:
                    width += self.get_kerning(prev_cp, cp)
                
                # Add advance (except last character)
                width += glyph.advance
                prev_cp = cp
        
        return width


class SDFTextRenderer:
    """Renders SDF text with effects."""
    
    def __init__(self, font: SDFFont):
        """Initialize text renderer.
        
        Args:
            font: SDF font to use
        """
        self.font = font
        self.outline_color = Color(0, 0, 0)
        self.outline_width = 0.5
        self.shadow_offset = Vec2(2, 2)
        self.shadow_color = Color(0, 0, 0, 0.5)
    
    def render_character(self, position: Vec2, glyph: SDFGlyph, 
                         color: Color, scale: float = 1.0) -> None:
        """Render single character at position.
        
        Args:
            position: Screen position
            glyph: Character glyph
            color: Text color
            scale: Size scale factor
        """
        # Simplified: Just render bounding box for now
        # Real implementation would use shader with SDF texture
        size = glyph.advance * scale
        
        # This would be replaced with actual SDF shader rendering
        pass
    
    def render_text(self, text: str, position: Vec2, 
                    color: Color, scale: float = 1.0,
                    alignment: str = 'left') -> None:
        """Render text string.
        
        Args:
            text: Text to render
            position: Screen position (top-left or center based on alignment)
            color: Text color
            scale: Size scale
            alignment: 'left', 'center', or 'right'
        """
        # Calculate start position based on alignment
        text_width = self.font.measure_text(text) * scale
        
        if alignment == 'center':
            x = position.x - text_width / 2
        elif alignment == 'right':
            x = position.x - text_width
        else:  # left
            x = position.x
        
        y = position.y
        
        # Render each character
        prev_cp = None
        for char in text:
            cp = ord(char)
            glyph = self.font.get_glyph(cp)
            
            if glyph:
                # Apply kerning
                if prev_cp is not None:
                    x += self.font.get_kerning(prev_cp, cp) * scale
                
                # Render glyph
                self.render_character(Vec2(x, y), glyph, color, scale)
                
                x += glyph.advance * scale
                prev_cp = cp


class SDFFontManager:
    """Manages multiple SDF fonts."""
    
    def __init__(self):
        """Initialize font manager."""
        self.fonts: Dict[str, SDFFont] = {}
        self.default_font: Optional[SDFFont] = None
    
    def load_font(self, name: str, size: float = 32.0) -> SDFFont:
        """Load or create SDF font.
        
        Args:
            name: Font identifier
            size: Font size
            
        Returns:
            Loaded font
        """
        font = SDFFont(size)
        self.fonts[name] = font
        
        if self.default_font is None:
            self.default_font = font
        
        return font
    
    def get_font(self, name: str) -> Optional[SDFFont]:
        """Get font by name."""
        return self.fonts.get(name, self.default_font)
    
    def measure_text(self, text: str, font_name: str = '') -> float:
        """Measure text with specified font."""
        font = self.get_font(font_name)
        if font:
            return font.measure_text(text)
        return 0.0
