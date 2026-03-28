"""
Asset Subsystem.

Provides asset loading and management.

Layer: 2 (Engine)
Dependencies: engine.subsystem, hal.interfaces
"""

from engine.asset.manager import IAssetManager, AssetManager

__all__ = [
    "IAssetManager",
    "AssetManager",
]
