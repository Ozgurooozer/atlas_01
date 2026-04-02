"""Tests for Tag system.

Test-First Development for Tag management
"""
from world.tag import Tag, Taggable, TagManager


class TestTag:
    """Test tag."""
    
    def test_initialization(self):
        """Test tag creation."""
        tag = Tag("enemy")
        assert tag.name == "enemy"
    
    def test_equality(self):
        """Test tag equality."""
        tag1 = Tag("player")
        tag2 = Tag("player")
        tag3 = Tag("enemy")
        
        assert tag1 == tag2
        assert tag1 != tag3
    
    def test_hash(self):
        """Test tag can be used in sets/dicts."""
        tag1 = Tag("player")
        tag2 = Tag("player")
        
        tags = {tag1}
        assert tag2 in tags


class TestTaggable:
    """Test taggable mixin."""
    
    def test_add_tag(self):
        """Test adding tag."""
        obj = Taggable()
        obj.add_tag("player")
        
        assert "player" in obj.tags
    
    def test_add_multiple_tags(self):
        """Test adding multiple tags."""
        obj = Taggable()
        obj.add_tag("enemy")
        obj.add_tag("boss")
        
        assert "enemy" in obj.tags
        assert "boss" in obj.tags
    
    def test_remove_tag(self):
        """Test removing tag."""
        obj = Taggable()
        obj.add_tag("player")
        obj.remove_tag("player")
        
        assert "player" not in obj.tags
    
    def test_has_tag(self):
        """Test checking tag."""
        obj = Taggable()
        obj.add_tag("enemy")
        
        assert obj.has_tag("enemy") is True
        assert obj.has_tag("player") is False
    
    def test_has_any_tag(self):
        """Test checking any of multiple tags."""
        obj = Taggable()
        obj.add_tag("enemy")
        
        assert obj.has_any_tag(["player", "enemy"]) is True
        assert obj.has_any_tag(["player", "npc"]) is False
    
    def test_has_all_tags(self):
        """Test checking all tags."""
        obj = Taggable()
        obj.add_tag("enemy")
        obj.add_tag("boss")
        
        assert obj.has_all_tags(["enemy", "boss"]) is True
        assert obj.has_all_tags(["enemy", "minion"]) is False
    
    def test_clear_tags(self):
        """Test clearing all tags."""
        obj = Taggable()
        obj.add_tag("enemy")
        obj.add_tag("boss")
        
        obj.clear_tags()
        
        assert len(obj.tags) == 0
    
    def test_get_tags(self):
        """Test getting all tags."""
        obj = Taggable()
        obj.add_tag("player")
        
        tags = obj.get_tags()
        assert "player" in tags


class TestTagManager:
    """Test tag manager."""
    
    def test_initialization(self):
        """Test manager creation."""
        manager = TagManager()
        assert manager.objects_by_tag == {}
    
    def test_register_object(self):
        """Test registering tagged object."""
        manager = TagManager()
        obj = Taggable()
        obj.add_tag("enemy")
        
        manager.register(obj)
        
        assert obj in manager.get_by_tag("enemy")
    
    def test_unregister_object(self):
        """Test unregistering object."""
        manager = TagManager()
        obj = Taggable()
        obj.add_tag("enemy")
        manager.register(obj)
        
        manager.unregister(obj)
        
        assert obj not in manager.get_by_tag("enemy")
    
    def test_get_by_tag(self):
        """Test getting objects by tag."""
        manager = TagManager()
        obj1 = Taggable()
        obj1.add_tag("enemy")
        obj2 = Taggable()
        obj2.add_tag("enemy")
        obj3 = Taggable()
        obj3.add_tag("player")
        
        manager.register(obj1)
        manager.register(obj2)
        manager.register(obj3)
        
        enemies = manager.get_by_tag("enemy")
        assert len(enemies) == 2
        assert obj1 in enemies
        assert obj2 in enemies
    
    def test_get_by_multiple_tags(self):
        """Test getting objects with any of multiple tags."""
        manager = TagManager()
        obj1 = Taggable()
        obj1.add_tag("enemy")
        obj2 = Taggable()
        obj2.add_tag("player")
        
        manager.register(obj1)
        manager.register(obj2)
        
        result = manager.get_by_any_tag(["enemy", "player"])
        assert len(result) == 2
    
    def test_get_all_tags(self):
        """Test getting all known tags."""
        manager = TagManager()
        obj = Taggable()
        obj.add_tag("enemy")
        obj.add_tag("boss")
        manager.register(obj)
        
        tags = manager.get_all_tags()
        assert "enemy" in tags
        assert "boss" in tags
    
    def test_clear(self):
        """Test clearing all registrations."""
        manager = TagManager()
        obj = Taggable()
        obj.add_tag("enemy")
        manager.register(obj)
        
        manager.clear()
        
        assert manager.get_by_tag("enemy") == []
