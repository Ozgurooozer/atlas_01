"""
Renderer Subsystem.

Provides 2D rendering using ModernGL.

Layer: 2 (Engine)
Dependencies: engine.subsystem, hal.interfaces
"""

from engine.renderer.renderer import IRenderer, Renderer2D
from engine.renderer.texture import Texture, TextureLoader
from engine.renderer.sprite import Sprite
from engine.renderer.batch import SpriteBatch
from engine.renderer.camera import Camera

__all__ = [
    "IRenderer",
    "Renderer2D",
    "Texture",
    "TextureLoader",
    "Sprite",
    "SpriteBatch",
    "Camera",
]
