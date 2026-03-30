"""
Tests for StateMachine - Hierarchical State Machine.

StateMachine provides game logic organization:
- States with enter/exit/tick lifecycle
- Transitions between states
- Hierarchical (nested) states
- History states (optional)

Layer: 5 (Scripting)
Dependencies: core.object
"""

import pytest
from scripting.statemachine import State, StateMachine


class TestStateBasics:
    """Test State base class."""

    def test_state_has_name(self):
        """State should have a name property."""
        state = State(name="Idle")
        assert hasattr(state, 'name')
        assert state.name == "Idle"

    def test_state_default_name(self):
        """State should have default name from class."""
        state = State()
        assert state.name == "State"

    def test_state_has_on_enter(self):
        """State should have on_enter method."""
        state = State()
        assert hasattr(state, 'on_enter')
        assert callable(state.on_enter)

    def test_state_has_on_exit(self):
        """State should have on_exit method."""
        state = State()
        assert hasattr(state, 'on_exit')
        assert callable(state.on_exit)

    def test_state_has_tick(self):
        """State should have tick method."""
        state = State()
        assert hasattr(state, 'tick')
        assert callable(state.tick)


class TestStateMachineBasics:
    """Test StateMachine basic functionality."""

    def test_statemachine_creation(self):
        """StateMachine should be creatable with initial state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        assert sm is not None

    def test_statemachine_has_current_state(self):
        """StateMachine should track current state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        assert sm.current_state is initial

    def test_statemachine_has_states_dict(self):
        """StateMachine should have states dictionary."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        assert hasattr(sm, 'states')
        assert isinstance(sm.states, dict)

    def test_statemachine_add_state(self):
        """StateMachine should allow adding states."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)
        assert "Idle" in sm.states
        assert sm.states["Idle"] is idle

    def test_statemachine_has_tick(self):
        """StateMachine should have tick method."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        assert hasattr(sm, 'tick')
        assert callable(sm.tick)


class TestStateTransitions:
    """Test state transition functionality."""

    def test_transition_changes_state(self):
        """Transition should change current state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        sm.transition("Idle")
        assert sm.current_state is idle

    def test_transition_calls_on_exit(self):
        """Transition should call on_exit on old state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        exit_called = []
        initial.on_exit = lambda ctx=None: exit_called.append(True)

        sm.transition("Idle")
        assert len(exit_called) == 1

    def test_transition_calls_on_enter(self):
        """Transition should call on_enter on new state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        enter_called = []
        idle.on_enter = lambda ctx=None: enter_called.append(True)

        sm.transition("Idle")
        assert len(enter_called) == 1

    def test_transition_to_unknown_state_raises(self):
        """Transition to unknown state should raise."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)

        with pytest.raises(KeyError):
            sm.transition("Unknown")

    def test_transition_to_same_state_no_op(self):
        """Transition to same state should be no-op."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)

        exit_count = []
        initial.on_exit = lambda: exit_count.append(True)

        sm.transition("Initial")  # Same state
        assert len(exit_count) == 0


class TestStateMachineTick:
    """Test StateMachine tick functionality."""

    def test_tick_calls_current_state_tick(self):
        """Tick should call current state's tick."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)

        tick_called = []
        initial.tick = lambda dt: tick_called.append(dt)

        sm.tick(0.016)
        assert len(tick_called) == 1
        assert tick_called[0] == 0.016

    def test_tick_after_transition(self):
        """Tick should call new state's tick after transition."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        tick_called = []
        idle.tick = lambda dt: tick_called.append(dt)

        sm.transition("Idle")
        sm.tick(0.016)
        assert len(tick_called) == 1

    def test_multiple_ticks(self):
        """Multiple ticks should work correctly."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)

        tick_count = []
        initial.tick = lambda dt: tick_count.append(dt)

        sm.tick(0.016)
        sm.tick(0.016)
        sm.tick(0.016)
        assert len(tick_count) == 3


class TestStateLifecycle:
    """Test state lifecycle callbacks."""

    def test_on_enter_receives_context(self):
        """on_enter should receive optional context."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        enter_context = []
        idle.on_enter = lambda context=None: enter_context.append(context)

        sm.transition("Idle", context={"reason": "player_input"})
        assert enter_context[0] == {"reason": "player_input"}

    def test_on_exit_receives_context(self):
        """on_exit should receive optional context."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        exit_context = []
        initial.on_exit = lambda context=None: exit_context.append(context)

        sm.transition("Idle", context={"reason": "timeout"})
        assert exit_context[0] == {"reason": "timeout"}


class TestStateMachineStateTracking:
    """Test state tracking and history."""

    def test_is_in_state(self):
        """StateMachine should check if in specific state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)

        assert sm.is_in_state("Initial") is True
        assert sm.is_in_state("Idle") is False

    def test_previous_state(self):
        """StateMachine should track previous state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        sm.transition("Idle")
        assert sm.previous_state is initial

    def test_state_history(self):
        """StateMachine should track state history."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        run = State(name="Run")
        sm.add_state(idle)
        sm.add_state(run)

        sm.transition("Idle")
        sm.transition("Run")

        history = sm.history
        assert "Initial" in history
        assert "Idle" in history
        assert history[-1] == "Run"


class TestStateMachineSerialization:
    """Test StateMachine serialization."""

    def test_serialize_current_state(self):
        """StateMachine should serialize current state name."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)

        data = sm.serialize()
        assert data["current_state"] == "Initial"

    def test_deserialize_state(self):
        """StateMachine should deserialize to correct state."""
        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = State(name="Idle")
        sm.add_state(idle)

        sm.deserialize({"current_state": "Idle"})
        assert sm.current_state is idle


class TestCustomState:
    """Test custom state subclasses."""

    def test_custom_state_subclass(self):
        """Should be able to create custom state subclasses."""

        class IdleState(State):
            def __init__(self):
                super().__init__(name="Idle")
                self.tick_count = 0

            def tick(self, dt: float) -> None:
                self.tick_count += 1

        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        idle = IdleState()
        sm.add_state(idle)

        sm.transition("Idle")
        sm.tick(0.016)
        sm.tick(0.016)

        assert idle.tick_count == 2

    def test_custom_state_with_transition_logic(self):
        """Custom state should be able to trigger transitions."""

        class PatrolState(State):
            def __init__(self, sm: StateMachine):
                super().__init__(name="Patrol")
                self._sm = sm
                self.patrol_time = 0.0

            def tick(self, dt: float) -> None:
                self.patrol_time += dt
                if self.patrol_time > 5.0:
                    if "Chase" in self._sm.states:
                        self._sm.transition("Chase")

        initial = State(name="Initial")
        sm = StateMachine(initial_state=initial)
        patrol = PatrolState(sm)
        chase = State(name="Chase")
        sm.add_state(patrol)
        sm.add_state(chase)

        sm.transition("Patrol")

        # Simulate 5+ seconds
        for _ in range(6):
            sm.tick(1.0)

        assert sm.is_in_state("Chase")
