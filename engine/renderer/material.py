"""
Material system for custom shaders and uniforms.

A Material defines how a sprite is rendered by specifying
a shader and a set of uniform values.

Layer: 2 (Engine)
Dependencies: None
"""

from __future__ import annotations
from typing import Any, Dict


class Material:
    """
    Material defining shader and uniform parameters.

    Attributes:
        shader_name: Name of the shader to use.
        uniforms: Dictionary of uniform names and values.
    """

    def __init__(self, shader_name: str = "default"):
        """
        Create a new Material.

        Args:
            shader_name: Name of the shader from ShaderLibrary.
        """
        self._shader_name: str = shader_name
        self._uniforms: Dict[str, Any] = {}

    @property
    def shader_name(self) -> str:
        """Get shader name."""
        return self._shader_name

    @shader_name.setter
    def shader_name(self, value: str) -> None:
        """Set shader name."""
        self._shader_name = value

    @property
    def uniforms(self) -> Dict[str, Any]:
        """Get uniforms dictionary."""
        return self._uniforms

    def set_uniform(self, name: str, value: Any) -> None:
        """
        Set a uniform value.

        Args:
            name: Uniform name in shader.
            value: Value to set (float, int, tuple, etc.)
        """
        self._uniforms[name] = value

    def get_uniform(self, name: str, default: Any = None) -> Any:
        """
        Get a uniform value.

        Args:
            name: Uniform name.
            default: Default value if not found.

        Returns:
            Uniform value or default.
        """
        return self._uniforms.get(name, default)

    def copy(self) -> Material:
        """
        Create a deep copy of the material.

        Returns:
            A new Material instance with same properties.
        """
        new_mat = Material(self._shader_name)
        # Shallow copy of dict is enough for simple types (float, int, tuple)
        new_mat._uniforms = self._uniforms.copy()
        return new_mat

    def __repr__(self) -> str:
        """String representation."""
        return f"Material(shader='{self._shader_name}', uniforms={len(self._uniforms)})"
