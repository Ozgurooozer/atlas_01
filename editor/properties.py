"""Properties panel for object property editing.

DearPyGui-based properties panel that displays and edits
object properties using the reflection system.

Layer: 7 (Editor)
Dependencies: editor.main, core.reflection
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from editor.main import EditorPanel
from core.reflection import get_properties, PropertyMeta

if TYPE_CHECKING:
    from core.object import Object
    from editor.main import Editor


class Properties(EditorPanel):
    """
    Properties panel for editing object properties.

    Uses the reflection system to discover and display
    properties of the selected object.

    Attributes:
        target: The object being edited.
        properties: List of PropertyMeta for target.
        is_modified: Whether there are pending changes.
    """

    def __init__(
        self,
        name: str = "Properties",
        editor: Optional[Editor] = None
    ) -> None:
        """Initialize properties panel.

        Args:
            name: Panel display name.
            editor: Optional parent editor reference.
        """
        super().__init__(name=name, editor=editor)
        self._target: Optional[Object] = None
        self._properties: List[PropertyMeta] = []
        self._is_modified: bool = False
        self._changes: List[Dict[str, Any]] = []
        self._original_values: Dict[str, Any] = {}

    @property
    def target(self) -> Optional[Object]:
        """Get target object."""
        return self._target

    @target.setter
    def target(self, value: Optional[Object]) -> None:
        """Set target object and refresh."""
        self._target = value
        self.refresh()

    @property
    def properties(self) -> List[PropertyMeta]:
        """Get properties list."""
        return self._properties

    @property
    def is_modified(self) -> bool:
        """Get modified flag."""
        return self._is_modified

    def refresh(self) -> None:
        """Refresh properties from target object.

        Discovers all reflected properties from the target.
        """
        self._properties = []
        self._original_values = {}
        self._changes = []
        self._is_modified = False

        if self._target is None:
            return

        self._properties = get_properties(self._target)

        # Store original values for undo
        for prop in self._properties:
            try:
                value = self._get_property_value(prop.name)
                self._original_values[prop.name] = value
            except AttributeError:
                pass

    def _get_property_value(self, name: str) -> Any:
        """Get property value from target."""
        if self._target is None:
            return None

        # Reflected property önce dene
        for prop in self._properties:
            if prop.name == name:
                from core.reflection import get_property_value
                return get_property_value(self._target, name)

        # Fallback: direkt attribute
        if hasattr(self._target, name):
            return getattr(self._target, name)

        return None

    def get_property_value(self, name: str) -> Any:
        """Get property value (public API).

        Args:
            name: Property name.

        Returns:
            Property value.
        """
        return self._get_property_value(name)

    def set_property_value(self, name: str, value: Any) -> None:
        """Set property value on target.

        Args:
            name: Property name.
            value: New value.
        """
        if self._target is None:
            return

        old_value = self._get_property_value(name)

        # Set the value
        if hasattr(self._target, name):
            setattr(self._target, name, value)
        else:
            from core.reflection import set_property_value
            set_property_value(self._target, name, value)

        # Track change
        existing_change = next(
            (c for c in self._changes if c['property'] == name),
            None
        )

        if existing_change:
            existing_change['new_value'] = value
        else:
            self._changes.append({
                'property': name,
                'old_value': old_value,
                'new_value': value
            })

        self._is_modified = True

    def get_categories(self) -> List[str]:
        """Get list of property categories.

        Returns:
            List of unique category names.
        """
        categories = set()
        for prop in self._properties:
            categories.add(prop.category)
        return list(categories)

    def clear_modified(self) -> None:
        """Clear modified flag and change tracking."""
        self._is_modified = False
        self._changes = []
        self._original_values = {}

        # Re-store original values
        if self._target:
            for prop in self._properties:
                try:
                    value = self._get_property_value(prop.name)
                    self._original_values[prop.name] = value
                except AttributeError:
                    pass

    def sync_with_selection(self) -> None:
        """Sync target with editor selection."""
        if self._editor is None:
            return

        self._target = self._editor.selected_object
        self.refresh()

    def get_changes(self) -> List[Dict[str, Any]]:
        """Get list of pending changes.

        Returns:
            List of change dicts.
        """
        return self._changes.copy()

    def apply_changes(self) -> None:
        """Apply all pending changes.

        Changes are already applied to the object,
        this just clears the modification state.
        """
        self.clear_modified()

    def revert_changes(self) -> None:
        """Revert all pending changes.

        Restores original values to the target object.
        """
        if self._target is None:
            return

        for name, value in self._original_values.items():
            if hasattr(self._target, name):
                setattr(self._target, name, value)

        self.clear_modified()

    def render(self) -> None:
        """Render properties content.

        In a real implementation, this would use DearPyGui
        to render property editors for each property.
        """
        if not self.visible:
            return

        if self._target is None:
            return

        # DearPyGui rendering would go here
        # For headless testing, this is a no-op
        pass
