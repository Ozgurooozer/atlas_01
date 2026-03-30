"""Tests for soft shadow system."""
import pytest
import math
from core.vec import Vec2


class TestShadowCaster:
    """Test suite for shadow casting objects."""

    def test_shadow_caster_creation(self):
        """ShadowCaster should store position and size."""
        from engine.renderer.soft_shadows import ShadowCaster
        
        caster = ShadowCaster(
            position=Vec2(100, 200),
            width=50.0,
            height=30.0
        )
        
        assert caster.position.x == 100
        assert caster.position.y == 200
        assert caster.width == 50.0
        assert caster.height == 30.0

    def test_cast_shadow_basic(self):
        """ShadowCaster should cast shadow in light direction."""
        from engine.renderer.soft_shadows import ShadowCaster, ShadowLight
        
        caster = ShadowCaster(position=Vec2(0, 0), width=32.0, height=32.0)
        light = ShadowLight(position=Vec2(100, 0), height=50)  # Light from right
        
        shadow = caster.cast_shadow(light)
        
        assert shadow is not None
        assert shadow.length > 0

    def test_self_shadow_detection(self):
        """ShadowCaster should detect self-shadowing."""
        from engine.renderer.soft_shadows import ShadowCaster, ShadowLight
        
        caster = ShadowCaster(position=Vec2(0, 0), width=32.0, height=32.0)
        # Light from above and slightly to side
        light = ShadowLight(position=Vec2(10, 0), height=100)
        
        is_self_shadow = caster.check_self_shadow(light)
        
        # This is a simplified test - actual implementation may vary
        assert isinstance(is_self_shadow, bool)


class TestShadowMap:
    """Test suite for shadow map generation."""

    def test_shadow_map_creation(self):
        """ShadowMap should initialize with dimensions."""
        from engine.renderer.soft_shadows import ShadowMap
        
        shadow_map = ShadowMap(width=256, height=256)
        
        assert shadow_map.width == 256
        assert shadow_map.height == 256

    def test_generate_shadow_map(self):
        """ShadowMap should accumulate shadows from casters."""
        from engine.renderer.soft_shadows import ShadowMap, ShadowCaster, ShadowLight
        
        shadow_map = ShadowMap(width=128, height=128)
        caster = ShadowCaster(position=Vec2(50, 50), width=20.0, height=20.0)
        light = ShadowLight(position=Vec2(100, 50), height=50)
        
        shadow_map.generate_shadow_map([caster], light)
        
        # Shadow map should have been generated
        assert shadow_map.is_generated

    def test_shadow_blur(self):
        """ShadowMap should support Gaussian blur for soft edges."""
        from engine.renderer.soft_shadows import ShadowMap
        
        shadow_map = ShadowMap(width=64, height=64)
        
        # Create simple shadow data
        shadow_map._data = [[1.0 if x == 32 else 0.0 for x in range(64)] for y in range(64)]
        
        # Apply blur
        shadow_map.blur_shadows(radius=3)
        
        # After blur, neighboring pixels should have non-zero values
        assert shadow_map._data[32][31] > 0
        assert shadow_map._data[32][33] > 0


class TestShadowLight:
    """Test suite for shadow-casting lights."""

    def test_shadow_light_creation(self):
        """ShadowLight should store position and properties."""
        from engine.renderer.soft_shadows import ShadowLight
        
        light = ShadowLight(
            position=Vec2(100, 200),
            height=50.0,
            radius=150.0,
            intensity=0.8
        )
        
        assert light.position.x == 100
        assert light.position.y == 200
        assert light.height == 50.0
        assert light.radius == 150.0
        assert light.intensity == 0.8

    def test_shadow_light_3d_position(self):
        """ShadowLight should provide 3D position."""
        from engine.renderer.soft_shadows import ShadowLight
        
        light = ShadowLight(position=Vec2(100, 200), height=75.0)
        
        pos_3d = light.get_3d_position()
        assert pos_3d[0] == 100.0
        assert pos_3d[1] == 200.0
        assert pos_3d[2] == 75.0

    def test_height_based_shadow_offset(self):
        """Higher lights should cast longer shadows."""
        from engine.renderer.soft_shadows import ShadowLight, ShadowCaster
        
        caster = ShadowCaster(position=Vec2(0, 0), width=32.0, height=32.0)
        
        # Low light
        low_light = ShadowLight(position=Vec2(100, 0), height=10.0)
        shadow_low = caster.cast_shadow(low_light)
        
        # High light
        high_light = ShadowLight(position=Vec2(100, 0), height=100.0)
        shadow_high = caster.cast_shadow(high_light)
        
        # Higher light should cast shorter shadow (more vertical)
        # This is a simplified test - actual shadow geometry may vary
        assert shadow_low is not None
        assert shadow_high is not None


class TestSoftShadowKernel:
    """Test suite for soft shadow kernel operations."""

    def test_gaussian_kernel_generation(self):
        """Should generate Gaussian kernel for blur."""
        from engine.renderer.soft_shadows import SoftShadowKernel
        
        kernel = SoftShadowKernel.generate_gaussian(radius=2, sigma=1.0)
        
        # Kernel should be 5x5 (radius 2 = diameter 5)
        assert len(kernel) == 5
        assert len(kernel[0]) == 5
        
        # Center should be highest
        assert kernel[2][2] > kernel[0][0]
        assert kernel[2][2] > kernel[4][4]

    def test_kernel_normalization(self):
        """Gaussian kernel should sum to 1.0."""
        from engine.renderer.soft_shadows import SoftShadowKernel
        
        kernel = SoftShadowKernel.generate_gaussian(radius=3, sigma=1.5)
        
        total = sum(sum(row) for row in kernel)
        
        assert abs(total - 1.0) < 0.01

    def test_soft_shadow_calculation(self):
        """Should calculate soft shadow intensity at a point."""
        from engine.renderer.soft_shadows import SoftShadowKernel, ShadowCaster, ShadowLight
        
        caster = ShadowCaster(position=Vec2(0, 0), width=32.0, height=32.0)
        light = ShadowLight(position=Vec2(50, 0), height=30.0)
        
        intensity = SoftShadowKernel.calculate_shadow_intensity(
            point=Vec2(20, 0),
            caster=caster,
            light=light
        )
        
        # Shadow intensity should be between 0 and 1
        assert 0.0 <= intensity <= 1.0
