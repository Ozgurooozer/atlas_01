"""Tests for behaviour tree system."""
import pytest
from scripting.behaviour_tree import (
    NodeStatus, Sequence, Selector, Parallel,
    Inverter, Repeater, ActionNode, ConditionNode, BehaviourTree
)


class TestActionNode:
    def test_success(self):
        node = ActionNode(lambda: True)
        assert node.tick() == NodeStatus.SUCCESS

    def test_failure_on_false(self):
        node = ActionNode(lambda: False)
        assert node.tick() == NodeStatus.FAILURE

    def test_failure_on_exception(self):
        def bad(): raise ValueError("oops")
        node = ActionNode(bad)
        assert node.tick() == NodeStatus.FAILURE


class TestConditionNode:
    def test_true(self):
        node = ConditionNode(lambda: True)
        assert node.tick() == NodeStatus.SUCCESS

    def test_false(self):
        node = ConditionNode(lambda: False)
        assert node.tick() == NodeStatus.FAILURE


class TestSequence:
    def test_all_success(self):
        seq = Sequence()
        seq.add_child(ActionNode(lambda: True))
        seq.add_child(ActionNode(lambda: True))
        assert seq.tick() == NodeStatus.SUCCESS

    def test_fails_on_first_failure(self):
        seq = Sequence()
        seq.add_child(ActionNode(lambda: False))
        seq.add_child(ActionNode(lambda: True))
        assert seq.tick() == NodeStatus.FAILURE

    def test_empty_sequence(self):
        seq = Sequence()
        assert seq.tick() == NodeStatus.SUCCESS


class TestSelector:
    def test_succeeds_on_first_success(self):
        sel = Selector()
        sel.add_child(ActionNode(lambda: True))
        sel.add_child(ActionNode(lambda: False))
        assert sel.tick() == NodeStatus.SUCCESS

    def test_fails_if_all_fail(self):
        sel = Selector()
        sel.add_child(ActionNode(lambda: False))
        sel.add_child(ActionNode(lambda: False))
        assert sel.tick() == NodeStatus.FAILURE

    def test_skips_to_success(self):
        sel = Selector()
        sel.add_child(ActionNode(lambda: False))
        sel.add_child(ActionNode(lambda: True))
        assert sel.tick() == NodeStatus.SUCCESS


class TestInverter:
    def test_inverts_success(self):
        inv = Inverter(ActionNode(lambda: True))
        assert inv.tick() == NodeStatus.FAILURE

    def test_inverts_failure(self):
        inv = Inverter(ActionNode(lambda: False))
        assert inv.tick() == NodeStatus.SUCCESS


class TestParallel:
    def test_success_threshold(self):
        par = Parallel(success_threshold=2)
        par.add_child(ActionNode(lambda: True))
        par.add_child(ActionNode(lambda: True))
        par.add_child(ActionNode(lambda: False))
        assert par.tick() == NodeStatus.SUCCESS


class TestBehaviourTree:
    def test_tree_tick(self):
        tree = BehaviourTree()
        root = Selector()
        root.add_child(ConditionNode(lambda: False))
        root.add_child(ActionNode(lambda: True))
        tree.set_root(root)
        assert tree.tick() == NodeStatus.SUCCESS

    def test_no_root(self):
        tree = BehaviourTree()
        assert tree.tick() is None

    def test_reset(self):
        tree = BehaviourTree()
        root = Sequence()
        tree.set_root(root)
        tree.reset()  # Should not raise
