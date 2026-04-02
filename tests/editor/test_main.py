"""Tests for Editor application entry point."""

from core.object import Object


class TestEditor:
    """Test suite for Editor class."""

    def test_editor_is_object(self):
        """Editor should inherit from Object."""
        from editor.main import Editor
        assert issubclass(Editor, Object)

    def test_editor_creation(self):
        """Editor should be created with optional engine reference."""
        from editor.main import Editor
        editor = Editor()
        assert editor is not None

    def test_editor_with_engine(self):
        """Editor should accept engine reference."""
        from editor.main import Editor
        from engine.engine import Engine

        engine = Engine()
        editor = Editor(engine=engine)
        assert editor.engine is engine

    def test_editor_has_guid(self):
        """Editor should have a GUID as Object."""
        from editor.main import Editor
        from core.guid import GUID

        editor = Editor()
        assert hasattr(editor, 'guid')
        assert isinstance(editor.guid, GUID)

    def test_editor_has_name(self):
        """Editor should have a name."""
        from editor.main import Editor

        editor = Editor(name="TestEditor")
        assert editor.name == "TestEditor"

    def test_editor_default_name(self):
        """Editor should have default name."""
        from editor.main import Editor

        editor = Editor()
        assert editor.name == "Editor"

    def test_editor_context(self):
        """Editor should have DearPyGui context management."""
        from editor.main import Editor

        editor = Editor()
        # Context should be created on initialization or first use
        assert hasattr(editor, '_context_created')

    def test_editor_run_method(self):
        """Editor should have run method."""
        from editor.main import Editor

        editor = Editor()
        assert hasattr(editor, 'run')
        assert callable(editor.run)

    def test_editor_shutdown_method(self):
        """Editor should have shutdown method."""
        from editor.main import Editor

        editor = Editor()
        assert hasattr(editor, 'shutdown')
        assert callable(editor.shutdown)

    def test_editor_selection(self):
        """Editor should track selected object."""
        from editor.main import Editor

        editor = Editor()
        assert hasattr(editor, 'selected_object')
        assert editor.selected_object is None

    def test_editor_set_selection(self):
        """Editor should allow setting selected object."""
        from editor.main import Editor
        from world.actor import Actor

        editor = Editor()
        actor = Actor(name="TestActor")
        editor.select(actor)
        assert editor.selected_object is actor

    def test_editor_clear_selection(self):
        """Editor should allow clearing selection."""
        from editor.main import Editor
        from world.actor import Actor

        editor = Editor()
        actor = Actor(name="TestActor")
        editor.select(actor)
        editor.clear_selection()
        assert editor.selected_object is None

    def test_editor_panels_registry(self):
        """Editor should have panels registry."""
        from editor.main import Editor

        editor = Editor()
        assert hasattr(editor, '_panels')
        assert isinstance(editor._panels, dict)

    def test_editor_register_panel(self):
        """Editor should allow registering panels."""
        from editor.main import Editor

        editor = Editor()

        class MockPanel:
            name = "TestPanel"

            def render(self):
                pass

        editor.register_panel(MockPanel())
        assert "TestPanel" in editor._panels

    def test_editor_unregister_panel(self):
        """Editor should allow unregistering panels."""
        from editor.main import Editor

        editor = Editor()

        class MockPanel:
            name = "TestPanel"

            def render(self):
                pass

        panel = MockPanel()
        editor.register_panel(panel)
        editor.unregister_panel("TestPanel")
        assert "TestPanel" not in editor._panels


class TestEditorPanel:
    """Test suite for EditorPanel base class."""

    def test_panel_is_object(self):
        """EditorPanel should inherit from Object."""
        from editor.main import EditorPanel
        assert issubclass(EditorPanel, Object)

    def test_panel_has_name(self):
        """Panel should have a name."""
        from editor.main import EditorPanel

        panel = EditorPanel(name="TestPanel")
        assert panel.name == "TestPanel"

    def test_panel_has_render_method(self):
        """Panel should have render method."""
        from editor.main import EditorPanel

        panel = EditorPanel(name="TestPanel")
        assert hasattr(panel, 'render')
        assert callable(panel.render)

    def test_panel_has_visible_flag(self):
        """Panel should have visible flag."""
        from editor.main import EditorPanel

        panel = EditorPanel(name="TestPanel")
        assert hasattr(panel, 'visible')
        assert panel.visible is True

    def test_panel_set_visible(self):
        """Panel visibility should be toggleable."""
        from editor.main import EditorPanel

        panel = EditorPanel(name="TestPanel")
        panel.visible = False
        assert panel.visible is False

    def test_panel_has_editor_reference(self):
        """Panel should have optional editor reference."""
        from editor.main import EditorPanel, Editor

        editor = Editor()
        panel = EditorPanel(name="TestPanel", editor=editor)
        assert panel.editor is editor


class TestEditorIntegration:
    """Integration tests for Editor with Engine."""

    def test_editor_with_full_engine(self):
        """Editor should work with fully configured engine."""
        from editor.main import Editor
        from engine.engine import Engine

        engine = Engine()
        editor = Editor(engine=engine)
        assert editor.engine is engine

    def test_editor_reflection_properties(self):
        """Editor should have reflection properties via Object."""
        from editor.main import Editor
        from core.reflection import get_properties

        editor = Editor(name="TestEditor")
        # Object has name property which may be reflected
        props = get_properties(editor)
        # Just verify no errors occur
        assert isinstance(props, list)

    def test_editor_multiple_instances(self):
        """Multiple editor instances should have unique GUIDs."""
        from editor.main import Editor

        editor1 = Editor()
        editor2 = Editor()
        assert editor1.guid != editor2.guid

    def test_editor_flags(self):
        """Editor should support Object flags."""
        from editor.main import Editor

        editor = Editor()
        # Object uses integer flags with bitwise operations
        editor.flags = 1  # Set flag bit
        assert editor.flags == 1

    def test_editor_with_world_selection(self):
        """Editor should select actors from world."""
        from editor.main import Editor
        from engine.engine import Engine
        from world.world import World
        from world.actor import Actor

        engine = Engine()
        world = World()
        actor = Actor(name="SelectableActor")
        world.spawn_actor(actor)

        editor = Editor(engine=engine)
        editor.select(actor)

        assert editor.selected_object is actor

    def test_editor_run_initializes_context(self):
        """Editor run should initialize context."""
        from editor.main import Editor

        editor = Editor()
        assert editor._context_created is False
        editor.run()
        assert editor._context_created is True

    def test_editor_shutdown_clears_state(self):
        """Editor shutdown should clear state."""
        from editor.main import Editor

        editor = Editor()
        editor.run()
        editor.shutdown()
        assert editor._context_created is False
        assert editor.selected_object is None
        assert len(editor._panels) == 0
