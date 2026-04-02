"""
Run Game Mode.

Specialized GameMode for roguelike runs. Bridges Engine loop to RunController.

Layer: 4 (Game/Run)
Dependencies: game.gamemode, game.run.run_controller, engine.loop
"""
from __future__ import annotations
from typing import Any, Dict
from game.gamemode import GameMode
from game.run.run_controller import RunController
from game.run.room import Room


class RunGameMode(GameMode):
    """
    Roguelike run game mode.

    Bridges the Engine game loop to the RunController lifecycle.
    Provides the single game loop contract:
    start_run -> tick -> room_clear -> reward -> next_room -> ... -> boss -> victory
    """

    def __init__(self, seed: int = 42):
        super().__init__(name="RunGameMode")
        self.run_controller = RunController(seed=seed)
        self._setup_run_callbacks()

    def _setup_run_callbacks(self) -> None:
        self.run_controller.on_room_enter(self._on_room_enter)
        self.run_controller.on_room_clear(self._on_room_clear)
        self.run_controller.register_on_death(self._on_run_death)
        self.run_controller.on_victory(self._on_run_victory)

    def on_start(self) -> None:
        """Called when game mode starts."""
        first_room = self.run_controller.start_run()

    def on_tick(self, dt: float) -> None:
        """Called each frame."""
        self.run_controller.tick(dt)
        if self.world:
            self.world.tick(dt)

    def start_new_run(self, seed: int | None = None) -> Room:
        """Start a new run."""
        return self.run_controller.start_run(seed)

    def _on_room_enter(self, room: Room) -> None:
        """Called when entering a new room."""
        pass  # Override in subclass to spawn enemies, setup room

    def _on_room_clear(self, room: Room) -> None:
        """Called when current room is cleared."""
        pass  # Override in subclass for reward generation

    def _on_run_death(self) -> None:
        """Called when player dies."""
        pass  # Override in subclass for death screen

    def _on_run_victory(self) -> None:
        """Called when run is completed (boss cleared)."""
        pass  # Override in subclass for victory screen

    def get_stats(self) -> Dict[str, Any]:
        return self.run_controller.stats

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data["run_controller"] = self.run_controller.serialize()
        return data
