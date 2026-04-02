"""Tests for Game Loop system.

Test-First Development for Game Loop
"""
import pytest
from engine.loop import GameLoop, LoopPhase, FixedTimestep


class MockHandler:
    """Simple mock handler for testing without unittest.mock."""
    
    def __init__(self):
        self.call_count = 0
        self.calls = []
        self.called = False
    
    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.calls.append((args, kwargs))
        self.called = True
    
    def assert_called_once(self):
        assert self.call_count == 1, f"Expected 1 call, got {self.call_count}"
    
    def assert_not_called(self):
        assert self.call_count == 0, f"Expected no calls, got {self.call_count}"
    
    def reset(self):
        self.call_count = 0
        self.calls = []
        self.called = False


class TestLoopPhase:
    """Test loop phase enum."""
    
    def test_phase_values(self):
        """Test phase enum has correct values."""
        assert LoopPhase.STARTUP.value == "startup"
        assert LoopPhase.UPDATE.value == "update"
        assert LoopPhase.RENDER.value == "render"
        assert LoopPhase.SHUTDOWN.value == "shutdown"


class TestFixedTimestep:
    """Test fixed timestep accumulator."""
    
    def test_initialization(self):
        """Test timestep creation."""
        ts = FixedTimestep(target_fps=60)
        assert ts.target_fps == 60
        assert ts.timestep == pytest.approx(1/60, rel=1e-6)
        assert ts.accumulator == 0.0
    
    def test_add_time(self):
        """Test adding frame time."""
        ts = FixedTimestep(target_fps=60)
        ts.add(1/30)  # 30 FPS frame
        assert ts.accumulator == pytest.approx(1/30, rel=1e-6)
    
    def test_consume_timestep(self):
        """Test consuming fixed timestep."""
        ts = FixedTimestep(target_fps=60)
        ts.add(1/30)  # Add 2 frames worth
        
        consumed = ts.consume()
        assert consumed is True
        assert ts.accumulator == pytest.approx(1/30 - 1/60, rel=1e-6)
        
        consumed = ts.consume()
        assert consumed is True
        assert ts.accumulator == pytest.approx(0, abs=1e-10)
        
        consumed = ts.consume()
        assert consumed is False
    
    def test_get_alpha(self):
        """Test alpha for interpolation."""
        ts = FixedTimestep(target_fps=60)
        ts.add(1/40)  # Halfway between frames
        
        alpha = ts.get_alpha()
        assert 0.0 <= alpha <= 1.0


