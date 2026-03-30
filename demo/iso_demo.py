"""2.5D Isometric Demo - Working Grid."""
import pyglet
import math

class IsometricDemo:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.cam_x = 0
        self.cam_y = 0
        self.time = 0
        
    def update(self, dt):
        self.time += dt
        
    def render(self):
        window.clear()
        batch = pyglet.graphics.Batch()
        
        # Isometric grid
        grid = 5
        tile = 50
        cx = self.width / 2 + self.cam_x
        cy = self.height / 2 + self.cam_y
        
        for x in range(-grid, grid + 1):
            for y in range(-grid, grid + 1):
                # Isometric projection
                sx = cx + (x - y) * tile
                sy = cy + (x + y) * tile * 0.5
                
                # Checkerboard pattern
                white = (x + y) % 2 == 0
                color = (240, 240, 240) if white else (100, 100, 100)
                
                # Draw tile (as rectangle)
                pyglet.shapes.Rectangle(
                    sx - tile/2, sy - tile/4,
                    tile, tile/2,
                    color=color,
                    batch=batch
                )
        
        # Animated red player
        px = cx + math.sin(self.time * 2) * 80
        py = cy + 30
        
        pyglet.shapes.Rectangle(
            px - 12, py - 12, 24, 24,
            color=(255, 50, 50),
            batch=batch
        )
        
        batch.draw()
        
        pyglet.text.Label(
            'WASD: Move Camera | ESC: Exit',
            font_size=14, x=10, y=10,
            color=(255, 255, 255, 255)
        ).draw()

# Create window
window = pyglet.window.Window(800, 600, '2.5D Isometric', vsync=True)
demo = IsometricDemo(800, 600)

@window.event
def on_draw():
    demo.render()

@window.event  
def on_key_press(sym, mod):
    if sym == pyglet.window.key.W: demo.cam_y -= 40
    elif sym == pyglet.window.key.S: demo.cam_y += 40
    elif sym == pyglet.window.key.A: demo.cam_x += 40
    elif sym == pyglet.window.key.D: demo.cam_x -= 40
    elif sym == pyglet.window.key.ESCAPE: pyglet.app.exit()

pyglet.clock.schedule_interval(demo.update, 1/60)
pyglet.app.run()
