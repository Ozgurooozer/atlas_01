"""Tests for layer manager and depth sorting system."""
import pytest
from core.vec import Vec2
from engine.renderer.layer_manager import LayerManager, DepthSortKey
from engine.renderer.height_sprite import HeightSprite


class TestLayerManager:
    """Test suite for layer management system."""

    def test_layer_manager_creation(self):
        """LayerManager should initialize with default layers."""
        from engine.renderer.layer_manager import LayerManager
        
        lm = LayerManager()
        
        assert 'floor' in lm.layers
        assert 'characters' in lm.layers
        assert 'ui' in lm.layers

    def test_add_to_layer(self):
        """Sprite should be addable to layer."""
        from engine.renderer.layer_manager import LayerManager
        
        lm = LayerManager()
        sprite = HeightSprite(base_position=Vec2(100, 200))
        
        lm.add_to_layer(sprite, 'characters')
        
        assert sprite in lm.get_layer('characters')

    def test_layer_render_order(self):
        """Layers should have correct render order."""
        from engine.renderer.layer_manager import LayerManager
        
        lm = LayerManager()
        
        # 'floor' should render before 'characters'
        floor_order = lm.get_layer_order('floor')
        char_order = lm.get_layer_order('characters')
        
        assert floor_order < char_order

    def test_sort_layer_by_depth(self):
        """Layer should sort sprites by depth (back-to-front)."""
        from engine.renderer.layer_manager import LayerManager
        
        lm = LayerManager()
        
        # Create sprites at different Y positions
        # Lower Y (100) = front, Higher Y (300) = back
        sprite_front = HeightSprite(base_position=Vec2(0, 100))
        sprite_back = HeightSprite(base_position=Vec2(0, 300))
        
        lm.add_to_layer(sprite_front, 'characters')
        lm.add_to_layer(sprite_back, 'characters')
        
        # Sort the layer
        lm.sort_layer('characters')
        
        # Back sprite (Y=300, higher sort key) should come AFTER front (Y=100)
        # Render order: front first, then back
        layer = lm.get_layer('characters')
        assert layer[0] == sprite_front  # Front renders first
        assert layer[1] == sprite_back   # Back renders after


class TestDepthSortKey:
    """Test suite for depth sorting keys."""

    def test_sort_key_from_sprite(self):
        """DepthSortKey should extract key from sprite."""
        from engine.renderer.layer_manager import DepthSortKey
        
        sprite = HeightSprite(base_position=Vec2(100, 200), height=50.0)
        
        key = DepthSortKey.from_sprite(sprite)
        
        # Should be y + height * 0.5 = 200 + 25 = 225
        assert key.sort_value == 225.0

    def test_sort_key_comparison(self):
        """DepthSortKey should be comparable."""
        from engine.renderer.layer_manager import DepthSortKey
        
        key_back = DepthSortKey(y_position=300, height=0)
        key_front = DepthSortKey(y_position=100, height=0)
        
        # Back (higher Y=300) should have higher sort value, render AFTER front (Y=100)
        # So key_back > key_front (back comes after front in render order)
        assert key_back > key_front
        assert key_front < key_back

    def test_custom_priority_override(self):
        """Custom priority should override automatic sorting."""
        from engine.renderer.layer_manager import DepthSortKey
        
        key = DepthSortKey(y_position=200, height=0, custom_priority=1000)
        
        # High priority should push sprite to front
        assert key.sort_value > 200
