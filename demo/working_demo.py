"""Simple working demo with all features."""
import sys
sys.path.insert(0, '.')

import pyglet
import math
from pyglet.window import key
from core.vec import Vec2
from core.color import Color
from engine.renderer.height_sprite import HeightSprite

window = pyglet.window.Window(1024, 768, '2.5D Demo', vsync=True)

cam_x, cam_y = 0, 0
time = 0
sprites = []

# Create scene
for x in range(-5, 6):
    for y in range(-5, 6):
        h = max(0, 40 - (abs(x) + abs(y)) * 6)
        s = HeightSprite(
            base_position=Vec2(512 + x*50, 384 + y*50),
            height=h
        )
        s.color = Color(0.3, 0.6, 0.3) if h < 15 else Color(0.6, 0.5, 0.4)
        s.size = 45
        sprites.append(s)

# Trees
trees = [(450, 300, 60), (580, 320, 70), (480, 450, 55)]
for x, y, h in trees:
    s = HeightSprite(base_position=Vec2(x, y), height=h)
    s.color = Color(0.2, 0.7, 0.2)
    s.size = 35
    s.is_tree = True
    sprites.append(s)

# Character
char = HeightSprite(base_position=Vec2(512, 384), height=0)
char.color = Color(0.9, 0.3, 0.3)
char.size = 30
char.is_char = True
sprites.append(char)

@window.event
def on_draw():
    window.clear()
    
    cx, cy = 512 + cam_x, 384 + cam_y
    
    for s in sprites:
        rel_x = s.base_position.x - 512
        rel_y = s.base_position.y - 384
        
        sx = cx + (rel_x - rel_y) * 0.5
        sy = cy + (rel_x + rel_y) * 0.25 - s.height * 0.3
        
        size = s.size
        
        if hasattr(s, 'is_char'):
            # Character
            px = cx + math.sin(time * 2) * 80
            py = cy + 40
            pyglet.shapes.Rectangle(px-15, py-15, 30, 30, 
                color=(int(s.color.r*255), int(s.color.g*255), int(s.color.b*255))).draw()
            
            # Direction line
            dx = math.cos(time * 3) * 20
            dy = math.sin(time * 3) * 10
            pyglet.shapes.Line(px, py, px+dx, py+dy, color=(255,255,0)).draw()
            
        elif hasattr(s, 'is_tree'):
            # Tree
            pyglet.shapes.Circle(sx, sy, size/2, 
                color=(int(s.color.r*255), int(s.color.g*255), int(s.color.b*255))).draw()
            # Shadow
            pyglet.shapes.Circle(sx+8, sy-6, size/3, color=(40,40,40)).draw()
        else:
            # Ground
            pyglet.shapes.Rectangle(sx-size/2, sy-size/4, size, size/2,
                color=(int(s.color.r*255), int(s.color.g*255), int(s.color.b*255))).draw()
    
    # Particles
    for i in range(8):
        angle = time * 4 + i * 0.8
        dist = 40 + math.sin(time * 2 + i) * 15
        px = cx + math.sin(time * 2) * 80 + math.cos(angle) * dist
        py = cy + 60 + math.sin(angle) * dist * 0.5
        pyglet.shapes.Circle(px, py, 5, color=(255, 215, 0)).draw()
    
    # UI
    pyglet.text.Label('WASD:Move | ESC:Exit | 2.5D Engine', 
        font_size=16, x=10, y=10, color=(255,255,255,255)).draw()

def update(dt):
    global time
    time += dt

@window.event  
def on_key_press(sym, mod):
    global cam_x, cam_y
    if sym == key.W: cam_y -= 40
    elif sym == key.S: cam_y += 40
    elif sym == key.A: cam_x += 40
    elif sym == key.D: cam_x -= 40
    elif sym == key.ESCAPE: pyglet.app.exit()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