class TestGameLoop:
    """Test game loop."""
    
    def test_initialization(self):
        """Test loop creation."""
        loop = GameLoop(target_fps=60)
        assert loop.target_fps == 60
        assert loop.is_running is False
        assert loop.current_phase == LoopPhase.STARTUP
    
    def test_start_stop(self):
        """Test starting and stopping."""
        loop = GameLoop()
        
        loop.start()
        assert loop.is_running is True
        
        loop.stop()
        assert loop.is_running is False
        assert loop.current_phase == LoopPhase.SHUTDOWN
    
    def test_register_handlers(self):
        """Test handler registration."""
        loop = GameLoop()
        mock_handler = MockHandler()
        
        loop.on(LoopPhase.UPDATE, mock_handler)
        
        assert mock_handler in loop._handlers[LoopPhase.UPDATE]
    
    def test_unregister_handlers(self):
        """Test handler unregistration."""
        loop = GameLoop()
        mock_handler = MockHandler()
        
        loop.on(LoopPhase.UPDATE, mock_handler)
        loop.off(LoopPhase.UPDATE, mock_handler)
        
        assert mock_handler not in loop._handlers[LoopPhase.UPDATE]
    
    def test_single_update_step(self):
        """Test single update step."""
        loop = GameLoop(target_fps=60)
        update_handler = MockHandler()
        
        loop.on(LoopPhase.UPDATE, update_handler)
        loop.start()
        
        # Simulate one 16ms frame
        loop.step(1/60)
        
        update_handler.assert_called_once()
    
    def test_multiple_fixed_updates(self):
        """Test multiple fixed updates in one frame."""
        loop = GameLoop(target_fps=60)
        update_handler = MockHandler()
        
        loop.on(LoopPhase.UPDATE, update_handler)
        loop.start()
        
        # Large frame time should trigger multiple updates
        loop.step(1/20)  # 3 frames worth
        
        # Should update at least twice
        assert update_handler.call_count >= 2
    
    def test_render_called(self):
        """Test render is called with alpha."""
        loop = GameLoop(target_fps=60)
        render_handler = MockHandler()
        
        loop.on(LoopPhase.RENDER, render_handler)
        loop.start()
        
        loop.step(1/60)
        
        render_handler.assert_called_once()
        args = render_handler.calls[0][0]
        assert len(args) == 1  # alpha value
        assert 0.0 <= args[0] <= 1.0
    
    def test_delta_time_passed_to_update(self):
        """Test delta time is passed to update."""
        loop = GameLoop(target_fps=60)
        update_handler = MockHandler()
        
        loop.on(LoopPhase.UPDATE, update_handler)
        loop.start()
        
        loop.step(1/60)
        
        # Check delta time is approximately timestep
        args = update_handler.calls[0][0]
        assert len(args) == 1  # dt value
        assert args[0] == pytest.approx(1/60, rel=0.1)
    
    def test_get_fps(self):
        """Test FPS calculation."""
        loop = GameLoop()
        
        # Simulate 60 frames
        loop.start()
        for _ in range(60):
            loop.step(1/60)
        
        fps = loop.get_fps()
        assert fps == pytest.approx(60.0, rel=0.1)
    
    def test_get_frame_time(self):
        """Test frame time calculation."""
        loop = GameLoop()
        
        loop.start()
        loop.step(1/60)
        
        frame_time = loop.get_frame_time()
        assert frame_time == pytest.approx(1/60, rel=0.1)
    
    def test_pause_resume(self):
        """Test pause and resume."""
        loop = GameLoop()
        
        loop.start()
        loop.pause()
        assert loop.is_paused is True
        
        update_handler = MockHandler()
        loop.on(LoopPhase.UPDATE, update_handler)
        
        loop.step(1/60)
        # Update should not be called when paused
        update_handler.assert_not_called()
        
        loop.resume()
        assert loop.is_paused is False
    
    def test_get_total_time(self):
        """Test total running time."""
        loop = GameLoop()
        
        loop.start()
        loop.step(1/60)
        loop.step(1/60)
        loop.step(1/60)
        
        total = loop.get_total_time()
        assert total == pytest.approx(3/60, rel=0.01)
    
    def test_set_max_updates_per_frame(self):
        """Test limiting updates per frame."""
        loop = GameLoop(target_fps=60)
        loop.set_max_updates_per_frame(2)
        
        update_handler = MockHandler()
        loop.on(LoopPhase.UPDATE, update_handler)
        loop.start()
        
        # Large frame that would normally trigger many updates
        loop.step(1/10)
        
        # Should be limited to 2
        assert update_handler.call_count <= 2
    
    def test_startup_handler_called(self):
        """Test startup phase handler."""
        loop = GameLoop()
        startup_handler = MockHandler()
        
        loop.on(LoopPhase.STARTUP, startup_handler)
        loop.start()
        
        startup_handler.assert_called_once()
    
    def test_shutdown_handler_called(self):
        """Test shutdown phase handler."""
        loop = GameLoop()
        shutdown_handler = MockHandler()
        
        loop.on(LoopPhase.SHUTDOWN, shutdown_handler)
        loop.start()
        loop.stop()
        
        shutdown_handler.assert_called_once()
    
    def test_clear_handlers(self):
        """Test clearing all handlers for a phase."""
        loop = GameLoop()
        handler1 = MockHandler()
        handler2 = MockHandler()
        
        loop.on(LoopPhase.UPDATE, handler1)
        loop.on(LoopPhase.UPDATE, handler2)
        
        loop.clear_handlers(LoopPhase.UPDATE)
        
        assert handler1 not in loop._handlers[LoopPhase.UPDATE]
        assert handler2 not in loop._handlers[LoopPhase.UPDATE]
