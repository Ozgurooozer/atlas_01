"""Tests for volumetric effects system."""
from core.vec import Vec3


class TestVolumetricFog:
    """Test suite for volumetric fog system."""

    def test_fog_creation(self):
        """VolumetricFog should initialize with density."""
        from engine.renderer.volumetric import VolumetricFog
        
        fog = VolumetricFog(density=0.5)
        
        assert fog.density == 0.5
        assert fog.scattering == 1.0

    def test_height_fog(self):
        """Fog should support height-based density."""
        from engine.renderer.volumetric import VolumetricFog
        
        fog = VolumetricFog()
        fog.height_fog(fog_height=50.0, falloff=0.1)
        
        assert fog.height == 50.0
        assert fog.falloff == 0.1

    def test_get_density_at_height(self):
        """Fog density should vary with height."""
        from engine.renderer.volumetric import VolumetricFog
        
        fog = VolumetricFog(density=1.0)
        fog.height_fog(fog_height=100.0, falloff=0.1)
        
        # At fog height, density should be max
        density_at_height = fog.get_density_at_height(100.0)
        assert density_at_height > 0.8
        
        # Below fog, density should decrease
        density_below = fog.get_density_at_height(0.0)
        assert density_below < density_at_height


class TestLightShafts:
    """Test suite for light shaft/god ray effects."""

    def test_light_shaft_creation(self):
        """LightShaft should store light position and properties."""
        from engine.renderer.volumetric import LightShaft
        
        shaft = LightShaft(
            light_position=Vec3(100, 200, 150),
            intensity=0.8
        )
        
        assert shaft.light_position.x == 100
        assert shaft.intensity == 0.8

    def test_occlusion_query(self):
        """LightShaft should detect occluding objects."""
        from engine.renderer.volumetric import LightShaft
        
        shaft = LightShaft(light_position=Vec3(0, 0, 100))
        
        # Object at light position (occluding)
        occluded = shaft.check_occlusion(Vec3(0, 0, 100))
        assert occluded is True

    def test_ray_march_steps(self):
        """LightShaft should calculate ray march steps."""
        from engine.renderer.volumetric import LightShaft
        
        shaft = LightShaft(light_position=Vec3(0, 0, 100))
        
        steps = shaft.get_ray_march_steps(start=Vec3(0, 0, 0), end=Vec3(0, 0, 50))
        
        assert len(steps) > 0
        assert len(steps) <= 64  # Max steps


class TestVolumetricRenderer:
    """Test suite for volumetric rendering."""

    def test_renderer_creation(self):
        """VolumetricRenderer should initialize."""
        from engine.renderer.volumetric import VolumetricRenderer
        
        renderer = VolumetricRenderer()
        
        assert renderer.fog_pass_enabled is True
        assert renderer.light_shaft_enabled is True

    def test_render_fog_pass(self):
        """Renderer should render fog pass."""
        from engine.renderer.volumetric import VolumetricRenderer, VolumetricFog
        
        renderer = VolumetricRenderer()
        fog = VolumetricFog(density=0.5)
        
        # Should not raise
        result = renderer.render_fog(fog, screen_width=800, screen_height=600)
        
        assert result is not None

    def test_composite_lightshafts(self):
        """Renderer should composite light shafts."""
        from engine.renderer.volumetric import VolumetricRenderer, LightShaft
        
        renderer = VolumetricRenderer()
        shaft = LightShaft(light_position=Vec3(100, 100, 200))
        
        # Should not raise
        result = renderer.composite_lightshafts([shaft])
        
        assert result is not None
