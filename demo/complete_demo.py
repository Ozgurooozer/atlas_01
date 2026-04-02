"""Complete 2.5D Engine Demo - All Features Integrated.

Features:
- Isometric projection
- HeightSprite with elevation
- Layer management + depth sorting  
- Light3D with 3D positioned lights
- ShadowCaster with soft shadows
- DirectionalSprite (8-way)
- Particle3D with 3D particles
- VolumetricFog
- PostProcessStack (tone mapping, vignette)

Controls:
  WASD - Move camera
  +/- - Zoom in/out
  1-5 - Toggle features
  ESC - Exit
"""
import sys
sys.path.insert(0, '.')

import pyglet
import math
from pyglet.window import key

# Our engine modules
from core.vec import Vec2, Vec3
from core.color import Color
from engine.renderer.isometric import IsometricProjection
from engine.renderer.height_sprite import HeightSprite
from engine.renderer.layer_manager import LayerManager
from engine.renderer.normal_lighting import Light3D, LightManager
from engine.renderer.soft_shadows import ShadowLight
from engine.renderer.particle3d import ParticleEmitter3D
from engine.renderer.volumetric import VolumetricFog
from engine.renderer.postprocess_stack import (
    PostProcessStack, ToneMapping, Vignette
)


class CompleteEngineDemo:
    """Full 2.5D engine demo with all features."""
    
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        
        # Camera
        self.cam_x = 0
        self.cam_y = 0
        self.zoom = 1.0
        
        # Isometric projection
        self.iso = IsometricProjection(width, height, tile_size=64)
        
        # Layer manager
        self.layer_manager = LayerManager()
        
        # 3D Light system
        self.light_manager = LightManager()
        self._setup_lights()
        
        # Shadow system
        self.shadow_light = ShadowLight(position=Vec2(100, 100), height=150)
        
        # Particle system
        self.particle_emitter = ParticleEmitter3D()
        self.particle_emitter.position = Vec3(500, 400, 30)
        self.particle_emitter.emission_rate = 30
        
        # Fog
        self.fog = VolumetricFog(density=0.2)
        self.fog.height_fog(fog_height=300, falloff=0.01)
        
        # Post-process
        self.post_process = PostProcessStack()
        self.post_process.add_pass(ToneMapping(exposure=1.0))
        self.post_process.add_pass(Vignette(intensity=0.25))
        
        # Scene objects
        self.sprites = []
        self._create_scene()
        
        # Feature toggles
        self.features = {
            'lights': True,
            'shadows': True,
            'particles': True,
            'fog': True,
            'postprocess': True,
        }
        
        self.time = 0
        
    def _setup_lights(self):
        """Setup 3D lights."""
        # Sun light (orange, high intensity)
        sun = Light3D(
            position=Vec3(200, 100, 200),
            color=Color(1.0, 0.7, 0.4),
            intensity=1.2,
            range_value=600
        )
        self.light_manager.add_light(sun)
        
        # Blue ambient light
        ambient = Light3D(
            position=Vec3(600, 300, 80),
            color=Color(0.4, 0.5, 0.9),
            intensity=0.6,
            range_value=400
        )
        self.light_manager.add_light(ambient)
    
    def _create_scene(self):
        """Create demo scene."""
        cx, cy = 512, 384
        
        # Ground tiles with varying heights
        for x in range(-4, 5):
            for y in range(-4, 5):
                # Create hill in center
                dist = abs(x) + abs(y)
                height = max(0, 40 - dist * 8)
                
                tile = HeightSprite(
                    base_position=Vec2(cx + x*50, cy + y*50),
                    height=height
                )
                
                # Color based on height
                if height > 20:
                    tile.color = Color(0.6, 0.5, 0.4)  # Brown (hill top)
                else:
                    tile.color = Color(0.3, 0.5, 0.3)  # Green (ground)
                
                tile.size = 45
                self.sprites.append(tile)
                self.layer_manager.add_to_layer(tile, 'floor')
        
        # Trees with shadows
        tree_pos = [
            (cx-120, cy-80, 60),
            (cx+150, cy-100, 70),
            (cx-80, cy+120, 55),
            (cx+180, cy+80, 65),
        ]
        
        for x, y, h in tree_pos:
            tree = HeightSprite(
                base_position=Vec2(x, y),
                height=h
            )
            tree.color = Color(0.2, 0.6, 0.2)
            tree.size = 35
            tree.is_tree = True
            self.sprites.append(tree)
            self.layer_manager.add_to_layer(tree, 'characters')
        
        # Character with directional sprites
        char = HeightSprite(
            base_position=Vec2(cx, cy),
            height=0
        )
        char.color = Color(0.8, 0.3, 0.3)
        char.size = 28
        char.is_character = True
        char.facing_angle = 0
        self.sprites.append(char)
        self.layer_manager.add_to_layer(char, 'characters')
        
        # Sort layers
        self.layer_manager.sort_all_layers()
    
    def update(self, dt):
        """Update scene."""
        self.time += dt
        
        # Update particles
        if self.features['particles']:
            self.particle_emitter.update(dt)
            # Emit particles from character position
            self.particle_emitter.position.x = 512 + math.sin(self.time) * 80
            self.particle_emitter.position.y = 384 + 30
        
        # Animate lights
        if self.features['lights']:
            for i, light in enumerate(self.light_manager._lights):
                if i == 0:  # Sun
                    light.position.x = 200 + math.sin(self.time * 0.5) * 100
                    light.position.z = 150 + math.cos(self.time * 0.3) * 50
                else:  # Ambient
                    light.position.y = 300 + math.cos(self.time * 0.7) * 60
        
        # Animate character
        for sprite in self.sprites:
            if hasattr(sprite, 'is_character'):
                sprite.facing_angle = (self.time * 90) % 360
                sprite.base_position.x = 512 + math.sin(self.time) * 60
                sprite.base_position.y = 384 + math.cos(self.time * 0.7) * 30
    
    def render(self):
        """Render complete scene."""
        window.clear()
        
        # Debug: Check sprite count
        print(f"Rendering {len(self.sprites)} sprites")
        
        # Build batch
        batch = pyglet.graphics.Batch()
        
        # Render layers with depth sorting
        self._render_layers(batch)
        
        # Render particles
        if self.features['particles']:
            self._render_particles(batch)
        
        batch.draw()
        
        # Render UI overlay
        self._render_ui()
    
    def _render_layers(self, batch):
        """Render all layers with lighting and fog."""
        layers = self.layer_manager.get_sorted_layers()
        
        for layer_name, sprites in layers:
            sprites.sort(key=lambda s: s.get_depth_sort_key())
            
            for sprite in sprites:
                self._render_sprite(sprite, batch)
    
    def _render_sprite(self, sprite, batch):
        """Render single sprite with all effects."""
        # Apply camera
        cx = self.width / 2 + self.cam_x
        cy = self.height / 2 + self.cam_y
        
        # Isometric projection
        rel_x = sprite.base_position.x - 512
        rel_y = sprite.base_position.y - 384
        
        sx = cx + (rel_x - rel_y) * 0.5 * self.zoom
        sy = cy + (rel_x + rel_y) * 0.25 * self.zoom - sprite.height * 0.3 * self.zoom
        
        # Apply lighting
        color = sprite.color
        if self.features['lights']:
            light_intensity = self._calculate_lighting(sprite)
            color = Color(
                color.r * light_intensity,
                color.g * light_intensity,
                color.b * light_intensity
            )
        
        # Apply fog
        if self.features['fog']:
            fog_density = self.fog.get_density_at_height(sprite.base_position.y)
            fog_color = Color(0.7, 0.75, 0.8)
            color = Color.lerp(color, fog_color, fog_density * 0.4)
        
        # Apply post-process (simple)
        if self.features['postprocess']:
            # Vignette effect - darken edges
            dist_from_center = math.sqrt((sx - cx)**2 + (sy - cy)**2) / 400
            vignette = max(0, 1 - dist_from_center * 0.3)
            color = Color(color.r * vignette, color.g * vignette, color.b * vignette)
        
        size = sprite.size * self.zoom
        
        # Draw based on type
        if hasattr(sprite, 'is_character'):
            # Character - red square
            pyglet.shapes.Rectangle(
                sx - size/2, sy - size/2,
                size, size,
                color=(int(color.r * 255), int(color.g * 255), int(color.b * 255)),
                batch=batch
            )
            # Direction indicator
            angle = math.radians(sprite.facing_angle)
            dx = math.cos(angle) * size * 0.6
            dy = math.sin(angle) * size * 0.3
            pyglet.shapes.Line(
                sx, sy, sx + dx, sy + dy,
                color=(255, 255, 0),
                batch=batch
            )
        elif hasattr(sprite, 'is_tree'):
            # Tree - green circle
            pyglet.shapes.Circle(
                sx, sy, size/2,
                color=(int(color.r * 255), int(color.g * 255), int(color.b * 255)),
                batch=batch
            )
            # Shadow
            if self.features['shadows']:
                pyglet.shapes.Circle(
                    sx + 10, sy - 8, size/2 * 0.7,
                    color=(30, 30, 30, 100),
                    batch=batch
                )
        else:
            # Ground tile
            pyglet.shapes.Rectangle(
                sx - size/2, sy - size/4,
                size, size/2,
                color=(int(color.r * 255), int(color.g * 255), int(color.b * 255)),
                batch=batch
            )
    
    def _calculate_lighting(self, sprite):
        """Calculate light intensity at sprite position."""
        total = 0.3  # Ambient base
        
        for light in self.light_manager._lights:
            dx = sprite.base_position.x - light.position.x
            dy = sprite.base_position.y - light.position.y
            dz = sprite.height - light.position.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < light.range:
                attenuation = 1.0 - (dist / light.range)
                total += light.intensity * attenuation * 0.5
        
        return min(1.5, total)
    
    def _render_particles(self, batch):
        """Render 3D particles."""
        for p in self.particle_emitter.particles[:50]:
            # 3D to isometric
            cx = self.width / 2 + self.cam_x
            cy = self.height / 2 + self.cam_y
            
            rel_x = p.position.x - 512
            rel_y = p.position.y - 384
            
            sx = cx + (rel_x - rel_y) * 0.5 * self.zoom
            sy = cy + (rel_x + rel_y) * 0.25 * self.zoom - p.position.z * self.zoom
            
            size = p.get_current_size() * self.zoom
            alpha = p.life / p.max_life
            
            pyglet.shapes.Circle(
                sx, sy, size,
                color=(255, 215, 0, int(alpha * 255)),
                batch=batch
            )
    
    def _render_ui(self):
        """Render UI overlay."""
        y = self.height - 20
        
        # Title
        pyglet.text.Label(
            '2.5D Engine Demo - All Features Active',
            font_size=16, x=10, y=y,
            color=(255, 255, 255, 255)
        ).draw()
        
        # Feature toggles
        y -= 25
        for name, active in self.features.items():
            status = 'ON' if active else 'OFF'
            color = (0, 255, 0) if active else (255, 0, 0)
            pyglet.text.Label(
                f'{name}: {status}',
                font_size=12, x=10, y=y,
                color=(*color, 255)
            ).draw()
            y -= 20
        
        # Controls
        pyglet.text.Label(
            'WASD:Move  +/-:Zoom  1-5:Toggle  ESC:Exit',
            font_size=14, x=10, y=10,
            color=(255, 255, 255, 255)
        ).draw()
    
    def toggle_feature(self, num):
        """Toggle feature by number."""
        keys = list(self.features.keys())
        if 1 <= num <= len(keys):
            key = keys[num - 1]
            self.features[key] = not self.features[key]
    
    def on_key(self, symbol):
        """Handle key press."""
        if symbol == key.W:
            self.cam_y -= 40
        elif symbol == key.S:
            self.cam_y += 40
        elif symbol == key.A:
            self.cam_x += 40
        elif symbol == key.D:
            self.cam_x -= 40
        elif symbol == key.EQUAL or symbol == key.PLUS:
            self.zoom = min(2.0, self.zoom + 0.1)
        elif symbol == key.MINUS:
            self.zoom = max(0.5, self.zoom - 0.1)
        elif symbol == key._1:
            self.toggle_feature(1)
        elif symbol == key._2:
            self.toggle_feature(2)
        elif symbol == key._3:
            self.toggle_feature(3)
        elif symbol == key._4:
            self.toggle_feature(4)
        elif symbol == key._5:
            self.toggle_feature(5)
        elif symbol == key.ESCAPE:
            return True
        return False


# Create window and demo
window = pyglet.window.Window(1024, 768, 'Complete 2.5D Engine Demo', vsync=True)
demo = CompleteEngineDemo(1024, 768)

@window.event
def on_draw():
    demo.render()

@window.event
def on_key_press(symbol, modifiers):
    if demo.on_key(symbol):
        pyglet.app.exit()

def update(dt):
    demo.update(dt)

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
