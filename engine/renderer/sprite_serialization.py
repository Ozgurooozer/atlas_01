"""
Sprite serialization utilities.

Provides serialize() and deserialize() methods for
saving and loading sprite data.

Layer: 2 (Engine)
Dependencies: core.object
"""

from __future__ import annotations

from typing import Any, Dict


class SpriteSerializationMixin:
    """
    Mixin class for sprite serialization.

    Requires: position, scale_x, scale_y, rotation, color, visible, z_index
    Provides: serialize(), deserialize()
    """

    def serialize(self) -> Dict[str, Any]:
        """Serialize sprite data."""
        data = self._serialize_base()  # type: ignore[attr-defined]
        data['position_x'] = self.position.x  # type: ignore[attr-defined]
        data['position_y'] = self.position.y  # type: ignore[attr-defined]
        data['scale_x'] = self.scale_x  # type: ignore[attr-defined]
        data['scale_y'] = self.scale_y  # type: ignore[attr-defined]
        data['rotation'] = self.rotation  # type: ignore[attr-defined]
        data['color'] = self.color  # type: ignore[attr-defined]
        data['visible'] = self.visible  # type: ignore[attr-defined]
        data['z_index'] = self.z_index  # type: ignore[attr-defined]
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize sprite data."""
        self._deserialize_base(data)  # type: ignore[attr-defined]
        if 'position_x' in data:
            from core.vec import Vec2
            self.position = Vec2(  # type: ignore[attr-defined]
                data['position_x'],
                data.get('position_y', 0)
            )
        if 'scale_x' in data:
            self.scale_x = data['scale_x']  # type: ignore[attr-defined]
        if 'scale_y' in data:
            self.scale_y = data['scale_y']  # type: ignore[attr-defined]
        if 'rotation' in data:
            self.rotation = data['rotation']  # type: ignore[attr-defined]
        if 'color' in data:
            self.color = tuple(data['color'])  # type: ignore[attr-defined]
        if 'visible' in data:
            self.visible = data['visible']  # type: ignore[attr-defined]
        if 'z_index' in data:
            self.z_index = data['z_index']  # type: ignore[attr-defined]

    def _serialize_base(self) -> Dict[str, Any]:
        """Call parent serialize. Override if needed."""
        return super().serialize()  # type: ignore[misc]

    def _deserialize_base(self, data: Dict[str, Any]) -> None:
        """Call parent deserialize. Override if needed."""
        super().deserialize(data)  # type: ignore[misc]
