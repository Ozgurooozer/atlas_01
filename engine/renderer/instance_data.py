"""
InstanceData for GPU Instancing.

Provides a structured way to pass per-instance data to the GPU.
Used by SpriteBatch, ParticleSystem, and TileMapRenderer.

Layer: 2 (Engine)
Dependencies: dataclasses, struct
"""

from __future__ import annotations
import struct
import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class InstanceData:
    """
    Per-instance data for GPU instancing.
    
    Attributes:
        position: (x, y) world position.
        size: (width, height) in world units.
        rotation: rotation in degrees.
        color: (r, g, b, a) normalized color (0.0 - 1.0).
        anchor: (x, y) anchor point (0.0 - 1.0).
        flip: (x, y) flip flags (0.0 or 1.0).
        uv_offset: (u, v) texture coordinate offset.
        uv_size: (u, v) texture coordinate size.
    """
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (1.0, 1.0)
    rotation: float = 0.0
    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    anchor: Tuple[float, float] = (0.5, 0.5)
    flip: Tuple[float, float] = (0.0, 0.0)
    uv_offset: Tuple[float, float] = (0.0, 0.0)
    uv_size: Tuple[float, float] = (1.0, 1.0)

    def __post_init__(self) -> None:
        """Validate data for NaN or Inf values."""
        fields = [
            self.position, self.size, (self.rotation,), 
            self.color, self.anchor, self.flip, 
            self.uv_offset, self.uv_size
        ]
        for field in fields:
            for val in field:
                if not math.isfinite(val):
                    raise ValueError(f"InstanceData contains non-finite value: {val}")

    def to_bytes(self) -> bytes:
        """
        Serialize to binary format for GPU buffer.
        Format: 17 floats (68 bytes)
        pos(2), size(2), rot(1), color(4), anchor(2), flip(2), uv_off(2), uv_size(2)
        """
        return struct.pack(
            "17f",
            self.position[0], self.position[1],
            self.size[0], self.size[1],
            self.rotation,
            self.color[0], self.color[1], self.color[2], self.color[3],
            self.anchor[0], self.anchor[1],
            self.flip[0], self.flip[1],
            self.uv_offset[0], self.uv_offset[1],
            self.uv_size[0], self.uv_size[1]
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> InstanceData:
        """Deserialize from binary format."""
        vals = struct.unpack("17f", data)
        return cls(
            position=(vals[0], vals[1]),
            size=(vals[2], vals[3]),
            rotation=vals[4],
            color=(vals[5], vals[6], vals[7], vals[8]),
            anchor=(vals[9], vals[10]),
            flip=(vals[11], vals[12]),
            uv_offset=(vals[13], vals[14]),
            uv_size=(vals[15], vals[16])
        )
