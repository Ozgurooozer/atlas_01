"""
Puzzle Demo Game.

A match-3 puzzle game demonstrating engine features:
- Grid board with colored gems
- Selection and swapping mechanics
- Match detection (3+ in a row)
- Gravity and falling gems
- Undo/Redo system
- Save/Load game state
- Score tracking

Layer: Game (uses all engine layers)
Dependencies: engine, world, core
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Set, Tuple

from core.vec import Vec2
from engine.engine import Engine
from engine.input.input_handler import InputHandler
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.camera import Camera
from world.world import World
from hal.headless import HeadlessGPU


class Gem:
    """
    A colored gem in the puzzle grid.

    Attributes:
        color: The color of the gem (e.g., "red", "blue", "green")
    """

    VALID_COLORS = ["red", "blue", "green", "yellow", "purple", "orange"]

    def __init__(self, color: str = None):
        """Create a gem with optional color."""
        self._color = color or self._random_color()

    @property
    def color(self) -> str:
        """Get gem color."""
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        """Set gem color."""
        self._color = value

    @staticmethod
    def _random_color() -> str:
        """Get a random valid color."""
        import random
        return random.choice(Gem.VALID_COLORS)

    def serialize(self) -> Dict[str, Any]:
        """Serialize gem to dictionary."""
        return {"color": self._color}

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "Gem":
        """Deserialize gem from dictionary."""
        return cls(color=data.get("color"))


class Grid:
    """
    8x8 grid of gems for the puzzle game.

    Provides:
    - Gem placement and retrieval
    - Match detection
    - Gravity simulation
    """

    def __init__(self, width: int = 8, height: int = 8):
        """Create an empty grid."""
        self._width = width
        self._height = height
        self._gems: List[List[Optional[Gem]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    @property
    def width(self) -> int:
        """Get grid width."""
        return self._width

    @property
    def height(self) -> int:
        """Get grid height."""
        return self._height

    def get_gem(self, x: int, y: int) -> Optional[Gem]:
        """Get gem at position (x, y)."""
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._gems[y][x]
        return None

    def set_gem(self, x: int, y: int, gem: Optional[Gem]) -> None:
        """Set gem at position (x, y)."""
        if 0 <= x < self._width and 0 <= y < self._height:
            self._gems[y][x] = gem

    def populate(self, avoid_matches: bool = True) -> None:
        """Fill grid with random gems, optionally avoiding initial matches."""
        for y in range(self._height):
            for x in range(self._width):
                if avoid_matches:
                    # Get colors that would create a match
                    forbidden = self._get_forbidden_colors(x, y)
                    available = [c for c in Gem.VALID_COLORS if c not in forbidden]
                    color = available[0] if available else Gem.VALID_COLORS[0]
                else:
                    color = None  # Will use random

                self._gems[y][x] = Gem(color)

    def _get_forbidden_colors(self, x: int, y: int) -> Set[str]:
        """Get colors that would create a match at position."""
        forbidden = set()

        # Check horizontal (left side)
        if x >= 2:
            left1 = self.get_gem(x - 1, y)
            left2 = self.get_gem(x - 2, y)
            if left1 and left2 and left1.color == left2.color:
                forbidden.add(left1.color)

        # Check vertical (below)
        if y >= 2:
            down1 = self.get_gem(x, y - 1)
            down2 = self.get_gem(x, y - 2)
            if down1 and down2 and down1.color == down2.color:
                forbidden.add(down1.color)

        return forbidden

    def find_matches(self) -> List[List[Tuple[int, int]]]:
        """Find all matches (3+ in a row/column)."""
        matches = []
        visited = set()

        # Check horizontal matches
        for y in range(self._height):
            x = 0
            while x < self._width:
                gem = self.get_gem(x, y)
                if gem is None:
                    x += 1
                    continue

                # Count consecutive same-color gems
                match = [(x, y)]
                next_x = x + 1
                while next_x < self._width:
                    next_gem = self.get_gem(next_x, y)
                    if next_gem and next_gem.color == gem.color:
                        match.append((next_x, y))
                        next_x += 1
                    else:
                        break

                if len(match) >= 3:
                    matches.append(match)
                    for pos in match:
                        visited.add(pos)

                x = next_x

        # Check vertical matches
        for x in range(self._width):
            y = 0
            while y < self._height:
                gem = self.get_gem(x, y)
                if gem is None:
                    y += 1
                    continue

                # Count consecutive same-color gems
                match = [(x, y)]
                next_y = y + 1
                while next_y < self._height:
                    next_gem = self.get_gem(x, next_y)
                    if next_gem and next_gem.color == gem.color:
                        match.append((x, next_y))
                        next_y += 1
                    else:
                        break

                if len(match) >= 3:
                    # Check if this match overlaps with a horizontal one
                    # If so, merge them
                    merged = False
                    for existing in matches:
                        if any(pos in existing for pos in match):
                            # Merge positions
                            for pos in match:
                                if pos not in existing:
                                    existing.append(pos)
                            merged = True
                            break
                    if not merged:
                        matches.append(match)

                y = next_y

        return matches

    def remove_gems(self, positions: List[Tuple[int, int]]) -> None:
        """Remove gems at given positions."""
        for x, y in positions:
            self._gems[y][x] = None

    def apply_gravity(self) -> None:
        """Make gems fall to fill empty spaces."""
        for x in range(self._width):
            # Collect non-empty gems from bottom to top
            gems = []
            for y in range(self._height):
                gem = self.get_gem(x, y)
                if gem is not None:
                    gems.append(gem)

            # Fill from bottom with collected gems
            for y in range(self._height):
                if y < len(gems):
                    self._gems[y][x] = gems[y]
                else:
                    # Spawn new gems at top
                    self._gems[y][x] = Gem()

    def serialize(self) -> List[List[Optional[Dict]]]:
        """Serialize grid to nested list."""
        return [
            [self._gems[y][x].serialize() if self._gems[y][x] else None
             for x in range(self._width)]
            for y in range(self._height)
        ]

    @classmethod
    def deserialize(cls, data: List[List[Optional[Dict]]]) -> "Grid":
        """Deserialize grid from nested list."""
        height = len(data)
        width = len(data[0]) if height > 0 else 0
        grid = cls(width, height)
        for y, row in enumerate(data):
            for x, gem_data in enumerate(row):
                if gem_data:
                    grid._gems[y][x] = Gem.deserialize(gem_data)
        return grid

    def copy(self) -> "Grid":
        """Create a deep copy of this grid."""
        new_grid = Grid(self._width, self._height)
        for y in range(self._height):
            for x in range(self._width):
                gem = self._gems[y][x]
                if gem:
                    new_grid._gems[y][x] = Gem(gem.color)
        return new_grid


class UndoSystem:
    """
    Simple undo/redo system using state snapshots.

    Stores grid states, score, and moves for each action.
    """

    def __init__(self, max_history: int = 100):
        """Create undo system with max history size."""
        self._max_history = max_history
        self._history: List[Dict[str, Any]] = []
        self._current_index: int = -1

    def push(self, state: Dict[str, Any]) -> None:
        """Push a new state onto the history."""
        # Remove any redo states
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]

        # Add new state
        self._history.append(copy.deepcopy(state))

        # Trim if needed
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        self._current_index = len(self._history) - 1

    def undo(self) -> Optional[Dict[str, Any]]:
        """Undo and return previous state."""
        if self._current_index > 0:
            self._current_index -= 1
            return copy.deepcopy(self._history[self._current_index])
        return None

    def redo(self) -> Optional[Dict[str, Any]]:
        """Redo and return next state."""
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            return copy.deepcopy(self._history[self._current_index])
        return None

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._current_index > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._current_index < len(self._history) - 1


class PuzzleGame:
    """
    Match-3 Puzzle demo game.

    Demonstrates:
    - Grid-based game logic
    - Match detection algorithms
    - Undo/Redo pattern
    - Save/Load with serialization
    - Event-driven scoring

    Example:
        >>> game = PuzzleGame()
        >>> game.initialize()
        >>> game.click_cell(0, 0)  # Select gem
        >>> game.click_cell(1, 0)  # Swap with adjacent
        >>> game.process_matches()  # Remove matches
    """

    def __init__(self):
        """Create game instance."""
        self._engine: Optional[Engine] = None
        self._world: Optional[World] = None
        self._grid: Optional[Grid] = None
        self._camera: Optional[Camera] = None

        self._selected_position: Optional[Tuple[int, int]] = None
        self._score: int = 0
        self._moves: int = 0

        self._undo_system: UndoSystem = UndoSystem()
        self._initialized: bool = False

        # For rendering
        self._cell_size: int = 64
        self._sprites: List[List[Optional[Sprite]]] = []

    @property
    def engine(self) -> Optional[Engine]:
        """Get engine."""
        return self._engine

    @property
    def world(self) -> Optional[World]:
        """Get world."""
        return self._world

    @property
    def grid(self) -> Optional[Grid]:
        """Get grid."""
        return self._grid

    @property
    def camera(self) -> Optional[Camera]:
        """Get camera."""
        return self._camera

    @property
    def selected_position(self) -> Optional[Tuple[int, int]]:
        """Get selected position."""
        return self._selected_position

    @selected_position.setter
    def selected_position(self, value: Optional[Tuple[int, int]]) -> None:
        """Set selected position."""
        self._selected_position = value

    @property
    def score(self) -> int:
        """Get score."""
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        """Set score."""
        self._score = value

    @property
    def moves(self) -> int:
        """Get move count."""
        return self._moves

    @moves.setter
    def moves(self, value: int) -> None:
        """Set move count."""
        self._moves = value

    def initialize(self) -> None:
        """Initialize game."""
        # Create engine
        self._engine = Engine()

        # Create and register subsystems
        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        self._engine.register_subsystem(renderer)

        input_handler = InputHandler()
        self._engine.register_subsystem(input_handler)

        # Initialize engine
        self._engine.initialize()

        # Create world
        self._world = World(name="PuzzleWorld")

        # Create grid
        self._grid = Grid(8, 8)
        self._grid.populate(avoid_matches=True)

        # Create camera
        self._camera = Camera()
        self._camera.viewport_width = 800
        self._camera.viewport_height = 600
        self._camera.position = Vec2(256.0, 256.0)  # Center of 8x8 grid with 64px cells

        # Save initial state
        self._save_undo_state()

        self._initialized = True

    def _get_gem_color_rgba(self, color: str) -> Tuple[int, int, int, int]:
        """Convert color name to RGBA tuple."""
        colors = {
            "red": (255, 80, 80, 255),
            "blue": (80, 80, 255, 255),
            "green": (80, 200, 80, 255),
            "yellow": (255, 255, 80, 255),
            "purple": (180, 80, 255, 255),
            "orange": (255, 180, 80, 255),
        }
        return colors.get(color, (200, 200, 200, 255))

    def click_cell(self, x: int, y: int) -> None:
        """Handle click on a grid cell."""
        if self._selected_position is None:
            # No selection, select this cell
            self._selected_position = (x, y)
        elif self._selected_position == (x, y):
            # Clicking same cell, deselect
            self._selected_position = None
        elif self._is_adjacent(self._selected_position, (x, y)):
            # Adjacent cell, swap
            self._swap_gems(self._selected_position, (x, y))
            self._selected_position = None
        else:
            # Non-adjacent cell, select new cell
            self._selected_position = (x, y)

    def _is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Check if two positions are adjacent (horizontally or vertically)."""
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

    def _swap_gems(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> None:
        """Swap two gems."""
        gem1 = self._grid.get_gem(pos1[0], pos1[1])
        gem2 = self._grid.get_gem(pos2[0], pos2[1])

        self._grid.set_gem(pos1[0], pos1[1], gem2)
        self._grid.set_gem(pos2[0], pos2[1], gem1)

        self._moves += 1

        # Process any matches
        self.process_matches()

        # Save state AFTER swap is complete for undo
        self._save_undo_state()

    def process_matches(self) -> None:
        """Find and remove all matches, apply gravity, and score."""
        matches = self._grid.find_matches()

        if not matches:
            return

        # Calculate score (10 points per gem, bonus for larger matches)
        for match in matches:
            base_score = len(match) * 10
            # Bonus for matches larger than 3
            if len(match) > 3:
                base_score += (len(match) - 3) * 20
            self._score += base_score

            # Remove matched gems
            self._grid.remove_gems(match)

        # Apply gravity to make gems fall
        self.apply_gravity()

    def apply_gravity(self) -> None:
        """Apply gravity to make gems fall into empty spaces."""
        self._grid.apply_gravity()

    def _save_undo_state(self) -> None:
        """Save current state for undo."""
        state = {
            "grid": self._grid.serialize(),
            "score": self._score,
            "moves": self._moves,
            "selected": self._selected_position,
        }
        self._undo_system.push(state)

    def undo(self) -> bool:
        """Undo the last move."""
        state = self._undo_system.undo()
        if state:
            self._load_state(state)
            return True
        return False

    def redo(self) -> bool:
        """Redo the last undone move."""
        state = self._undo_system.redo()
        if state:
            self._load_state(state)
            return True
        return False

    def _load_state(self, state: Dict[str, Any]) -> None:
        """Load a state from dictionary."""
        self._grid = Grid.deserialize(state["grid"])
        self._score = state["score"]
        self._moves = state["moves"]
        self._selected_position = state.get("selected")

    def save_state(self) -> Dict[str, Any]:
        """Save game state for persistence."""
        return {
            "grid": self._grid.serialize(),
            "score": self._score,
            "moves": self._moves,
            "selected": self._selected_position,
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        """Load game state from persistence."""
        self._grid = Grid.deserialize(state["grid"])
        self._score = state["score"]
        self._moves = state["moves"]
        self._selected_position = state.get("selected")

        # Save to undo system
        self._undo_system.push(state)

    def update(self, dt: float) -> None:
        """Update game state."""
        if not self._initialized:
            return

        # Update world
        self._world.tick(dt)

    def render(self) -> None:
        """Render game."""
        if not self._initialized:
            return

        renderer = self._engine.get_subsystem("renderer")
        if renderer:
            renderer.clear(0.1, 0.1, 0.15, 1.0)  # Dark background

            # Draw grid background and gems
            for y in range(self._grid.height):
                for x in range(self._grid.width):
                    gem = self._grid.get_gem(x, y)
                    if gem:
                        # Create colored texture for gem
                        color = self._get_gem_color_rgba(gem.color)
                        texture = Texture.from_color(56, 56, color)

                        # Position gem (offset by selection)
                        pos_x = x * self._cell_size + self._cell_size // 2
                        pos_y = y * self._cell_size + self._cell_size // 2

                        sprite = Sprite(texture=texture, position=Vec2(pos_x, pos_y))
                        sprite.anchor_x = 0.5
                        sprite.anchor_y = 0.5

                        renderer.draw_sprite(sprite)

            renderer.present()

    def tick(self, dt: float) -> None:
        """Main game tick."""
        self.update(dt)
        self.render()

    def run(self, duration: float = 10.0, dt: float = 0.016) -> None:
        """Run game for a duration."""
        if not self._initialized:
            self.initialize()

        elapsed = 0.0
        while elapsed < duration:
            self.tick(dt)
            elapsed += dt
