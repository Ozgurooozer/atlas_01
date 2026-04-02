"""Tests for Hierarchy panel."""

from editor.main import Editor, EditorPanel


class TestHierarchy:
    """Test suite for Hierarchy panel."""

    def test_hierarchy_is_panel(self):
        """Hierarchy should inherit from EditorPanel."""
        from editor.hierarchy import Hierarchy
        assert issubclass(Hierarchy, EditorPanel)

    def test_hierarchy_creation(self):
        """Hierarchy should be created with default settings."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hierarchy is not None
        assert hierarchy.name == "Hierarchy"

    def test_hierarchy_has_render_method(self):
        """Hierarchy should have render method."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hasattr(hierarchy, 'render')
        assert callable(hierarchy.render)

    def test_hierarchy_with_editor(self):
        """Hierarchy should accept editor reference."""
        from editor.hierarchy import Hierarchy

        editor = Editor()
        hierarchy = Hierarchy(editor=editor)
        assert hierarchy.editor is editor

    def test_hierarchy_has_world_reference(self):
        """Hierarchy should have world reference."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hasattr(hierarchy, 'world')

    def test_hierarchy_set_world(self):
        """Hierarchy should accept world reference."""
        from editor.hierarchy import Hierarchy
        from world.world import World

        hierarchy = Hierarchy()
        world = World()
        hierarchy.world = world
        assert hierarchy.world is world

    def test_hierarchy_has_root_items(self):
        """Hierarchy should have root items list."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hasattr(hierarchy, 'root_items')

    def test_hierarchy_root_items_empty_by_default(self):
        """Hierarchy root items should be empty by default."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hierarchy.root_items == []

    def test_hierarchy_refresh_from_world(self):
        """Hierarchy should refresh from world."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor1 = Actor(name="Actor1")
        actor2 = Actor(name="Actor2")
        world.spawn_actor(actor1)
        world.spawn_actor(actor2)

        hierarchy.world = world
        hierarchy.refresh()

        assert len(hierarchy.root_items) == 2

    def test_hierarchy_get_item_by_guid(self):
        """Hierarchy should find item by GUID."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="TestActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        item = hierarchy.get_item_by_guid(actor.guid)
        assert item is not None
        assert item['name'] == "TestActor"

    def test_hierarchy_has_selected_item(self):
        """Hierarchy should track selected item."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hasattr(hierarchy, 'selected_item')

    def test_hierarchy_selected_item_none_by_default(self):
        """Hierarchy selected item should be None by default."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hierarchy.selected_item is None

    def test_hierarchy_select_item(self):
        """Hierarchy should allow selecting item."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="TestActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        hierarchy.select_item(actor.guid)
        assert hierarchy.selected_item == actor.guid

    def test_hierarchy_clear_selection(self):
        """Hierarchy should allow clearing selection."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="TestActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()
        hierarchy.select_item(actor.guid)
        hierarchy.clear_selection()

        assert hierarchy.selected_item is None


class TestHierarchyTree:
    """Test suite for Hierarchy tree operations."""

    def test_hierarchy_builds_tree(self):
        """Hierarchy should build tree structure."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()

        parent = Actor(name="Parent")
        child = Actor(name="Child")
        world.spawn_actor(parent)
        world.spawn_actor(child)

        hierarchy.world = world
        hierarchy.refresh()

        # Should have two root items (no parenting yet)
        assert len(hierarchy.root_items) == 2

    def test_hierarchy_item_has_name(self):
        """Hierarchy items should have name."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="MyActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        item = hierarchy.root_items[0]
        assert item['name'] == "MyActor"

    def test_hierarchy_item_has_guid(self):
        """Hierarchy items should have GUID."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="MyActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        item = hierarchy.root_items[0]
        assert item['guid'] == actor.guid

    def test_hierarchy_item_has_children(self):
        """Hierarchy items should have children list."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="MyActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        item = hierarchy.root_items[0]
        assert 'children' in item
        assert item['children'] == []

    def test_hierarchy_item_is_expanded(self):
        """Hierarchy items should have expanded state."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="MyActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        item = hierarchy.root_items[0]
        assert 'expanded' in item

    def test_hierarchy_toggle_expand(self):
        """Hierarchy should toggle item expansion."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()
        actor = Actor(name="MyActor")
        world.spawn_actor(actor)

        hierarchy.world = world
        hierarchy.refresh()

        item_guid = hierarchy.root_items[0]['guid']
        hierarchy.toggle_expand(item_guid)


class TestHierarchyFiltering:
    """Test suite for Hierarchy filtering."""

    def test_hierarchy_has_filter(self):
        """Hierarchy should have filter text."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hasattr(hierarchy, 'filter_text')

    def test_hierarchy_filter_default_empty(self):
        """Hierarchy filter should default to empty."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        assert hierarchy.filter_text == ""

    def test_hierarchy_set_filter(self):
        """Hierarchy should allow setting filter."""
        from editor.hierarchy import Hierarchy

        hierarchy = Hierarchy()
        hierarchy.filter_text = "Test"
        assert hierarchy.filter_text == "Test"

    def test_hierarchy_filter_items(self):
        """Hierarchy should filter items by name."""
        from editor.hierarchy import Hierarchy
        from world.world import World
        from world.actor import Actor

        hierarchy = Hierarchy()
        world = World()

        actor1 = Actor(name="Enemy1")
        actor2 = Actor(name="Player")
        actor3 = Actor(name="Enemy2")
        world.spawn_actor(actor1)
        world.spawn_actor(actor2)
        world.spawn_actor(actor3)

        hierarchy.world = world
        hierarchy.refresh()

        hierarchy.filter_text = "Enemy"
        filtered = hierarchy.get_filtered_items()

        assert len(filtered) == 2
        assert all("Enemy" in item['name'] for item in filtered)
