"""Tests for dialogue system."""
from game.dialogue.dialogue import DialogueTree, DialogueNode, DialogueChoice


class TestDialogueNode:
    def test_node_creation(self):
        node = DialogueNode("start", "NPC", "Hello!")
        assert node.node_id == "start"
        assert node.speaker == "NPC"
        assert node.text == "Hello!"

    def test_add_choice(self):
        node = DialogueNode("start", "NPC", "Hello!")
        choice = DialogueChoice("Hi!", next_node="greet")
        node.add_choice(choice)
        assert len(node.choices) == 1

    def test_available_choices(self):
        node = DialogueNode("start")
        c1 = DialogueChoice("Yes")
        c2 = DialogueChoice("No")
        c2.condition = lambda: False
        node.add_choice(c1)
        node.add_choice(c2)
        available = node.get_available_choices()
        assert len(available) == 1
        assert available[0].text == "Yes"


class TestDialogueTree:
    def test_tree_creation(self):
        tree = DialogueTree(name="Merchant")
        assert tree.name == "Merchant"
        assert tree.is_active is False

    def test_start(self):
        tree = DialogueTree()
        node = DialogueNode("start", "NPC", "Hello!")
        tree.add_node(node)
        assert tree.start("start") is True
        assert tree.is_active is True
        assert tree.current_node.text == "Hello!"

    def test_start_invalid_node(self):
        tree = DialogueTree()
        assert tree.start("nonexistent") is False

    def test_choose(self):
        tree = DialogueTree()
        n1 = DialogueNode("start", "NPC", "Hello!")
        n2 = DialogueNode("greet", "NPC", "How are you?")
        n1.add_choice(DialogueChoice("Hi!", next_node="greet"))
        tree.add_node(n1)
        tree.add_node(n2)
        tree.start("start")
        tree.choose(0)
        assert tree.current_node.node_id == "greet"

    def test_choose_ends_on_empty_next(self):
        tree = DialogueTree()
        node = DialogueNode("start", "NPC", "Bye!")
        node.add_choice(DialogueChoice("Goodbye", next_node=""))
        tree.add_node(node)
        tree.start("start")
        tree.choose(0)
        assert tree.is_active is False

    def test_advance_auto_next(self):
        tree = DialogueTree()
        n1 = DialogueNode("start", "NPC", "Line 1")
        n1.auto_next = "next"
        n2 = DialogueNode("next", "NPC", "Line 2")
        tree.add_node(n1)
        tree.add_node(n2)
        tree.start("start")
        tree.advance()
        assert tree.current_node.node_id == "next"

    def test_on_end_callback(self):
        called = []
        tree = DialogueTree()
        node = DialogueNode("start", "NPC", "Bye!")
        tree.add_node(node)
        tree.on_end(lambda: called.append(True))
        tree.start("start")
        tree.end()
        assert called == [True]
