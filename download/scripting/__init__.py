"""
Scripting Layer - Layer 5

Provides game logic scripting tools:
- StateMachine: Hierarchical State Machine
- BehaviourTree: AI decision making
- Blackboard: AI shared state
- EventGraph: Visual scripting nodes
- Timeline: Sequence/Director

Dependencies: core (Layer 1), world (Layer 3)
"""

from scripting.statemachine import State, StateMachine
from scripting.blackboard import Blackboard

__all__ = [
    'State',
    'StateMachine',
    'Blackboard',
]
