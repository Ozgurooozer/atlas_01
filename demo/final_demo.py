"""Final 2.5D Isometric Demo - Working."""
import pyglet
import math

window = pyglet.window.Window(1024, 768, '2.5D Isometric Demo', vsync=True)

cam_x, cam_y = 0, 0
time = 0

@window.event
def on_draw():
    window.clear()
    
    cx, cy = 512 + cam_x, 384 + cam_y
    tile = 35
    
    # Grid
    for x in range(-6, 7):
        for y in range(-6, 7):
            sx = cx + (x - y) * tile
            sy = cy + (x + y) * tile * 0.5
            
            # Sadece ekranda görünenler
            if -50 < sx < 1074 and -50 < sy < 818:
                white = (x + y) % 2 == 0
                color = (240, 240, 240) if white else (80, 80, 80)
                pyglet.shapes.Rectangle(sx-18, sy-9, 36, 18, color=color).draw()
    
    # Player - hareketli
    px = cx + math.sin(time * 2) * 120
    py = cy + 40
    pyglet.shapes.Rectangle(px-12, py-12, 24, 24, color=(255, 50, 50)).draw()
    
    # Particles
    for i in range(5):
        angle = time * 3 + i * 1.2
        dist = 30 + math.sin(time + i) * 15
        px2 = px + math.cos(angle) * dist
        py2 = py + math.sin(angle) * dist
        pyglet.shapes.Circle(px2, py2, 4, color=(255, 215, 0)).draw()
    
    # UI
    pyglet.text.Label(
        'WASD: Move Camera | ESC: Exit',
        font_size=16, x=10, y=10,
        color=(255, 255, 255, 255)
    ).draw()

def update(dt):
    global time
    time += dt

@window.event  
def on_key_press(sym, mod):
    global cam_x, cam_y
    if sym == pyglet.window.key.W: cam_y -= 40
    elif sym == pyglet.window.key.S: cam_y += 40
    elif sym == pyglet.window.key.A: cam_x += 40
    elif sym == pyglet.window.key.D: cam_x -= 40
    elif sym == pyglet.window.key.ESCAPE: pyglet.app.exit()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
