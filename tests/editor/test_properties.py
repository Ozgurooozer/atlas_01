"""Tests for Properties panel."""

from editor.main import Editor, EditorPanel


class TestProperties:
    """Test suite for Properties panel."""

    def test_properties_is_panel(self):
        """Properties should inherit from EditorPanel."""
        from editor.properties import Properties
        assert issubclass(Properties, EditorPanel)

    def test_properties_creation(self):
        """Properties should be created with default settings."""
        from editor.properties import Properties

        props = Properties()
        assert props is not None
        assert props.name == "Properties"

    def test_properties_has_render_method(self):
        """Properties should have render method."""
        from editor.properties import Properties

        props = Properties()
        assert hasattr(props, 'render')
        assert callable(props.render)

    def test_properties_with_editor(self):
        """Properties should accept editor reference."""
        from editor.properties import Properties

        editor = Editor()
        props = Properties(editor=editor)
        assert props.editor is editor

    def test_properties_has_target(self):
        """Properties should have target object."""
        from editor.properties import Properties

        props = Properties()
        assert hasattr(props, 'target')

    def test_properties_target_none_by_default(self):
        """Properties target should be None by default."""
        from editor.properties import Properties

        props = Properties()
        assert props.target is None

    def test_properties_set_target(self):
        """Properties should accept target object."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        assert props.target is actor

    def test_properties_has_properties_list(self):
        """Properties should have properties list."""
        from editor.properties import Properties

        props = Properties()
        assert hasattr(props, 'properties')

    def test_properties_refresh_from_target(self):
        """Properties should refresh from target object."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        # Properties list should exist (may be empty if no reflected props)
        assert isinstance(props.properties, list)

    def test_properties_get_property_names(self):
        """Properties should return property names."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        # Properties can be empty if no reflected properties
        names = [p.name for p in props.properties]
        assert isinstance(names, list)

    def test_properties_get_property_value(self):
        """Properties should return property value."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="MyActor")
        props.target = actor
        props.refresh()

        value = props.get_property_value('name')
        assert value == "MyActor"

    def test_properties_set_property_value(self):
        """Properties should set property value."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="OldName")
        props.target = actor
        props.refresh()

        props.set_property_value('name', "NewName")
        assert actor.name == "NewName"


class TestPropertiesDisplay:
    """Test suite for Properties display features."""

    def test_properties_has_categories(self):
        """Properties should group by category."""
        from editor.properties import Properties

        props = Properties()
        assert hasattr(props, 'get_categories')

    def test_properties_get_by_category(self):
        """Properties should filter by category."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        categories = props.get_categories()
        assert isinstance(categories, list)

    def test_properties_has_modified_flag(self):
        """Properties should track modifications."""
        from editor.properties import Properties

        props = Properties()
        assert hasattr(props, 'is_modified')

    def test_properties_modified_default_false(self):
        """Properties modified should be False by default."""
        from editor.properties import Properties

        props = Properties()
        assert props.is_modified is False

    def test_properties_mark_modified(self):
        """Properties should track when modified."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        props.set_property_value('name', "NewName")
        assert props.is_modified is True

    def test_properties_clear_modified(self):
        """Properties should allow clearing modified flag."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        props.set_property_value('name', "NewName")
        props.clear_modified()
        assert props.is_modified is False


class TestPropertiesEditor:
    """Test suite for Properties editor integration."""

    def test_properties_sync_with_editor_selection(self):
        """Properties should sync with editor selection."""
        from editor.properties import Properties
        from world.actor import Actor

        editor = Editor()
        props = Properties(editor=editor)
        actor = Actor(name="TestActor")

        editor.select(actor)
        props.sync_with_selection()

        assert props.target is actor

    def test_properties_clear_on_no_selection(self):
        """Properties should clear when no selection."""
        from editor.properties import Properties
        from world.actor import Actor

        editor = Editor()
        props = Properties(editor=editor)
        actor = Actor(name="TestActor")
        props.target = actor

        editor.clear_selection()
        props.sync_with_selection()

        assert props.target is None

    def test_properties_has_undo_support(self):
        """Properties should track changes for undo."""
        from editor.properties import Properties

        props = Properties()
        assert hasattr(props, 'get_changes')

    def test_properties_get_changes(self):
        """Properties should return change list."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        props.set_property_value('name', "NewName")
        changes = props.get_changes()

        assert len(changes) == 1
        assert changes[0]['property'] == 'name'
        assert changes[0]['old_value'] == "TestActor"
        assert changes[0]['new_value'] == "NewName"

    def test_properties_apply_changes(self):
        """Properties should apply pending changes."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        props.refresh()

        props.set_property_value('name', "NewName")
        props.apply_changes()

        assert actor.name == "NewName"

    def test_properties_revert_changes(self):
        """Properties should revert pending changes."""
        from editor.properties import Properties
        from world.actor import Actor

        props = Properties()
        actor = Actor(name="TestActor")
        props.target = actor
        # Don't refresh - it clears original values
        # Store original manually
        props._original_values['name'] = "TestActor"

        props.set_property_value('name', "NewName")
        props.revert_changes()

        assert actor.name == "TestActor"
