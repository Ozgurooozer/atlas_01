"""2.5D Isometric Demo - Fixed Camera."""
import pyglet
import math

window = pyglet.window.Window(800, 600, '2.5D Isometric', vsync=True)

cam_x, cam_y = 0, 0
time = 0

@window.event
def on_draw():
    window.clear()
    batch = pyglet.graphics.Batch()
    
    # Fixed center - NO camera offset here
    cx = 400
    cy = 300
    
    # Isometric grid
    grid = 4
    tile = 60
    
    for x in range(-grid, grid + 1):
        for y in range(-grid, grid + 1):
            # Isometric projection + camera
            sx = cx + (x - y) * tile * 0.8 + cam_x
            sy = cy + (x + y) * tile * 0.4 + cam_y
            
            # Checkerboard
            white = (x + y) % 2 == 0
            color = (220, 220, 220) if white else (80, 80, 80)
            
            # Rectangle tile
            pyglet.shapes.Rectangle(
                sx - tile/2, sy - tile/3,
                tile, tile/1.5,
                color=color,
                batch=batch
            )
    
    # Player - animated
    px = cx + math.sin(time * 2) * 100 + cam_x
    py = cy + 50 + cam_y
    
    pyglet.shapes.Rectangle(
        px - 15, py - 15, 30, 30,
        color=(255, 0, 0),
        batch=batch
    )
    
    batch.draw()
    
    pyglet.text.Label(
        f'WASD: Move | ESC: Exit | Cam: {cam_x},{cam_y}',
        font_size=14, x=10, y=10,
        color=(255, 255, 255, 255)
    ).draw()

def update(dt):
    global time
    time += dt

@window.event  
def on_key_press(sym, mod):
    global cam_x, cam_y
    if sym == pyglet.window.key.W: cam_y -= 50
    elif sym == pyglet.window.key.S: cam_y += 50
    elif sym == pyglet.window.key.A: cam_x += 50
    elif sym == pyglet.window.key.D: cam_x -= 50
    elif sym == pyglet.window.key.ESCAPE: pyglet.app.exit()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
