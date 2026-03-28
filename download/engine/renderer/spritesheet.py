"""
Engine Layer (Layer 2) - Spritesheet

Texture atlas with named/indexed frame support.
Compatible with Aseprite and TexturePacker JSON export formats.

Layer: 2 (Engine)
Dependencies: engine.renderer.texture, engine.renderer.animation
"""

from __future__ import annotations
import json
from typing import Dict, List, Optional, Tuple

from engine.renderer.texture import Texture, UVRegion
from engine.renderer.animation import Animation, AnimationFrame


class SpritesheetError(Exception):
    pass


class Spritesheet:
    """
    Texture atlas that maps string or integer keys to UV regions.

    Supports:
    - Grid-based slicing (uniform cells)
    - Named frame registration
    - JSON metadata import (Aseprite-compatible)
    - Animation extraction from named frame sequences
    """

    def __init__(self, texture: Texture) -> None:
        self._texture = texture
        self._frames: Dict[str, UVRegion] = {}

    @property
    def texture(self) -> Texture:
        return self._texture

    @property
    def frame_names(self) -> List[str]:
        return list(self._frames.keys())

    def add_frame(self, name: str, uv: UVRegion) -> None:
        self._frames[name] = uv

    def add_frame_pixels(
        self, name: str, x: int, y: int, w: int, h: int
    ) -> None:
        uv = self._texture.sub_region(x, y, w, h)
        self._frames[name] = uv

    def get_frame(self, name: str) -> UVRegion:
        if name not in self._frames:
            raise SpritesheetError(f"Frame {name!r} not found in spritesheet")
        return self._frames[name]

    def get_frame_safe(self, name: str) -> Optional[UVRegion]:
        return self._frames.get(name)

    def __contains__(self, name: str) -> bool:
        return name in self._frames

    def __len__(self) -> int:
        return len(self._frames)

    @classmethod
    def from_grid(
        cls,
        texture: Texture,
        cell_width: int,
        cell_height: int,
        columns: Optional[int] = None,
        rows: Optional[int] = None,
        offset_x: int = 0,
        offset_y: int = 0,
        spacing_x: int = 0,
        spacing_y: int = 0,
        prefix: str = "frame_",
    ) -> "Spritesheet":
        """
        Slice a texture into a uniform grid.

        Frames are named: prefix + zero-padded index (e.g. "frame_00", "frame_01")
        """
        sheet = cls(texture)
        cols = columns or (texture.width // cell_width)
        row_count = rows or (texture.height // cell_height)

        index = 0
        for row in range(row_count):
            for col in range(cols):
                px = offset_x + col * (cell_width + spacing_x)
                py = offset_y + row * (cell_height + spacing_y)
                name = f"{prefix}{index:02d}"
                sheet.add_frame_pixels(name, px, py, cell_width, cell_height)
                index += 1

        return sheet

    @classmethod
    def from_aseprite_json(
        cls,
        texture: Texture,
        json_path: str,
    ) -> "Spritesheet":
        """
        Load frame data from an Aseprite-exported JSON atlas.

        Expected format:
        {
          "frames": {
            "frame_name": {
              "frame": {"x": 0, "y": 0, "w": 32, "h": 32}
            }
          }
        }
        """
        with open(json_path, "r") as f:
            data = json.load(f)

        sheet = cls(texture)
        frames_data = data.get("frames", {})

        if isinstance(frames_data, list):
            # Array format
            for entry in frames_data:
                name = entry["filename"]
                fr = entry["frame"]
                sheet.add_frame_pixels(name, fr["x"], fr["y"], fr["w"], fr["h"])
        else:
            # Dict format
            for name, entry in frames_data.items():
                fr = entry["frame"]
                sheet.add_frame_pixels(name, fr["x"], fr["y"], fr["w"], fr["h"])

        return sheet

    def build_animation(
        self,
        name: str,
        frame_names: List[str],
        fps: float = 12.0,
        mode: str = "loop",
    ) -> Animation:
        """
        Build an Animation from a list of frame names in this sheet.
        """
        duration = 1.0 / fps
        frames = []
        for fn in frame_names:
            uv = self.get_frame(fn)
            frames.append(AnimationFrame(uv=uv, duration=duration))
        return Animation(name, frames, mode)

    def build_animation_range(
        self,
        name: str,
        prefix: str,
        start: int,
        end: int,
        fps: float = 12.0,
        mode: str = "loop",
    ) -> Animation:
        """
        Build animation from prefixed grid frames e.g. prefix='run_', 0..7
        """
        frame_names = [f"{prefix}{i:02d}" for i in range(start, end + 1)]
        return self.build_animation(name, frame_names, fps, mode)

    def __repr__(self) -> str:
        return (
            f"Spritesheet(tex_id={self._texture.gpu_id}, "
            f"frames={len(self._frames)})"
        )
