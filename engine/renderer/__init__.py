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
from engine.renderer.material import Material
from engine.renderer.postprocess_stack import (
    PostProcessStack,
    BloomPass,
    ColorGradingPass,
    VignettePass,
    FXAAPass,
)

__all__ = [
    "IRenderer",
    "Renderer2D",
    "Texture",
    "TextureLoader",
    "Sprite",
    "SpriteBatch",
    "Camera",
    "Material",
    "PostProcessStack",
    "BloomPass",
    "ColorGradingPass",
    "VignettePass",
    "FXAAPass",
]
