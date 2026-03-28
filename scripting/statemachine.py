"""
Hierarchical State Machine.

Provides state-based game logic organization.
States have enter/exit/tick lifecycle and can be nested.

Layer: 5 (Scripting)
Dependencies: core.object
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.object import Object

if TYPE_CHECKING:
    pass


class State(Object):
    """
    Base class for all states.

    A State represents a single state in a state machine.
    Override on_enter, on_exit, and tick to implement behavior.

    Example:
        >>> class IdleState(State):
        ...     def on_enter(self):
        ...         print("Entering idle")
        ...
        ...     def tick(self, dt):
        ...         # Check for transitions
        ...         pass

    Attributes:
        name: State name (used for transitions)
    """

    def __init__(self, name: str | None = None) -> None:
        """
        Create a new State.

        Args:
            name: State name. Defaults to class name.
        """
        super().__init__(name=name or "State")

    def on_enter(self, context: Any = None) -> None:
        """
        Called when entering this state.

        Override in subclasses to perform setup.

        Args:
            context: Optional context data for transition.
        """
        pass

    def on_exit(self, context: Any = None) -> None:
        """
        Called when exiting this state.

        Override in subclasses to perform cleanup.

        Args:
            context: Optional context data for transition.
        """
        pass

    def tick(self, dt: float) -> None:
        """
        Called each frame while this state is active.

        Override in subclasses to implement behavior.

        Args:
            dt: Delta time in seconds.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation."""
        return f"State(name={self._name!r})"


class StateMachine(Object):
    """
    Hierarchical State Machine.

    Manages state transitions and lifecycle callbacks.
    States are added with add_state() and transitions
    are triggered with transition().

    Example:
        >>> sm = StateMachine(initial_state=State(name="Idle"))
        >>> sm.add_state(State(name="Run"))
        >>> sm.transition("Run")
        >>> sm.tick(0.016)

    Attributes:
        current_state: The currently active state.
        previous_state: The previous state (None initially).
        states: Dictionary of all states by name.
        history: List of state names visited.
    """

    def __init__(self, initial_state: State) -> None:
        """
        Create a new StateMachine.

        Args:
            initial_state: The starting state.
        """
        super().__init__(name="StateMachine")
        self._current_state: State = initial_state
        self._previous_state: Optional[State] = None
        self._states: Dict[str, State] = {initial_state.name: initial_state}
        self._history: List[str] = [initial_state.name]

    @property
    def current_state(self) -> State:
        """Get current state."""
        return self._current_state

    @property
    def previous_state(self) -> Optional[State]:
        """Get previous state."""
        return self._previous_state

    @property
    def states(self) -> Dict[str, State]:
        """Get all states dictionary."""
        return self._states

    @property
    def history(self) -> List[str]:
        """Get state history."""
        return self._history.copy()

    def add_state(self, state: State) -> None:
        """
        Add a state to the machine.

        Args:
            state: State to add.
        """
        self._states[state.name] = state

    def is_in_state(self, state_name: str) -> bool:
        """
        Check if machine is in specific state.

        Args:
            state_name: Name of state to check.

        Returns:
            True if current state matches.
        """
        return self._current_state.name == state_name

    def transition(
        self,
        state_name: str,
        context: Any = None
    ) -> None:
        """
        Transition to a new state.

        Calls on_exit on current state and on_enter on new state.
        Does nothing if transitioning to same state.

        Args:
            state_name: Name of state to transition to.
            context: Optional context data for callbacks.

        Raises:
            KeyError: If state_name not found.
        """
        # Same state - no-op
        if state_name == self._current_state.name:
            return

        # Get new state
        if state_name not in self._states:
            raise KeyError(f"State '{state_name}' not found")

        new_state = self._states[state_name]

        # Exit current state
        self._current_state.on_exit(context)

        # Update state
        self._previous_state = self._current_state
        self._current_state = new_state

        # Track history
        self._history.append(state_name)

        # Enter new state
        new_state.on_enter(context)

    def tick(self, dt: float) -> None:
        """
        Update current state.

        Args:
            dt: Delta time in seconds.
        """
        self._current_state.tick(dt)

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize state machine state.

        Returns:
            Dictionary with current_state name.
        """
        data = super().serialize()
        data["current_state"] = self._current_state.name
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize state machine state.

        Args:
            data: Dictionary with current_state name.
        """
        super().deserialize(data)
        if "current_state" in data:
            state_name = data["current_state"]
            if state_name in self._states:
                self._current_state = self._states[state_name]

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"StateMachine(current={self._current_state.name}, "
            f"states={list(self._states.keys())})"
        )


__all__ = ['State', 'StateMachine']
