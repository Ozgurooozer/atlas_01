"""Tests for spritesheet system.

Layer: 2 (Engine)
"""

from __future__ import annotations


from engine.renderer.texture import Texture, UVRegion


class TestSpritesheet:
    """Test Spritesheet class."""

    def test_spritesheet_creation(self):
        """Test basic spritesheet creation."""
        from engine.renderer.spritesheet import Spritesheet

        texture = Texture(128, 128)
        sheet = Spritesheet(texture)

        assert sheet.texture is texture
        assert len(sheet) == 0

    def test_add_frame(self):
        """Test adding frames to spritesheet."""
        from engine.renderer.spritesheet import Spritesheet

        texture = Texture(128, 128)
        sheet = Spritesheet(texture)

        uv = UVRegion(0, 0, 0.5, 0.5)
        sheet.add_frame("frame1", uv)

        assert "frame1" in sheet
        assert len(sheet) == 1

    def test_get_frame(self):
        """Test retrieving frames."""
        from engine.renderer.spritesheet import Spritesheet

        texture = Texture(128, 128)
        sheet = Spritesheet(texture)

        uv = UVRegion(0, 0, 0.5, 0.5)
        sheet.add_frame("frame1", uv)
        retrieved = sheet.get_frame("frame1")

        assert retrieved == uv

    def test_get_frame_safe(self):
        """Test safe frame retrieval."""
        from engine.renderer.spritesheet import Spritesheet

        texture = Texture(128, 128)
        sheet = Spritesheet(texture)

        result = sheet.get_frame_safe("missing")
        assert result is None

    def test_add_frame_pixels(self):
        """Test adding frame by pixel coordinates."""
        from engine.renderer.spritesheet import Spritesheet

        texture = Texture(128, 128)
        sheet = Spritesheet(texture)

        sheet.add_frame_pixels("frame1", 0, 0, 32, 32)

        assert "frame1" in sheet
        uv = sheet.get_frame("frame1")
        assert uv.u0 == 0.0
        assert uv.v0 == 0.0
        assert uv.u1 == 0.25
        assert uv.v1 == 0.25

    def test_from_grid(self):
        """Test grid-based spritesheet creation."""
        from engine.renderer.spritesheet import Spritesheet

        texture = Texture(64, 64)
        sheet = Spritesheet.from_grid(texture, 32, 32)

        assert len(sheet) == 4  # 2x2 grid
        assert "frame_00" in sheet
        assert "frame_01" in sheet
        assert "frame_02" in sheet
        assert "frame_03" in sheet

    def test_build_animation(self):
        """Test building animation from frames."""
        from engine.renderer.spritesheet import Spritesheet
        from engine.renderer.animation import Animation

        texture = Texture(64, 32)
        sheet = Spritesheet.from_grid(texture, 32, 32)

        anim = sheet.build_animation("walk", ["frame_00", "frame_01"], fps=12)

        assert isinstance(anim, Animation)
        assert anim.name == "walk"
        assert anim.frame_count == 2

    def test_build_animation_range(self):
        """Test building animation from frame range."""
        from engine.renderer.spritesheet import Spritesheet
        from engine.renderer.animation import Animation

        texture = Texture(64, 64)
        sheet = Spritesheet.from_grid(texture, 32, 32)

        anim = sheet.build_animation_range("walk", "frame_", 0, 2, fps=12)

        assert isinstance(anim, Animation)
        assert anim.name == "walk"
        assert anim.frame_count == 3
