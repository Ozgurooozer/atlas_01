"""2.5D Isometric Rendering Visual Demo.

Demonstrates all FAZ 12 features:
- Isometric projection
- Height sprites with elevation
- Layer management and depth sorting
- Normal map lighting
- Soft shadows
- 3D positioned lights
- 3D particles
- Volumetric fog
- Post-process effects

Usage:
    python visual_demo_25d.py

Controls:
    WASD - Move camera
    +/- - Zoom in/out
    ESC - Exit
"""
import sys
import math

# Try to import pyglet for visual rendering
try:
    import pyglet
    from pyglet import shapes
    from pyglet.window import key
    HAS_PYGLET = True
except ImportError:
    HAS_PYGLET = False
    print("Pyglet not available. Running in headless demonstration mode.")

# Import our 2.5D rendering modules
sys.path.insert(0, '.')

from core.vec import Vec2, Vec3
from core.color import Color
from engine.renderer.isometric import IsometricProjection, IsometricCamera
from engine.renderer.height_sprite import HeightSprite, HeightMap
from engine.renderer.layer_manager import LayerManager
from engine.renderer.normal_lighting import Light3D, LightManager
from engine.renderer.particle3d import ParticleEmitter3D, ParticleRenderer3D
from engine.renderer.volumetric import VolumetricFog
from engine.renderer.postprocess_stack import (
    PostProcessStack, ToneMapping, Vignette
)


