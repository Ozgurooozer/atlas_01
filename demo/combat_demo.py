"""Enhanced 2.5D Demo - All FAZ 12 Features + Combat Polish.

Features:
- Isometric grid with height
- 3D positioned lights (visual)
- Moving character with particles
- Combat polish: damage numbers, screenshake, hit effects
- Trees with shadows
- SDF Font labels

Controls:
  WASD - Move camera
  SPACE - Trigger hit effect
  C - Critical hit
  H - Heal
  ESC - Exit
"""
import sys
sys.path.insert(0, '.')

import pyglet
import math
import random
from pyglet.window import key

from core.vec import Vec2, Vec3
from core.color import Color
from engine.renderer.height_sprite import HeightSprite
from engine.game.combat_polish import CombatPolishManager
from engine.renderer.sdf_font import SDFFont, SDFTextRenderer

from engine.settings import Settings
from ui.settings_menu import SettingsMenu

# Initialize settings
settings = Settings()
settings_menu = SettingsMenu(settings)
settings_menu.create_video_tab()
settings_menu.create_audio_tab()

# Initialize window
window = pyglet.window.Window(1024, 768, '2.5D Combat Demo', vsync=True)

# Game state
cam_x, cam_y = 0, 0
time = 0

# Combat polish system
combat = CombatPolishManager()

# SDF Font for text rendering
font = SDFFont(size=24)
text_renderer = SDFTextRenderer(font)

# Scene objects
sprites = []
damage_texts = []  # For rendering damage numbers

class DamageText:
    """Visual damage number for rendering."""
    def __init__(self, value, x, y, color, is_critical=False):
        self.value = value
        self.x = x
        self.y = y
        self.vy = 80  # Float up speed
        self.life = 1.5
        self.max_life = 1.5
        self.color = color
        self.is_critical = is_critical
        self.scale = 1.5 if is_critical else 1.0

    def update(self, dt):
        self.y += self.vy * dt
        self.vy *= 0.95  # Slow down
        self.life -= dt
        return self.life > 0

    def get_alpha(self):
        return max(0.0, self.life / self.max_life)


def create_scene():
    """Create demo scene."""
    cx, cy = 512, 384
    
    # Ground tiles
    for x in range(-5, 6):
        for y in range(-5, 6):
            dist = abs(x) + abs(y)
            height = max(0, 50 - dist * 8)
            
            tile = HeightSprite(
                base_position=Vec2(cx + x*50, cy + y*50),
                height=height
            )
            
            # Color based on height
            if height > 20:
                tile.color = Color(0.7, 0.6, 0.5)  # Brown (hill)
            else:
                tile.color = Color(0.3, 0.6, 0.3)  # Green
            
            tile.size = 45
            sprites.append(('ground', tile))
    
    # Trees
    tree_pos = [(cx-130, cy-90, 70), (cx+170, cy-110, 80), 
                (cx-90, cy+140, 65), (cx+200, cy+90, 75)]
    for x, y, h in tree_pos:
        tree = HeightSprite(base_position=Vec2(x, y), height=h)
        tree.color = Color(0.15, 0.6, 0.15)
        tree.size = 35
        sprites.append(('tree', tree))
    
    # Character
    char = HeightSprite(base_position=Vec2(cx, cy), height=0)
    char.color = Color(0.9, 0.25, 0.25)
    char.size = 28
    sprites.append(('character', char))
    
    return char


character = create_scene()


@window.event
def on_draw():
    window.clear()
    
    # Get screenshake offset
    shake = combat.update(1/60)
    cx = 512 + cam_x + int(shake.x)
    cy = 384 + cam_y + int(shake.y)
    
    # Draw all sprites
    for obj_type, sprite in sprites:
        rel_x = sprite.base_position.x - 512
        rel_y = sprite.base_position.y - 384
        
        sx = cx + (rel_x - rel_y) * 0.5
        sy = cy + (rel_x + rel_y) * 0.25 - sprite.height * 0.3
        size = sprite.size
        
        r = int(sprite.color.r * 255)
        g = int(sprite.color.g * 255)
        b = int(sprite.color.b * 255)
        
        if obj_type == 'character':
            # Animated character position
            px = cx + math.sin(time * 2) * 100
            py = cy + 30
            
            # Character body
            pyglet.shapes.Rectangle(px-14, py-14, 28, 28, 
                color=(230, 60, 60)).draw()
            
            # Direction indicator
            angle = time * 3
            dx = math.cos(angle) * 20
            dy = math.sin(angle) * 10
            pyglet.shapes.Line(px, py, px+dx, py+dy, 
                color=(255, 255, 0)).draw()
            
            # Light glow around character
            glow_alpha = int(80 + math.sin(time * 4) * 40)
            pyglet.shapes.Circle(px, py, 35, 
                color=(255, 200, 100, glow_alpha)).draw()
            
        elif obj_type == 'tree':
            # Tree crown
            pyglet.shapes.Circle(sx, sy, size/2, color=(r, g, b)).draw()
            # Shadow
            pyglet.shapes.Circle(sx+8, sy-6, size/3, color=(40, 40, 40)).draw()
            # Trunk
            pyglet.shapes.Rectangle(sx-4, sy-15, 8, 15, 
                color=(100, 80, 60)).draw()
            
        else:  # ground
            # Diamond shape approximation with rectangle
            pyglet.shapes.Rectangle(int(sx-size/2), int(sy-size/4), 
                int(size), int(size/2), color=(r, g, b)).draw()
    
    # Particles around character
    char_x = cx + math.sin(time * 2) * 100
    char_y = cy + 30
    
    for i in range(6):
        angle = time * 4 + i * 1.0
        dist = 35 + math.sin(time * 3 + i) * 15
        px = char_x + math.cos(angle) * dist
        py = char_y + math.sin(angle) * dist + 10
        size = 4 + math.sin(time * 5 + i) * 2
        
        pyglet.shapes.Circle(int(px), int(py), int(size), 
            color=(255, 215, 0)).draw()
    
    # Damage numbers
    for dmg in damage_texts:
        alpha = dmg.get_alpha()
        scale = dmg.scale
        text = str(dmg.value) + ('!' if dmg.is_critical else '')
        
        # Simple text rendering (placeholder for SDF)
        label = pyglet.text.Label(
            text,
            font_size=int(16 * scale),
            x=int(dmg.x), y=int(dmg.y),
            color=(int(dmg.color.r * 255), int(dmg.color.g * 255), 
                   int(dmg.color.b * 255), int(255 * alpha))
        )
        label.draw()
    
