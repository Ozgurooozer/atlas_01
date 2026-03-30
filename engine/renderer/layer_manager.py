"""Layer manager and depth sorting system for 2.5D rendering.

Provides layer-based rendering and depth sorting for isometric sprites.

Layer: 2 (Engine)
Dependencies: core.vec, engine.renderer.height_sprite
"""
from typing import List, Dict, Any, Optional
from core.vec import Vec2
from engine.renderer.height_sprite import HeightSprite


class DepthSortKey:
    """Sort key for depth-based sprite ordering.
    
    Determines render order of sprites within a layer.
    Lower values are rendered first (back), higher values last (front).
    
    Sorting formula: Y position + height * 0.5 + custom_priority
    
    Usage:
        key = DepthSortKey.from_sprite(sprite)
        or
        key = DepthSortKey(y_position=200, height=50)
    """
    
    def __init__(self, y_position: float, height: float = 0.0, 
                 custom_priority: float = 0.0):
        """Initialize depth sort key.
        
        Args:
            y_position: Sprite Y position in world
            height: Sprite height/elevation
            custom_priority: Manual override for sorting
        """
        self.y_position = y_position
        self.height = height
        self.custom_priority = custom_priority
        
        # Calculate final sort value
        self.sort_value = y_position + height * 0.5 + custom_priority
    
    @classmethod
    def from_sprite(cls, sprite: HeightSprite, 
                    custom_priority: float = 0.0) -> 'DepthSortKey':
        """Create sort key from HeightSprite.
        
        Args:
            sprite: HeightSprite instance
            custom_priority: Manual override
            
        Returns:
            DepthSortKey for the sprite
        """
        return cls(
            y_position=sprite.base_position.y,
            height=sprite.height,
            custom_priority=custom_priority
        )
    
    def __lt__(self, other: 'DepthSortKey') -> bool:
        """Compare sort keys for ordering."""
        return self.sort_value < other.sort_value
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, DepthSortKey):
            return False
        return self.sort_value == other.sort_value


class LayerManager:
    """Manages rendering layers and depth sorting.
    
    Organizes sprites into named layers (floor, characters, fx, ui, etc.)
    and handles back-to-front rendering order within each layer.
    
    Usage:
        lm = LayerManager()
        lm.add_to_layer(sprite, 'characters')
        lm.sort_layer('characters')
        lm.render_layers(renderer)
    """
    
    # Default layer configuration (layer_name: render_order)
    DEFAULT_LAYERS = {
        'background': -100,
        'floor': 0,
        'shadow': 1,
        'characters': 10,
        'fx_back': 20,
        'fx_front': 30,
        'ui': 100,
    }
    
    def __init__(self, custom_layers: Optional[Dict[str, int]] = None):
        """Initialize layer manager.
        
        Args:
            custom_layers: Optional custom layer configuration
        """
        # Use custom layers or defaults
        self.layers = custom_layers or dict(self.DEFAULT_LAYERS)
        
        # Store sprites per layer
        self._layer_sprites: Dict[str, List[HeightSprite]] = {
            name: [] for name in self.layers
        }
    
    def add_to_layer(self, sprite: HeightSprite, layer_name: str) -> None:
        """Add a sprite to a layer.
        
        Args:
            sprite: HeightSprite to add
            layer_name: Target layer name
        """
        if layer_name not in self._layer_sprites:
            raise ValueError(f"Unknown layer: {layer_name}")
        
        self._layer_sprites[layer_name].append(sprite)
    
    def remove_from_layer(self, sprite: HeightSprite, 
                         layer_name: str) -> bool:
        """Remove a sprite from a layer.
        
        Args:
            sprite: HeightSprite to remove
            layer_name: Layer to remove from
            
        Returns:
            True if removed, False if not found
        """
        if layer_name not in self._layer_sprites:
            return False
        
        layer = self._layer_sprites[layer_name]
        if sprite in layer:
            layer.remove(sprite)
            return True
        return False
    
    def get_layer(self, layer_name: str) -> List[HeightSprite]:
        """Get all sprites in a layer.
        
        Args:
            layer_name: Layer name
            
        Returns:
            List of sprites in that layer
        """
        return self._layer_sprites.get(layer_name, [])
    
    def get_layer_order(self, layer_name: str) -> int:
        """Get render order for a layer.
        
        Lower values are rendered first.
        
        Args:
            layer_name: Layer name
            
        Returns:
            Render order value
        """
        return self.layers.get(layer_name, 0)
    
    def sort_layer(self, layer_name: str) -> None:
        """Sort sprites in a layer by depth.
        
        Sorts back-to-front based on Y position + height.
        
        Args:
            layer_name: Layer to sort
        """
        if layer_name not in self._layer_sprites:
            return
        
        layer = self._layer_sprites[layer_name]
        
        # Sort by depth sort key (lower values = back, higher = front)
        layer.sort(key=lambda sprite: DepthSortKey.from_sprite(sprite))
    
    def sort_all_layers(self) -> None:
        """Sort all layers by depth."""
        for layer_name in self._layer_sprites:
            self.sort_layer(layer_name)
    
    def clear_layer(self, layer_name: str) -> None:
        """Remove all sprites from a layer.
        
        Args:
            layer_name: Layer to clear
        """
        if layer_name in self._layer_sprites:
            self._layer_sprites[layer_name].clear()
    
    def clear_all(self) -> None:
        """Remove all sprites from all layers."""
        for layer in self._layer_sprites.values():
            layer.clear()
    
    def get_sorted_layers(self) -> List[tuple]:
        """Get all layers sorted by render order.
        
        Returns:
            List of (layer_name, sprites) tuples in render order
        """
        # Sort layer names by render order
        sorted_names = sorted(
            self.layers.keys(),
            key=lambda name: self.layers[name]
        )
        
        # Return (name, sprites) pairs
        return [
            (name, self._layer_sprites[name])
            for name in sorted_names
        ]
    
    def render_layers(self, renderer: Any) -> None:
        """Render all layers in order.
        
        Args:
            renderer: Renderer instance with draw_sprite method
        """
        sorted_layers = self.get_sorted_layers()
        
        for layer_name, sprites in sorted_layers:
            # Sort within layer by depth
            sprites.sort(key=lambda s: DepthSortKey.from_sprite(s))
            
            # Render each sprite
            for sprite in sprites:
                if hasattr(renderer, 'draw_sprite'):
                    renderer.draw_sprite(sprite)
