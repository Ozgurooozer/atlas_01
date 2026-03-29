"""Tag System - Object tagging and categorization.

Provides tag-based organization and querying for game objects.

Layer: 3 (World)
Dependencies: core.object
"""
from typing import Dict, Set, List, Any
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tag:
    """Immutable tag for categorization.
    
    Tags are used to categorize and group game objects.
    
    Attributes:
        name: Tag identifier string
    """
    name: str
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class Taggable:
    """Mixin class for objects that can have tags.
    
    Inherit from this to add tag support to any class.
    """
    
    def __init__(self):
        """Initialize with empty tags."""
        self._tags: Set[str] = set()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this object.
        
        Args:
            tag: Tag name to add
        """
        self._tags.add(tag)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from this object.
        
        Args:
            tag: Tag name to remove
            
        Returns:
            True if removed, False if not present
        """
        if tag in self._tags:
            self._tags.remove(tag)
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """Check if object has specific tag.
        
        Args:
            tag: Tag name to check
            
        Returns:
            True if object has tag
        """
        return tag in self._tags
    
    def has_any_tag(self, tags: List[str]) -> bool:
        """Check if object has any of the given tags.
        
        Args:
            tags: List of tags to check
            
        Returns:
            True if object has at least one tag
        """
        return any(tag in self._tags for tag in tags)
    
    def has_all_tags(self, tags: List[str]) -> bool:
        """Check if object has all of the given tags.
        
        Args:
            tags: List of tags to check
            
        Returns:
            True if object has all tags
        """
        return all(tag in self._tags for tag in tags)
    
    def clear_tags(self) -> None:
        """Remove all tags from this object."""
        self._tags.clear()
    
    @property
    def tags(self) -> Set[str]:
        """Get all tags on this object."""
        return self._tags.copy()
    
    def get_tags(self) -> List[str]:
        """Get list of all tags."""
        return list(self._tags)


class TagManager:
    """Central manager for tag-based object queries.
    
    Maintains indexes for fast tag-based lookups.
    """
    
    def __init__(self):
        """Initialize tag manager."""
        # tag -> set of objects
        self._objects_by_tag: Dict[str, Set[Any]] = {}
        # object -> set of tags (for fast unregister)
        self._tags_by_object: Dict[Any, Set[str]] = {}
    
    @property
    def objects_by_tag(self) -> Dict[str, Set[Any]]:
        """Get objects indexed by tag (read-only view)."""
        return {tag: objs.copy() for tag, objs in self._objects_by_tag.items()}
    
    def register(self, obj: Any) -> None:
        """Register a taggable object.
        
        Args:
            obj: Object with tags to register
        """
        tags = getattr(obj, 'tags', set())
        if not tags:
            return
        
        # Add to each tag's set
        for tag in tags:
            if tag not in self._objects_by_tag:
                self._objects_by_tag[tag] = set()
            self._objects_by_tag[tag].add(obj)
        
        # Track for this object
        self._tags_by_object[obj] = tags.copy()
    
    def unregister(self, obj: Any) -> None:
        """Unregister a taggable object.
        
        Args:
            obj: Object to unregister
        """
        if obj not in self._tags_by_object:
            return
        
        tags = self._tags_by_object.pop(obj)
        
        # Remove from each tag's set
        for tag in tags:
            if tag in self._objects_by_tag:
                self._objects_by_tag[tag].discard(obj)
                # Clean up empty tag sets
                if not self._objects_by_tag[tag]:
                    del self._objects_by_tag[tag]
    
    def get_by_tag(self, tag: str) -> List[Any]:
        """Get all objects with specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of objects with tag
        """
        return list(self._objects_by_tag.get(tag, []))
    
    def get_by_any_tag(self, tags: List[str]) -> List[Any]:
        """Get all objects with any of the given tags.
        
        Args:
            tags: Tags to search for
            
        Returns:
            List of unique objects with any tag
        """
        result: Set[Any] = set()
        for tag in tags:
            result.update(self._objects_by_tag.get(tag, []))
        return list(result)
    
    def get_by_all_tags(self, tags: List[str]) -> List[Any]:
        """Get all objects with all of the given tags.
        
        Args:
            tags: Tags to search for
            
        Returns:
            List of objects with all tags
        """
        if not tags:
            return []
        
        # Start with objects from first tag
        result = set(self._objects_by_tag.get(tags[0], []))
        
        # Intersect with each subsequent tag
        for tag in tags[1:]:
            result &= self._objects_by_tag.get(tag, set())
        
        return list(result)
    
    def get_all_tags(self) -> List[str]:
        """Get all known tags.
        
        Returns:
            List of all registered tag names
        """
        return list(self._objects_by_tag.keys())
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._objects_by_tag.clear()
        self._tags_by_object.clear()
    
    def update_registration(self, obj: Any) -> None:
        """Update registration after object tags change.
        
        Args:
            obj: Object whose tags changed
        """
        # Remove old registration
        self.unregister(obj)
        # Re-register with new tags
        self.register(obj)
