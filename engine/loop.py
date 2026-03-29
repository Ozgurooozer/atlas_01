"""Game Loop System - Core game loop with fixed timestep.

Provides the main game loop with update/render phases and
fixed timestep for consistent physics/logic updates.

Layer: 2 (Engine)
Dependencies: None (Core)
"""
from enum import Enum, auto
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass


class LoopPhase(Enum):
    """Game loop execution phases."""
    STARTUP = "startup"
    UPDATE = "update"
    RENDER = "render"
    SHUTDOWN = "shutdown"


@dataclass
class FixedTimestep:
    """Fixed timestep accumulator for consistent updates.
    
    Accumulates frame time and provides fixed timestep slices
    for physics/logic updates while allowing render interpolation.
    """
    target_fps: float = 60.0
    
    def __post_init__(self):
        self.timestep: float = 1.0 / self.target_fps
        self.accumulator: float = 0.0
    
    def add(self, dt: float) -> None:
        """Add frame time to accumulator."""
        self.accumulator += dt
    
    def consume(self) -> bool:
        """Try to consume one fixed timestep.
        
        Returns:
            True if timestep was consumed
        """
        if self.accumulator >= self.timestep:
            self.accumulator -= self.timestep
            return True
        return False
    
    def get_alpha(self) -> float:
        """Get interpolation alpha for rendering.
        
        Returns:
            Value between 0 and 1 for interpolation
        """
        return min(1.0, self.accumulator / self.timestep)


Handler = Callable[..., Any]


class GameLoop:
    """Main game loop with fixed timestep.
    
    Manages the game lifecycle through phases:
    1. STARTUP - Initialize systems
    2. UPDATE - Fixed timestep logic/physics updates
    3. RENDER - Render with interpolation
    4. SHUTDOWN - Cleanup
    
    Usage:
        loop = GameLoop(target_fps=60)
        loop.on(LoopPhase.UPDATE, update_logic)
        loop.on(LoopPhase.RENDER, render_scene)
        loop.start()
        
        while loop.is_running:
            dt = get_delta_time()
            loop.step(dt)
    """
    
    def __init__(self, target_fps: float = 60.0):
        """Initialize game loop.
        
        Args:
            target_fps: Target update rate for fixed timestep
        """
        self.target_fps = target_fps
        self.timestep = FixedTimestep(target_fps)
        
        self.is_running: bool = False
        self.is_paused: bool = False
        self.current_phase: LoopPhase = LoopPhase.STARTUP
        
        self._handlers: Dict[LoopPhase, List[Handler]] = {
            phase: [] for phase in LoopPhase
        }
        
        self._max_updates_per_frame: int = 5
        self._total_time: float = 0.0
        self._frame_count: int = 0
        self._last_frame_time: float = 0.0
    
    def on(self, phase: LoopPhase, handler: Handler) -> None:
        """Register a handler for a phase.
        
        Args:
            phase: Loop phase to handle
            handler: Callable to invoke
        """
        if handler not in self._handlers[phase]:
            self._handlers[phase].append(handler)
    
    def off(self, phase: LoopPhase, handler: Handler) -> None:
        """Unregister a handler.
        
        Args:
            phase: Loop phase
            handler: Handler to remove
        """
        if handler in self._handlers[phase]:
            self._handlers[phase].remove(handler)
    
    def clear_handlers(self, phase: LoopPhase) -> None:
        """Clear all handlers for a phase.
        
        Args:
            phase: Phase to clear
        """
        self._handlers[phase].clear()
    
    def start(self) -> None:
        """Start the game loop."""
        if self.is_running:
            return
        
        self.is_running = True
        self.current_phase = LoopPhase.STARTUP
        self._total_time = 0.0
        self._frame_count = 0
        
        # Call startup handlers
        self._invoke_handlers(LoopPhase.STARTUP)
        
        self.current_phase = LoopPhase.UPDATE
    
    def stop(self) -> None:
        """Stop the game loop."""
        if not self.is_running:
            return
        
        self.current_phase = LoopPhase.SHUTDOWN
        self._invoke_handlers(LoopPhase.SHUTDOWN)
        self.is_running = False
    
    def pause(self) -> None:
        """Pause the game loop."""
        self.is_paused = True
    
    def resume(self) -> None:
        """Resume the game loop."""
        self.is_paused = False
    
    def step(self, dt: float) -> None:
        """Execute one frame of the game loop.
        
        Args:
            dt: Delta time since last frame
        """
        if not self.is_running:
            return
        
        self._last_frame_time = dt
        self._total_time += dt
        self._frame_count += 1
        
        if self.is_paused:
            # Still render when paused
            self._invoke_handlers(LoopPhase.RENDER, 1.0)
            return
        
        # Add to timestep accumulator
        self.timestep.add(dt)
        
        # Fixed timestep updates
        update_count = 0
        while self.timestep.consume() and update_count < self._max_updates_per_frame:
            self._invoke_handlers(LoopPhase.UPDATE, self.timestep.timestep)
            update_count += 1
        
        # Get interpolation alpha for render
        alpha = self.timestep.get_alpha()
        
        # Render
        self._invoke_handlers(LoopPhase.RENDER, alpha)
    
    def _invoke_handlers(self, phase: LoopPhase, *args: Any) -> None:
        """Invoke all handlers for a phase."""
        for handler in self._handlers[phase]:
            try:
                handler(*args)
            except Exception as e:
                # Log but don't stop other handlers
                print(f"Handler error in {phase.value}: {e}")
    
    def set_max_updates_per_frame(self, max_updates: int) -> None:
        """Set maximum updates per frame (spiral of death prevention).
        
        Args:
            max_updates: Maximum fixed timestep updates per frame
        """
        self._max_updates_per_frame = max(max_updates, 1)
    
    def get_fps(self) -> float:
        """Calculate current FPS.
        
        Returns:
            Average FPS over recent frames
        """
        if self._total_time <= 0:
            return 0.0
        return self._frame_count / self._total_time
    
    def get_frame_time(self) -> float:
        """Get last frame time.
        
        Returns:
            Time delta of last frame
        """
        return self._last_frame_time
    
    def get_total_time(self) -> float:
        """Get total running time.
        
        Returns:
            Total time since start() was called
        """
        return self._total_time
    
    def get_frame_count(self) -> int:
        """Get total frame count.
        
        Returns:
            Number of frames processed
        """
        return self._frame_count
