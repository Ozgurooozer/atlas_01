"""Tests for event graph system."""
from scripting.event_graph import (
    Pin, GraphNode, EventNode, ActionGraphNode, BranchNode, EventGraph
)


class TestPin:
    def test_pin_creation(self):
        pin = Pin("value", "float", is_input=True)
        assert pin.name == "value"
        assert pin.is_input is True

    def test_pin_value(self):
        pin = Pin("x")
        pin.value = 42
        assert pin.value == 42

    def test_pin_connect(self):
        out_pin = Pin("out", is_input=False)
        in_pin = Pin("in", is_input=True)
        out_pin.value = 99
        assert in_pin.connect(out_pin) is True
        assert in_pin.value == 99

    def test_same_direction_connect_fails(self):
        p1 = Pin("a", is_input=True)
        p2 = Pin("b", is_input=True)
        assert p1.connect(p2) is False


class TestGraphNode:
    def test_node_creation(self):
        node = GraphNode("TestNode")
        assert node.name == "TestNode"

    def test_add_pins(self):
        node = GraphNode()
        node.add_input("x")
        node.add_output("result")
        assert node.get_input("x") is not None
        assert node.get_output("result") is not None

    def test_set_next(self):
        n1 = GraphNode("A")
        n2 = GraphNode("B")
        n1.set_next(n2)
        assert n1.next_node is n2


class TestEventGraph:
    def test_trigger_event(self):
        called = []
        graph = EventGraph()
        entry = EventNode("on_start")
        action = ActionGraphNode("act", lambda: called.append(True))
        entry.set_next(action)
        graph.register_event("on_start", entry)
        graph.trigger("on_start")
        assert called == [True]

    def test_trigger_nonexistent(self):
        graph = EventGraph()
        assert graph.trigger("nonexistent") is False

    def test_has_event(self):
        graph = EventGraph()
        entry = EventNode("test")
        graph.register_event("test", entry)
        assert graph.has_event("test") is True
        assert graph.has_event("other") is False

    def test_branch_node_true(self):
        called = []
        graph = EventGraph()
        entry = EventNode("start")
        branch = BranchNode("branch", lambda: True)
        true_action = ActionGraphNode("true", lambda: called.append("true"))
        false_action = ActionGraphNode("false", lambda: called.append("false"))
        branch.set_true_node(true_action)
        branch.set_false_node(false_action)
        entry.set_next(branch)
        graph.register_event("start", entry)
        graph.trigger("start")
        assert "true" in called
        assert "false" not in called

    def test_chain_execution(self):
        order = []
        graph = EventGraph()
        entry = EventNode("chain")
        a = ActionGraphNode("a", lambda: order.append("a"))
        b = ActionGraphNode("b", lambda: order.append("b"))
        c = ActionGraphNode("c", lambda: order.append("c"))
        entry.set_next(a)
        a.set_next(b)
        b.set_next(c)
        graph.register_event("chain", entry)
        graph.trigger("chain")
        assert order == ["a", "b", "c"]
