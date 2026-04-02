from world.transform import TransformComponent

def test_transform_defaults():
    """Gereksinim 1.1, 1.2"""
    t = TransformComponent()
    assert t.position == (0.0, 0.0)
    assert t.rotation == 0.0
    assert t.scale == (1.0, 1.0)
    assert t.parent is None

def test_transform_hierarchy_3_levels():
    """Gereksinim 1.5, 1.6"""
    root = TransformComponent("Root")
    root.position = (100, 100)
    
    mid = TransformComponent("Mid")
    mid.parent = root
    mid.position = (50, 0)
    
    leaf = TransformComponent("Leaf")
    leaf.parent = mid
    leaf.position = (10, 0)
    
    # Root: (100, 100)
    # Mid: (100+50, 100+0) = (150, 100)
    # Leaf: (150+10, 100+0) = (160, 100)
    
    assert leaf.world_position == (160.0, 100.0)

def test_transform_parent_none_fallback():
    """Gereksinim 1.5"""
    t = TransformComponent()
    t.position = (42, 42)
    assert t.world_position == (42.0, 42.0)
    assert t.world_rotation == 0.0
    assert t.world_scale == (1.0, 1.0)

def test_transform_scale_inheritance():
    """Gereksinim 1.6"""
    parent = TransformComponent()
    parent.set_uniform_scale(2.0)
    
    child = TransformComponent()
    child.parent = parent
    child.position = (10, 0)
    child.set_uniform_scale(0.5)
    
    # World scale: 2.0 * 0.5 = 1.0
    assert child.world_scale == (1.0, 1.0)
    # World position: Parent(0,0) + Child(10*2, 0*2) = (20, 0)
    assert child.world_position == (20.0, 0.0)