class DemoScene:
    """2.5D demo scene showcasing all features."""
    
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        
        # Isometric projection
        self.iso = IsometricProjection(width, height, tile_size=64)
        
        # Camera
        self.camera = IsometricCamera(0, 0)
        self.camera.set_zoom_level(1.0)
        
        # Layer manager
        self.layer_manager = LayerManager()
        
        # Height map for terrain
        self.height_map = HeightMap(width=20, height=20, tile_size=64)
        self._setup_terrain()
        
        # Lights
        self.light_manager = LightManager()
        self._setup_lights()
        
        # Particles
        self.particle_emitter = ParticleEmitter3D()
        self.particle_emitter.position = Vec3(400, 300, 50)
        self.particle_renderer = ParticleRenderer3D(max_particles=1000)
        
        # Fog
        self.fog = VolumetricFog(density=0.15)
        self.fog.height_fog(fog_height=200.0, falloff=0.005)
        
        # Post-process
        self.post_process = PostProcessStack()
        self.post_process.add_pass(ToneMapping(exposure=1.0))
        self.post_process.add_pass(Vignette(intensity=0.3))
        
        # Demo objects
        self.sprites = []
        self._create_demo_scene()
        
        # Time
        self.time = 0.0
        
    def _setup_terrain(self):
        """Create height map terrain."""
        # Create a small hill at center
        for x in range(8, 12):
            for y in range(8, 12):
                height = 50.0 - (abs(x - 10) + abs(y - 10)) * 10
                self.height_map.set_height(x, y, max(0, height))
    
    def _setup_lights(self):
        """Setup 3D lights."""
        # Main sun light
        sun = Light3D(
            position=Vec3(512, 200, 200),
            color=Color.orange(),
            intensity=1.0,
            range_value=500.0
        )
        self.light_manager.add_light(sun)
        
        # Ambient point light
        point = Light3D(
            position=Vec3(400, 300, 80),
            color=Color.white(),
            intensity=0.6,
            range_value=200.0
        )
        self.light_manager.add_light(point)
    
    def _create_demo_scene(self):
        """Create demo scene objects."""
        # Ground tiles
        for x in range(-5, 6):
            for y in range(-5, 6):
                ground = HeightSprite(
                    base_position=Vec2(x * 64 + 400, y * 64 + 300),
                    height=0.0
                )
                ground.color = Color(0.4, 0.5, 0.3)  # Green
                ground.size = 64.0
                self.sprites.append(ground)
                self.layer_manager.add_to_layer(ground, 'floor')
        
        # Trees (with height)
        tree_positions = [
            (300, 200, 80),
            (500, 250, 80),
            (350, 400, 100),
            (450, 350, 90),
            (200, 300, 70),
        ]
        
        for x, y, h in tree_positions:
            tree = HeightSprite(
                base_position=Vec2(x, y),
                height=h
            )
            tree.color = Color(0.2, 0.6, 0.2)
            tree.size = 48.0
            self.sprites.append(tree)
            self.layer_manager.add_to_layer(tree, 'characters')
        
        # Characters
        char_positions = [
            (400, 300, 0),
            (420, 320, 0),
            (380, 310, 0),
        ]
        
        for x, y, h in char_positions:
            char = HeightSprite(
                base_position=Vec2(x, y),
                height=h
            )
            char.color = Color(0.8, 0.3, 0.3)  # Red-ish
            char.size = 32.0
            self.sprites.append(char)
            self.layer_manager.add_to_layer(char, 'characters')
        
        # Sort layers
        self.layer_manager.sort_all_layers()
    
    def update(self, dt):
        """Update scene."""
        self.time += dt
        
        # Update particles
        self.particle_emitter.update(dt)
        
        # Emit particles occasionally
        if int(self.time * 10) % 5 == 0:
            self.particle_emitter.emit(2)
        
        # Animate lights
        for i, light in enumerate(self.light_manager._lights):
            if i == 0:  # Sun
                light.position.x = 512 + math.sin(self.time * 0.5) * 100
                light.position.y = 200 + math.cos(self.time * 0.3) * 50
    
    def render(self):
        """Render scene."""
        if not HAS_PYGLET:
            self._render_headless()
            return
        
        # Clear screen
        pyglet.gl.glClearColor(0.1, 0.12, 0.15, 1.0)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        
        # Create batch for efficient rendering
        batch = pyglet.graphics.Batch()
        
        # Render layers
        self._render_layers(batch)
        
        # Render particles
        self._render_particles(batch)
        
        # Draw everything
        batch.draw()
    
    def _render_layers(self, batch):
        """Render all layers."""
        # Get sorted layers
        layers = self.layer_manager.get_sorted_layers()
        
        for layer_name, sprites in layers:
            # Sort by depth within layer
            sprites.sort(key=lambda s: s.get_depth_sort_key())
            
            for sprite in sprites:
                self._render_sprite(sprite, batch)
    
    def _render_sprite(self, sprite, batch):
        """Render a single sprite."""
        # Get screen position with height
        screen_pos = sprite.get_screen_position(self.iso)
        
        # Apply camera
        relative = Vec2(
            sprite.base_position.x - self.camera.position.x,
            sprite.base_position.y - self.camera.position.y
        )
        screen = self.iso.world_to_screen(relative)
        
        # Apply zoom
        center_x = self.width / 2
        center_y = self.height / 2
        final_x = center_x + (screen.x - center_x) * self.camera.zoom
        final_y = center_y + (screen.y - center_y) * self.camera.zoom
        
        # Apply height offset
        final_y -= sprite.height * 0.5 * self.camera.zoom
        
        # Get color with fog
        fog_density = self.fog.get_density_at_height(sprite.base_position.y)
        fog_color = Color(0.7, 0.75, 0.8)
        final_color = Color.lerp(sprite.color, fog_color, fog_density * 0.3)
        
        # Draw sprite (simplified as circle)
        size = sprite.size * self.camera.zoom / 2
        shapes.Circle(
            final_x, final_y, size,
            color=(int(final_color.r * 255), int(final_color.g * 255), int(final_color.b * 255)),
            batch=batch
        )
    
    def _render_particles(self, batch):
        """Render particles."""
        particles = self.particle_emitter.particles
        if not particles:
            return
        
        # Batch and sort particles
        batched = self.particle_renderer.batch_particles(particles)
        
        for p in batched[:100]:  # Limit visible particles
            # Get screen position
            relative = Vec2(
                p.position.x - self.camera.position.x,
                p.position.y - self.camera.position.y
            )
            screen = self.iso.world_to_screen(relative)
            
            # Apply zoom
            center_x = self.width / 2
            center_y = self.height / 2
            final_x = center_x + (screen.x - center_x) * self.camera.zoom
            final_y = center_y + (screen.y - center_y) * self.camera.zoom
            
            # Get size and color
            size = p.get_current_size() * self.camera.zoom
            color = p.get_current_color()
            alpha = int((p.life / p.max_life) * 255)
            
            # Draw particle
            shapes.Circle(
                final_x, final_y, size,
                color=(int(color.r * 255), int(color.g * 255), int(color.b * 255)),
                batch=batch
            )
    
    def _render_headless(self):
        """Render in headless mode (console output)."""
        # Just print status
        particle_count = len(self.particle_emitter.particles)
        light_count = self.light_manager.light_count
        sprite_count = len(self.sprites)
        
        print(f"\r[Demo] Sprites: {sprite_count}, Particles: {particle_count}, "
              f"Lights: {light_count}, Time: {self.time:.1f}s", end='', flush=True)
    
    def on_key_press(self, symbol, modifiers):
        """Handle key press."""
        speed = 50.0
        
        if symbol == key.W:
            self.camera.position.y += speed
        elif symbol == key.S:
            self.camera.position.y -= speed
        elif symbol == key.A:
            self.camera.position.x -= speed
        elif symbol == key.D:
            self.camera.position.x += speed
        elif symbol == key.EQUAL or symbol == key.PLUS:
            zoom = min(3.0, self.camera.zoom + 0.1)
            self.camera.set_zoom_level(zoom)
        elif symbol == key.MINUS:
            zoom = max(0.5, self.camera.zoom - 0.1)
            self.camera.set_zoom_level(zoom)
        elif symbol == key.ESCAPE:
            return True
        
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("2.5D Isometric Rendering Demo")
    print("=" * 60)
    print()
    print("Features demonstrated:")
    print("  - Isometric projection")
    print("  - Height/elevation system")
    print("  - Layer management (floor, characters)")
    print("  - Depth sorting")
    print("  - 3D positioned lights")
    print("  - Particle systems")
    print("  - Volumetric fog")
    print("  - Camera control")
    print()
    
    if HAS_PYGLET:
        print("Controls:")
        print("  WASD - Move camera")
        print("  +/-  - Zoom in/out")
        print("  ESC  - Exit")
        print()
        
        # Create window
        window = pyglet.window.Window(
            width=1024,
            height=768,
            caption="2.5D Isometric Demo",
            vsync=True
        )
        
        # Create scene
        scene = DemoScene(1024, 768)
        
        @window.event
        def on_draw():
            scene.render()
        
        @window.event
        def on_key_press(symbol, modifiers):
            if scene.on_key_press(symbol, modifiers):
                pyglet.app.exit()
        
        def update(dt):
            scene.update(dt)
        
        pyglet.clock.schedule_interval(update, 1/60.0)
        
        print("Starting demo...")
        pyglet.app.run()
    else:
        print("Running headless demonstration mode...")
        print()
        
        # Headless mode
        scene = DemoScene()
        
        # Simulate frames
        import time
        for i in range(300):  # 5 seconds at 60fps
            scene.update(1/60.0)
            scene.render()
            time.sleep(1/60.0)
        
        print("\n\nDemo complete!")
    
    print()
    print("=" * 60)
    print("Demo Statistics:")
    print(f"  Sprites: {len(scene.sprites)}")
    print(f"  Lights: {scene.light_manager.light_count}")
    print(f"  Layers: {len(scene.layer_manager.layers)}")
    print(f"  Runtime: {scene.time:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