# Draw settings menu if visible
    if settings_menu.visible:
        # Dark overlay
        overlay = pyglet.shapes.Rectangle(0, 0, window.width, window.height, 
                                          color=(0, 0, 0, 180))
        overlay.opacity = 180
        overlay.draw()
        
        # Menu panel
        panel_x, panel_y = 200, 150
        panel_w, panel_h = 624, 468
        panel = pyglet.shapes.Rectangle(panel_x, panel_y, panel_w, panel_h,
                                        color=(40, 40, 40))
        panel.draw()
        
        # Title
        pyglet.text.Label(
            'SETTINGS', font_size=24, x=panel_x + 20, y=panel_y + panel_h - 40,
            color=(255, 255, 255, 255), bold=True
        ).draw()
        
        # Current settings
        y_offset = panel_y + panel_h - 80
        settings_text = [
            f"Resolution: {settings.video.resolution[0]}x{settings.video.resolution[1]}",
            f"Fullscreen: {'ON' if settings.video.fullscreen else 'OFF'}",
            f"VSync: {'ON' if settings.video.vsync else 'OFF'}",
            f"Target FPS: {settings.video.target_fps}",
            f"Brightness: {settings.video.brightness:.1f}",
            f"Master Volume: {settings.audio.master_volume:.0%}",
            f"SFX Volume: {settings.audio.sfx_volume:.0%}",
            f"Music Volume: {settings.audio.music_volume:.0%}",
            "",
            "Press ESC to close",
            "Press Q to quit game"
        ]
        
        for text in settings_text:
            pyglet.text.Label(
                text, font_size=14, x=panel_x + 20, y=y_offset,
                color=(200, 200, 200, 255)
            ).draw()
            y_offset -= 25
    
    # UI
    pyglet.text.Label(
        '2.5D Combat Demo - FAZ 12 COMPLETE',
        font_size=16, x=10, y=748, color=(255, 255, 255, 255)
    ).draw()
    
    pyglet.text.Label(
        'WASD:Move Camera | SPACE:Hit | C:Critical | H:Heal | ESC:Settings',
        font_size=14, x=10, y=10, color=(255, 255, 255, 255)
    ).draw()


def update(dt):
    global time
    time += dt
    
    # Update combat polish
    combat.update(dt)
    
    # Update damage numbers
    for dmg in damage_texts[:]:
        if not dmg.update(dt):
            damage_texts.remove(dmg)


@window.event
def on_key_press(sym, mod):
    global cam_x, cam_y
    
    if sym == key.W:
        cam_y -= 50
    elif sym == key.S:
        cam_y += 50
    elif sym == key.A:
        cam_x += 50
    elif sym == key.D:
        cam_x -= 50
    
    elif sym == key.SPACE:
        # Normal hit
        char_x = 512 + math.sin(time * 2) * 100
        char_y = 384 + 30
        damage = random.randint(15, 35)
        combat.process_hit(damage, Vec3(char_x, char_y, 0))
        
        # Add visual damage text
        dmg_text = DamageText(damage, char_x + random.randint(-20, 20), 
                              char_y + 40, Color(1, 1, 1))
        damage_texts.append(dmg_text)
    
    elif sym == key.C:
        # Critical hit
        char_x = 512 + math.sin(time * 2) * 100
        char_y = 384 + 30
        damage = random.randint(80, 120)
        combat.process_hit(damage, Vec3(char_x, char_y, 0), critical=True)
        
        # Add critical damage text
        dmg_text = DamageText(damage, char_x, char_y + 50, 
                              Color(1, 0.3, 0.1), is_critical=True)
        damage_texts.append(dmg_text)
    
    elif sym == key.H:
        # Heal
        char_x = 512 + math.sin(time * 2) * 100
        char_y = 384 + 30
        heal_amount = random.randint(20, 50)
        combat.process_heal(heal_amount, Vec3(char_x, char_y, 0))
        
        # Add heal text
        dmg_text = DamageText(heal_amount, char_x, char_y + 40, 
                              Color(0.3, 1, 0.3))
        damage_texts.append(dmg_text)
    
    elif sym == key.ESCAPE:
        # Toggle settings menu only
        settings_menu.toggle()
        print(f"Menu: {'open' if settings_menu.visible else 'closed'}")
        if not settings_menu.visible:
            settings_menu.save_settings()
    
    elif sym == key.F1:
        # Exit game
        print("Exiting...")
        pyglet.app.exit()


pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
