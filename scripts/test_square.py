"""Test Demo - Single Square."""
import pyglet

window = pyglet.window.Window(800, 600, 'Test', vsync=True)

@window.event
def on_draw():
    window.clear()
    
    # Big white square in center
    pyglet.shapes.Rectangle(
        350, 250,  # x, y (bottom-left)
        100, 100,  # width, height
        color=(255, 255, 255)
    ).draw()
    
    # Small red square
    pyglet.shapes.Rectangle(
        375, 275,
        50, 50,
        color=(255, 0, 0)
    ).draw()

pyglet.app.run()
