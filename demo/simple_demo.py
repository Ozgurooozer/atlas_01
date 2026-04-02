"""Simple 2.5D Isometric Visual Demo - Working Version."""
import sys
import math

try:
    import pyglet
    from pyglet import shapes
    from pyglet.window import key
    HAS_PYGLET = True
except ImportError:
    HAS_PYGLET = False

sys.path.insert(0, '.')
from engine.renderer.isometric import IsometricProjection


class SimpleIsoDemo:
    """Simple working isometric demo."""
    
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.iso = IsometricProjection(width, height, tile_size=64)
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.time = 0
        
    def update(self, dt):
        self.time += dt
        
    def render(self):
        if not HAS_PYGLET:
            return
            
        # Dark background
        pyglet.gl.glClearColor(0.05, 0.05, 0.1, 1.0)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        
        batch = pyglet.graphics.Batch()
        
        # Draw isometric grid
        grid_size = 8
        tile_size = 64 * self.zoom
        
        center_x = self.width / 2 + self.camera_x
        center_y = self.height / 2 + self.camera_y
        
        for x in range(-grid_size, grid_size + 1):
            for y in range(-grid_size, grid_size + 1):
                # Isometric projection
                screen_x = center_x + (x - y) * tile_size * 0.5
                screen_y = center_y + (x + y) * tile_size * 0.25
                
                # Color based on position
                r = int(100 + (x + grid_size) * 10)
                g = int(150 + (y + grid_size) * 5)
                b = 80
                
                # Draw diamond tile using lines or multiple shapes
                size = tile_size * 0.5
                
                # Use a rectangle for simplicity
                shapes.Rectangle(
                    screen_x - size * 0.5,
                    screen_y - size * 0.25,
                    size,
                    size * 0.5,
                    color=(r, g, b),
                    batch=batch
                )
        
        # Draw some "trees" (green circles)
        tree_positions = [(2, 2), (-3, 1), (0, -2), (4, -1), (-2, -3)]
        for tx, ty in tree_positions:
            screen_x = center_x + (tx - ty) * tile_size * 0.5
            screen_y = center_y + (tx + ty) * tile_size * 0.25 + 20
            
            shapes.Circle(
                screen_x, screen_y, 15 * self.zoom,
                color=(34, 139, 34),
                batch=batch
            )
        
        # Draw "player" (red circle)
        px, py = 0, 0
        player_x = center_x + (px - py) * tile_size * 0.5
        player_y = center_y + (px + py) * tile_size * 0.25 + 10
        
        shapes.Circle(
            player_x, player_y, 12 * self.zoom,
            color=(220, 50, 50),
            batch=batch
        )
        
        # Draw particles (yellow dots)
        for i in range(10):
            angle = self.time * 2 + i * 0.6
            dist = 30 + math.sin(self.time + i) * 10
            px = player_x + math.cos(angle) * dist
            py = player_y + math.sin(angle) * dist + 20
            
            shapes.Circle(
                px, py, 3,
                color=(255, 215, 0),
                batch=batch
            )
        
        batch.draw()
        
        # Draw UI text
        label = pyglet.text.Label(
            f'WASD: Move | +/-: Zoom | ESC: Exit | Zoom: {self.zoom:.1f}x',
            font_name='Arial',
            font_size=14,
            x=10, y=10,
            color=(255, 255, 255, 255)
        )
        label.draw()


def main():
    if not HAS_PYGLET:
        print("Pyglet not available!")
        return
    
    window = pyglet.window.Window(
        width=1024,
        height=768,
        caption="2.5D Isometric Demo",
        vsync=True
    )
    
    demo = SimpleIsoDemo(1024, 768)
    
    @window.event
    def on_draw():
        demo.render()
    
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            demo.camera_y -= 50
        elif symbol == key.S:
            demo.camera_y += 50
        elif symbol == key.A:
            demo.camera_x += 50
        elif symbol == key.D:
            demo.camera_x -= 50
        elif symbol == key.EQUAL or symbol == key.PLUS:
            demo.zoom = min(3.0, demo.zoom + 0.1)
        elif symbol == key.MINUS:
            demo.zoom = max(0.3, demo.zoom - 0.1)
        elif symbol == key.ESCAPE:
            pyglet.app.exit()
    
    def update(dt):
        demo.update(dt)
    
    pyglet.clock.schedule_interval(update, 1/60.0)
    pyglet.app.run()


if __name__ == "__main__":
    main()
