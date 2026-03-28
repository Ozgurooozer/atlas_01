#!/usr/bin/env python3
"""
Simple Render Test - Direct import
"""

import sys
import os

# Add engine directory to path
engine_path = os.path.join(os.path.dirname(__file__), 'engine')
sys.path.insert(0, engine_path)

try:
    # Direct imports from engine directory
    from engine.renderer.renderer import Renderer2D
    from engine.renderer.sprite import Sprite
    from engine.renderer.texture import Texture
    from engine.renderer.camera import Camera
    from hal.headless import HeadlessGPU
    
    print("=" * 50)
    print("🎨 RENDERING SYSTEM TEST")
    print("=" * 50)
    
    # Create renderer
    print("Creating renderer...")
    renderer = Renderer2D()
    renderer.gpu_device = HeadlessGPU()
    
    # Initialize renderer
    print("Initializing renderer...")
    renderer.initialize()
    
    print("✅ Renderer initialized successfully!")
    print(f"  GPU Device: {type(renderer.gpu_device).__name__}")
    print(f"  Renderer Type: {type(renderer).__name__}")
    
    # Create texture
    print("\nCreating texture...")
    texture = Texture.from_color(64, 64, (255, 0, 0, 255))  # Red texture
    print(f"✅ Texture created: {texture.width}x{texture.height}")
    
    # Create sprite
    print("Creating sprite...")
    sprite = Sprite(texture=texture)
    sprite.position = (100, 100)
    print(f"✅ Sprite created at: {sprite.position}")
    
    # Create camera
    print("Creating camera...")
    camera = Camera()
    camera.viewport_width = 800
    camera.viewport_height = 600
    camera.position = (400, 300)
    print(f"✅ Camera created: {camera.viewport_width}x{camera.viewport_height}")
    
    # Test rendering
    print("\nTesting rendering...")
    renderer.clear(0.1, 0.1, 0.2, 1.0)  # Dark blue background
    renderer.draw_sprite(sprite)
    renderer.present()
    
    print("✅ Rendering test completed!")
    print("\n🎮 Rendering system is working!")
    
    # Show renderer capabilities
    print(f"\n📊 Renderer Info:")
    print(f"  Subsystem name: {renderer.name}")
    print(f"  Initialized: {renderer.initialized}")
    print(f"  Active: {renderer.active}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Engine path:", engine_path)
    print("Python path:", sys.path[:3])
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
