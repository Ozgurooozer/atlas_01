"""Tests for normal map lighting system."""
import pytest
from core.vec import Vec2
from core.color import Color


class TestNormalMapTexture:
    """Test suite for normal map texture system."""

    def test_normal_map_texture_creation(self):
        """NormalMapTexture should store diffuse and normal textures."""
        from engine.renderer.normal_lighting import NormalMapTexture
        
        nmt = NormalMapTexture()
        
        assert nmt.diffuse is None  # Not loaded yet
        assert nmt.normal is None
        assert nmt.specular is None

    def test_normal_map_load_diffuse(self):
        """NormalMapTexture should load diffuse texture."""
        from engine.renderer.normal_lighting import NormalMapTexture
        
        nmt = NormalMapTexture()
        # Mock texture load - would use real texture in implementation
        nmt.diffuse = "mock_diffuse_texture"
        
        assert nmt.diffuse == "mock_diffuse_texture"

    def test_normal_map_load_normal(self):
        """NormalMapTexture should load normal map."""
        from engine.renderer.normal_lighting import NormalMapTexture
        
        nmt = NormalMapTexture()
        nmt.normal = "mock_normal_texture"
        
        assert nmt.normal == "mock_normal_texture"


class TestNormalMapShader:
    """Test suite for normal map shader calculations."""

    def test_calculate_lighting_basic(self):
        """Shader should calculate basic lighting from normal and light."""
        from engine.renderer.normal_lighting import NormalMapShader
        
        shader = NormalMapShader()
        
        # Normal pointing up (0, 0, 1)
        normal = (0.0, 0.0, 1.0)
        # Light from above pointing down (towards surface)
        light_dir = (0.0, 0.0, 1.0)
        
        intensity = shader.calculate_lighting(normal, light_dir)
        
        # Light directly above normal should give max intensity
        assert intensity > 0.9

    def test_calculate_lighting_angled(self):
        """Shader should reduce intensity for angled light."""
        from engine.renderer.normal_lighting import NormalMapShader
        
        shader = NormalMapShader()
        
        # Normal pointing up
        normal = (0.0, 0.0, 1.0)
        # Light from 45 degree angle (pointing towards surface)
        import math
        angle_rad = math.radians(45)
        light_dir = (math.sin(angle_rad), 0.0, math.cos(angle_rad))
        
        intensity = shader.calculate_lighting(normal, light_dir)
        
        # Should be less than direct but still positive (around 0.707)
        assert 0.5 < intensity < 0.9

    def test_apply_specular(self):
        """Shader should calculate specular highlight."""
        from engine.renderer.normal_lighting import NormalMapShader
        
        shader = NormalMapShader()
        
        # View direction (looking down at surface)
        view_dir = (0.0, 0.0, 1.0)
        # Normal pointing up
        normal = (0.0, 0.0, 1.0)
        # Light direction (from above, same as view for direct reflection)
        light_dir = (0.0, 0.0, 1.0)
        
        specular = shader.apply_specular(normal, light_dir, view_dir, shininess=32.0)
        
        # Direct reflection should give high specular
        assert specular > 0.5


class TestLight3D:
    """Test suite for 3D-positioned lights."""

    def test_light3d_creation(self):
        """Light3D should store position, color, and intensity."""
        from engine.renderer.normal_lighting import Light3D
        from core.vec import Vec3
        
        light = Light3D(
            position=Vec3(100, 200, 50),
            color=Color.white(),
            intensity=1.0,
            range_value=200.0
        )
        
        assert light.position.x == 100
        assert light.position.y == 200
        assert light.position.z == 50
        assert light.intensity == 1.0
        assert light.range == 200.0

    def test_light3d_height(self):
        """Light3D should support height (Z elevation)."""
        from engine.renderer.normal_lighting import Light3D
        from core.vec import Vec3
        
        light = Light3D(position=Vec3(0, 0, 100))
        
        assert light.height == 100

    def test_light_attenuation(self):
        """Light intensity should fall off with distance."""
        from engine.renderer.normal_lighting import Light3D, LightAttenuation
        from core.vec import Vec3
        
        light = Light3D(
            position=Vec3(0, 0, 0),
            intensity=1.0,
            range_value=100.0
        )
        
        # Distance 0 should give full intensity
        atten = LightAttenuation.calculate(light, Vec3(0, 0, 0))
        assert atten == 1.0
        
        # Distance 50 should give partial intensity
        atten = LightAttenuation.calculate(light, Vec3(50, 0, 0))
        assert 0 < atten < 1.0


class TestLightManager:
    """Test suite for light management system."""

    def test_light_manager_creation(self):
        """LightManager should initialize with empty light list."""
        from engine.renderer.normal_lighting import LightManager
        
        lm = LightManager()
        
        assert lm.light_count == 0

    def test_add_light(self):
        """LightManager should add lights."""
        from engine.renderer.normal_lighting import LightManager, Light3D
        from core.vec import Vec3
        
        lm = LightManager()
        light = Light3D(position=Vec3(100, 100, 50))
        
        lm.add_light(light)
        
        assert lm.light_count == 1

    def test_max_lights_limit(self):
        """LightManager should enforce max lights limit."""
        from engine.renderer.normal_lighting import LightManager, Light3D
        
        lm = LightManager()
        
        # Add more than MAX_LIGHTS (50)
        for i in range(55):
            light = Light3D()
            lm.add_light(light)
        
        # Should be capped at 50
        assert lm.light_count == 50

    def test_cull_lights_by_distance(self):
        """LightManager should cull distant lights."""
        from engine.renderer.normal_lighting import LightManager, Light3D
        from core.vec import Vec3, Vec2
        
        lm = LightManager()
        camera_pos = Vec2(0, 0)
        
        # Add near light
        near = Light3D(position=Vec3(100, 100, 0), range_value=200)
        lm.add_light(near)
        
        # Add far light
        far = Light3D(position=Vec3(10000, 10000, 0), range_value=50)
        lm.add_light(far)
        
        # Cull lights
        visible = lm.cull_lights(camera_pos, max_distance=500)
        
        # Near light should be visible, far should be culled
        assert len(visible) == 1
