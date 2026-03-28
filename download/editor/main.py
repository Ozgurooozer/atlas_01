"""Editor application entry point.

DearPyGui-based editor for the game engine.
Layer 7 - consumes Engine API, no runtime code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from core.object import Object

if TYPE_CHECKING:
    from engine.engine import Engine


class EditorPanel(Object):
    """Base class for editor panels.

    Each panel is a distinct UI component that can be
    shown/hidden independently.

    Attributes:
        name: Panel display name.
        visible: Whether panel is currently visible.
    """

    def __init__(
        self,
        name: str = "Panel",
        editor: "Editor | None" = None
    ) -> None:
        """Initialize editor panel.

        Args:
            name: Panel display name.
            editor: Optional reference to parent editor.
        """
        super().__init__(name=name)
        self._editor = editor
        self._visible: bool = True

    @property
    def editor(self) -> Optional[Editor]:
        """Get parent editor reference."""
        return self._editor

    @property
    def visible(self) -> bool:
        """Get panel visibility."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set panel visibility.

        Args:
            value: New visibility state.
        """
        self._visible = value

    def render(self) -> None:
        """Render panel content. Override in subclasses."""
        pass


class Editor(Object):
    """Main editor application.

    Manages DearPyGui context, panels, and coordinates
    between different editor components.

    Attributes:
        engine: Reference to the game engine.
        selected_object: Currently selected object in editor.
    """

    def __init__(
        self,
        engine: Optional[Engine] = None,
        name: str = "Editor"
    ) -> None:
        """Initialize editor application.

        Args:
            engine: Optional reference to game engine.
            name: Editor instance name.
        """
        super().__init__(name=name)
        self._engine = engine
        self._selected_object: Optional[Object] = None
        self._panels: dict[str, EditorPanel] = {}
        self._context_created: bool = False

    @property
    def engine(self) -> Optional[Engine]:
        """Get engine reference."""
        return self._engine

    @property
    def selected_object(self) -> Optional[Object]:
        """Get currently selected object."""
        return self._selected_object

    def select(self, obj: Object) -> None:
        """Set selected object.

        Args:
            obj: Object to select.
        """
        self._selected_object = obj

    def clear_selection(self) -> None:
        """Clear current selection."""
        self._selected_object = None

    def register_panel(self, panel: EditorPanel) -> None:
        """Register a panel with the editor.

        Args:
            panel: Panel to register.
        """
        self._panels[panel.name] = panel

    def unregister_panel(self, name: str) -> None:
        """Unregister a panel by name.

        Args:
            name: Name of panel to unregister.
        """
        if name in self._panels:
            del self._panels[name]

    def run(self) -> None:
        """Start the editor main loop.

        Initializes DearPyGui context if not already created
        and starts the DearPyGui main loop.
        """
        if not self._context_created:
            self._init_context()

        # Render all visible panels
        for panel in self._panels.values():
            if panel.visible:
                panel.render()

    def shutdown(self) -> None:
        """Shutdown editor and cleanup resources."""
        if self._context_created:
            self._cleanup_context()
        self._panels.clear()
        self._selected_object = None

    def _init_context(self) -> None:
        """Initialize DearPyGui context.

        Called internally before first run.
        """
        # DearPyGui context initialization would go here
        # For headless testing, we just mark it as created
        self._context_created = True

    def _cleanup_context(self) -> None:
        """Cleanup DearPyGui context."""
        self._context_created = False
