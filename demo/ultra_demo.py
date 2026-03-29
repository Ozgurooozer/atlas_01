"""Ultra Simple 2.5D Demo - Black & White Squares."""
import sys
import math

try:
    import pyglet
    HAS_PYGLET = True
except ImportError:
    HAS_PYGLET = False

class UltraSimpleDemo:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.cam_x = 0
        self.cam_y = 0
        self.time = 0
        
    def update(self, dt):
        self.time += dt
        
    def render(self):
        if not HAS_PYGLET:
            return
        
        # Clear to black
        pyglet.gl.glClearColor(0, 0, 0, 1)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        
        # Draw white squares in isometric pattern
        batch = pyglet.graphics.Batch()
        
        grid = 6
        size = 40
        
        cx = self.width / 2 + self.cam_x
        cy = self.height / 2 + self.cam_y
        
        for x in range(-grid, grid + 1):
            for y in range(-grid, grid + 1):
                # Isometric position
                sx = cx + (x - y) * size * 0.8
                sy = cy + (x + y) * size * 0.4
                
                # Alternating black/white
                is_white = (x + y) % 2 == 0
                color = (255, 255, 255) if is_white else (100, 100, 100)
                
                # Draw square
                pyglet.shapes.Rectangle(
                    sx - size/2, sy - size/2,
                    size, size,
                    color=color,
                    batch=batch
                )
        
        # Moving red square (player)
        px = cx + math.sin(self.time) * 100
        py = cy + math.cos(self.time * 0.7) * 50 + 50
        
        pyglet.shapes.Rectangle(
            px - 15, py - 15, 30, 30,
            color=(255, 0, 0),
            batch=batch
        )
        
        batch.draw()
        
        # Simple text
        pyglet.text.Label(
            'WASD: Move | ESC: Exit',
            font_size=16, x=10, y=10,
            color=(255, 255, 255, 255)
        ).draw()

def main():
    if not HAS_PYGLET:
        print("Pyglet yok!")
        return
    
    window = pyglet.window.Window(800, 600, '2.5D Demo', vsync=True)
    demo = UltraSimpleDemo(800, 600)
    
    @window.event
    def on_draw():
        demo.render()
    
    @window.event  
    def on_key_press(sym, mod):
        if sym == pyglet.window.key.W: demo.cam_y -= 30
        elif sym == pyglet.window.key.S: demo.cam_y += 30
        elif sym == pyglet.window.key.A: demo.cam_x += 30
        elif sym == pyglet.window.key.D: demo.cam_x -= 30
        elif sym == pyglet.window.key.ESCAPE: pyglet.app.exit()
    
    pyglet.clock.schedule_interval(demo.update, 1/60)
    pyglet.app.run()

if __name__ == "__main__":
    main()
