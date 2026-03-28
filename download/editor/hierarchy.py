"""Hierarchy panel for actor tree display.

DearPyGui-based hierarchy panel that displays the scene tree.
Supports selection, expansion, and filtering.

Layer: 7 (Editor)
Dependencies: editor.main
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from editor.main import EditorPanel
from core.guid import GUID

if TYPE_CHECKING:
    from world.world import World
    from editor.main import Editor


class Hierarchy(EditorPanel):
    """
    Hierarchy panel for displaying scene tree.

    Shows all actors in the world as a tree structure.
    Supports selection, expansion, and name filtering.

    Attributes:
        world: Reference to the World being displayed.
        root_items: List of root-level tree items.
        selected_item: GUID of currently selected item.
        filter_text: Text filter for item names.
    """

    def __init__(
        self,
        name: str = "Hierarchy",
        editor: Optional[Editor] = None
    ) -> None:
        """Initialize hierarchy panel.

        Args:
            name: Panel display name.
            editor: Optional parent editor reference.
        """
        super().__init__(name=name, editor=editor)
        self._world: Optional[World] = None
        self._root_items: List[Dict[str, Any]] = []
        self._selected_item: Optional[GUID] = None
        self._filter_text: str = ""
        self._expanded_items: set = set()

    @property
    def world(self) -> Optional[World]:
        """Get world reference."""
        return self._world

    @world.setter
    def world(self, value: Optional[World]) -> None:
        """Set world reference."""
        self._world = value

    @property
    def root_items(self) -> List[Dict[str, Any]]:
        """Get root items list."""
        return self._root_items

    @property
    def selected_item(self) -> Optional[GUID]:
        """Get selected item GUID."""
        return self._selected_item

    @property
    def filter_text(self) -> str:
        """Get filter text."""
        return self._filter_text

    @filter_text.setter
    def filter_text(self, value: str) -> None:
        """Set filter text."""
        self._filter_text = value

    def refresh(self) -> None:
        """Refresh hierarchy from world.

        Rebuilds the tree structure from the world's actors.
        """
        self._root_items = []

        if self._world is None:
            return

        for actor in self._world.actors:
            item = {
                'guid': actor.guid,
                'name': actor.name,
                'children': [],
                'expanded': str(actor.guid) in self._expanded_items
            }
            self._root_items.append(item)

    def get_item_by_guid(self, guid: GUID) -> Optional[Dict[str, Any]]:
        """Find item by GUID.

        Args:
            guid: GUID to search for.

        Returns:
            Item dict or None if not found.
        """
        def find_in_items(items: List[Dict]) -> Optional[Dict]:
            for item in items:
                if item['guid'] == guid:
                    return item
                result = find_in_items(item['children'])
                if result:
                    return result
            return None

        return find_in_items(self._root_items)

    def select_item(self, guid: GUID) -> None:
        """Select an item by GUID.

        Args:
            guid: GUID of item to select.
        """
        self._selected_item = guid

        # Notify editor of selection
        if self._editor and self._world:
            item = self.get_item_by_guid(guid)
            if item:
                # Find the actor in world
                for actor in self._world.actors:
                    if actor.guid == guid:
                        self._editor.select(actor)
                        break

    def clear_selection(self) -> None:
        """Clear current selection."""
        self._selected_item = None
        if self._editor:
            self._editor.clear_selection()

    def toggle_expand(self, guid: GUID) -> None:
        """Toggle expansion state of an item.

        Args:
            guid: GUID of item to toggle.
        """
        guid_str = str(guid)
        if guid_str in self._expanded_items:
            self._expanded_items.remove(guid_str)
        else:
            self._expanded_items.add(guid_str)

        # Update item's expanded state
        item = self.get_item_by_guid(guid)
        if item:
            item['expanded'] = str(guid) in self._expanded_items

    def get_filtered_items(self) -> List[Dict[str, Any]]:
        """Get items filtered by filter_text.

        Returns:
            List of items matching the filter.
        """
        if not self._filter_text:
            return self._root_items

        filter_lower = self._filter_text.lower()

        def filter_items(items: List[Dict]) -> List[Dict]:
            result = []
            for item in items:
                if filter_lower in item['name'].lower():
                    result.append(item)
                # Also check children
                child_matches = filter_items(item['children'])
                if child_matches and item not in result:
                    result.append(item)
            return result

        return filter_items(self._root_items)

    def render(self) -> None:
        """Render hierarchy content.

        In a real implementation, this would use DearPyGui
        to render the tree view with selection and expansion.
        """
        if not self.visible:
            return

        # DearPyGui rendering would go here
        # For headless testing, this is a no-op
        pass
