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
from scripting.behaviour_tree import (
    NodeStatus, BTNode, Sequence, Selector, Parallel,
    Inverter, Repeater, ActionNode, ConditionNode, BehaviourTree,
)
from scripting.event_graph import Pin, GraphNode, EventNode, ActionGraphNode, BranchNode, EventGraph
from scripting.timeline import Timeline, TimelineEvent

__all__ = [
    'State', 'StateMachine',
    'Blackboard',
    'NodeStatus', 'BTNode', 'Sequence', 'Selector', 'Parallel',
    'Inverter', 'Repeater', 'ActionNode', 'ConditionNode', 'BehaviourTree',
    'Pin', 'GraphNode', 'EventNode', 'ActionGraphNode', 'BranchNode', 'EventGraph',
    'Timeline', 'TimelineEvent',
]
