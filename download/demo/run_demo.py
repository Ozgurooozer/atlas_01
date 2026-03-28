#!/usr/bin/env python3
"""
Demo Runner - Run the Bouncing Ball demo.

This script demonstrates the game engine in action:
- Creates a game instance
- Runs the game loop
- Prints state updates

Usage:
    python demo/run_demo.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo.bouncing_ball import BouncingBallGame


def main():
    """Run the demo."""
    print("=" * 50)
    print("🎮 BOUNCING BALL DEMO")
    print("=" * 50)
    print()

    # Create game
    print("Creating game...")
    game = BouncingBallGame()

    # Initialize
    print("Initializing engine and subsystems...")
    game.initialize()

    print(f"  ✓ Engine subsystems: {game.engine.subsystem_names}")
    print(f"  ✓ Ball position: ({game.ball.position.x:.1f}, {game.ball.position.y:.1f})")
    print(f"  ✓ Ground Y: {game.ground_y}")
    print()

    # Simulate some frames
    print("Running simulation (100 frames)...")
    print("-" * 50)

    dt = 0.016  # ~60 FPS
    jump_count = 0
    max_jumps = 3

    for frame in range(500):
        # Try to jump when on ground
        if game.ball.on_ground and jump_count < max_jumps and frame % 60 == 0 and frame > 0:
            game.handle_input("SPACE")
            jump_count += 1
            print(f"Frame {frame:3d}: JUMP #{jump_count}! Score: {game.score}")

        # Print state every 50 frames
        if frame % 50 == 0:
            on_ground_str = "G" if game.ball.on_ground else " "
            print(f"Frame {frame:3d}: Ball Y = {game.ball.position.y:6.1f}, Vel Y = {game.ball.velocity.y:7.1f} [{on_ground_str}]")

        # Update game
        game.update(dt)

    print("-" * 50)
    print()
    print("Simulation complete!")
    print(f"  Final score: {game.score}")
    print(f"  Final ball position: ({game.ball.position.x:.1f}, {game.ball.position.y:.1f})")
    print()
    print("=" * 50)
    print("✅ Demo completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
