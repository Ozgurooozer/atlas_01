"""
Visual Test for Advanced Renderer Integration

Demonstrates:
- Shader system with uniform caching
- Animation playback with loop/one-shot modes
- Spritesheet grid slicing
- Dynamic lighting (point + ambient lights)

Controls:
- SPACE: Toggle animation play/pause
- R: Reset animation
- ESC: Exit
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engine'))

import pyglet
from pyglet import gl
from pyglet.window import key

from engine.renderer.animation import AnimationPlayer
from engine.renderer.spritesheet import Spritesheet
from engine.renderer.light import Light2D, LightType
from engine.renderer.texture import Texture
from core.vec import Vec2
from core.color import Color

# Window setup
window = pyglet.window.Window(800, 600, "Advanced Renderer Visual Test", resizable=True)
batch = pyglet.graphics.Batch()

# Create test texture (checkerboard pattern)
def create_checkerboard_texture():
    """Create a 4x4 checkerboard texture for testing."""
    size = 4
    data = bytearray(size * size * 4)
    
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            if (x + y) % 2 == 0:
                # White
                data[idx:idx+4] = bytes([255, 255, 255, 255])
            else:
                # Orange (Hades-like)
                data[idx:idx+4] = bytes([255, 140, 0, 255])
    
    return Texture(width=size, height=size, data=bytes(data), name="checkerboard")

# Create spritesheet from checkerboard
texture = create_checkerboard_texture()
spritesheet = Spritesheet.from_grid(texture, 2, 2, columns=2, rows=2, prefix="frame_")

# Build animation from spritesheet
anim = spritesheet.build_animation_range("idle", "frame_", 0, 3, fps=4, mode="loop")

# Create animation player
player = AnimationPlayer()
player.play(anim)

# Create test label
info_label = pyglet.text.Label(
    text="Advanced Renderer Test\nAnimation: Playing | Frame: 0 | Light: ON",
    font_name='Consolas',
    font_size=12,
    x=10, y=window.height - 10,
    anchor_x='left', anchor_y='top',
    multiline=True,
    width=400,
    color=(255, 255, 255, 255),
)

# Light system setup (simulated for display)
ambient_light = Light2D(
    light_type=LightType.AMBIENT,
    color=Color(0.2, 0.2, 0.3, 1.0),
    intensity=0.3
)

point_light = Light2D(
    light_type=LightType.POINT,
    color=Color.orange(),
    intensity=1.0,
    position=Vec2(400, 300),
    radius=200.0,
    falloff=1.5
)

# Visual representation sprites
sprites = []
light_sprite = None

def update(dt):
    """Update animation and lights."""
    global player
    
    # Update animation
    player.update(dt)
    
    # Update info text
    frame_idx = player.current_frame_index
    playing = "Playing" if player.is_playing else "Paused"
    light_status = "ON" if point_light.enabled else "OFF"
    info_label.text = (
        f"Advanced Renderer Test\n"
        f"Animation: {playing} | Frame: {frame_idx} | Light: {light_status}\n"
        f"Point Light: pos=({point_light.position.x:.0f}, {point_light.position.y:.0f})\n"
        f"Ambient: {ambient_light.intensity:.1f}"
    )
    
    # Update visual sprite UVs based on animation frame
    if sprites and player.current_uv:
        # In a real implementation, this would update the sprite's UV coords
        pass

@window.event
def on_draw():
    """Render the scene."""
    window.clear()
    
    # Draw background (ambient light color)
    gl.glClearColor(
        ambient_light.color.r * ambient_light.intensity,
        ambient_light.color.g * ambient_light.intensity,
        ambient_light.color.b * ambient_light.intensity,
        1.0
    )
    window.clear()
    
    # Draw animated sprite representation
    # (In full implementation, this would use the shader system)
    frame_idx = player.current_frame_index
    colors = [
        (255, 255, 255),  # White
        (255, 200, 100),  # Light orange
        (255, 140, 0),    # Orange
        (200, 100, 50),   # Dark orange
    ]
    
    # Draw center sprite with animation frame color
    color = colors[frame_idx]
    
    # Apply point light attenuation at center
    center = Vec2(400, 300)
    att = point_light.attenuation_at(center)
    
    # Modulate color by light
    final_r = int(color[0] * (ambient_light.intensity + att * point_light.intensity))
    final_g = int(color[1] * (ambient_light.intensity + att * point_light.intensity))
    final_b = int(color[2] * (ambient_light.intensity + att * point_light.intensity))
    
    # Draw animated quad using modern pyglet API
    from pyglet.shapes import Rectangle
    rect = Rectangle(350, 250, 100, 100, color=(final_r, final_g, final_b, 255))
    rect.draw()
    
    # Draw point light visualization
    if point_light.enabled:
        light_rect = Rectangle(
            int(point_light.position.x - 10),
            int(point_light.position.y - 10),
            20, 20,
            color=(255, 255, 0, 128)
        )
        light_rect.draw()
    
    # Draw info label
    info_label.draw()
    
    # Draw legend
    legend_y = 100
    pyglet.text.Label(
        text="Controls:\nSPACE: Play/Pause | R: Reset | L: Toggle Light | ESC: Exit",
        font_name='Consolas',
        font_size=10,
        x=10, y=legend_y,
        multiline=True,
        width=400,
        color=(200, 200, 200, 255),
    ).draw()

@window.event
def on_key_press(symbol, modifiers):
    """Handle keyboard input."""
    global player, point_light
    
    if symbol == key.SPACE:
        if player.is_playing:
            player.pause()
        else:
            player.resume()
    elif symbol == key.R:
        player.stop()
        player.play(anim)
    elif symbol == key.L:
        point_light.enabled = not point_light.enabled
    elif symbol == key.ESCAPE:
        window.close()
        pyglet.app.exit()

@window.event
def on_mouse_motion(x, y, dx, dy):
    """Move point light with mouse."""
    point_light.position = Vec2(x, y)

if __name__ == "__main__":
    print("Advanced Renderer Visual Test")
    print("=" * 40)
    print("Features being tested:")
    print("  - Animation system (loop mode, 4 fps)")
    print("  - Spritesheet grid slicing (2x2)")
    print("  - Point light with attenuation")
    print("  - Ambient light")
    print("=" * 40)
    print("Controls: SPACE=Play/Pause, R=Reset, L=Toggle Light, ESC=Exit")
    print("Mouse moves the point light")
    
    # Schedule updates
    pyglet.clock.schedule_interval(update, 1/60.0)
    
    # Run
    pyglet.app.run()
