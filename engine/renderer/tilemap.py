"""
TileMapRenderer for efficient grid-based rendering.

Uses GPU instancing to draw large tilemaps with frustum culling.

Layer: 2 (Engine)
Dependencies: core.vec, engine.renderer.texture, engine.renderer.batch
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from core.vec import Vec2
from engine.renderer.texture import Texture
from engine.renderer.batch import SpriteBatch
from engine.renderer.sprite import Sprite


class TileMapRenderer:
    """
    Efficiently renders a grid of tiles.
    
    Attributes:
        tileset: Texture containing all tiles.
        tile_size: Size of a single tile in pixels.
        map_size: (width, height) in tiles.
    """
    
    def __init__(self, tileset: Texture, tile_size: int = 32):
        self.tileset = tileset
        self.tile_size = tile_size
        self.map_size = (0, 0)
        self._tiles: List[int] = [] # 1D array of tile indices (-1 for empty)
        
    def set_tiles(self, width: int, height: int, tiles: List[int]):
        """Set the tilemap data."""
        if len(tiles) != width * height:
            raise ValueError("Tile data size does not match map dimensions")
        self.map_size = (width, height)
        self._tiles = tiles
        
    def draw(self, batch: SpriteBatch, camera_pos: Vec2, viewport_size: Vec2):
        """
        Draw the tilemap with frustum culling.
        
        Each visible tile gets the correct UV offset from the tileset texture,
        so different tile indices map to different regions of the atlas.
        
        Args:
            batch: SpriteBatch to use for drawing.
            camera_pos: Center of the camera in world coordinates.
            viewport_size: Size of the viewport in world coordinates.
        """
        if not self._tiles:
            return
            
        w, h = self.map_size
        ts = self.tile_size
        
        # Calculate visible range (frustum culling)
        half_vw = viewport_size.x / 2
        half_vh = viewport_size.y / 2
        
        min_x = max(0, int((camera_pos.x - half_vw) / ts))
        max_x = min(w - 1, int((camera_pos.x + half_vw) / ts))
        min_y = max(0, int((camera_pos.y - half_vh) / ts))
        max_y = min(h - 1, int((camera_pos.y + half_vh) / ts))
        
        # Reuse a single sprite object for all tiles
        temp_sprite = Sprite(self.tileset)
        temp_sprite.width = float(ts)
        temp_sprite.height = float(ts)
        
        # UV size for a single tile (tileset is a horizontal strip)
        # tiles_per_row = how many tiles fit horizontally in the tileset
        tiles_per_row = max(1, self.tileset.width // ts)
        uv_w = ts / self.tileset.width
        uv_h = ts / self.tileset.height
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile_idx = self._tiles[y * w + x]
                if tile_idx < 0:
                    continue
                
                # Calculate UV offset for this tile index
                tile_col = tile_idx % tiles_per_row
                tile_row = tile_idx // tiles_per_row
                u0 = tile_col * uv_w
                v0 = tile_row * uv_h
                
                temp_sprite.position = Vec2(x * ts, y * ts)
                temp_sprite.uv_offset = (u0, v0)
                temp_sprite.uv_size = (uv_w, uv_h)
                
                batch.draw(temp_sprite)
