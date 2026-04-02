import math
from hypothesis import given, strategies as st
from world.transform import TransformComponent

@given(
    px=st.floats(min_value=-1000, max_value=1000),
    py=st.floats(min_value=-1000, max_value=1000),
    pr=st.floats(min_value=-360, max_value=360),
    ps=st.floats(min_value=0.1, max_value=10.0),
    lx=st.floats(min_value=-100, max_value=100),
    ly=st.floats(min_value=-100, max_value=100),
    lr=st.floats(min_value=-360, max_value=360),
    ls=st.floats(min_value=0.1, max_value=10.0)
)
def test_parent_child_world_transform(px, py, pr, ps, lx, ly, lr, ls):
    """
    Özellik 1: Parent-Child Dünya Transform Hesaplama
    Gereksinim 1.3, 1.4, 1.5, 1.6
    """
    parent = TransformComponent("Parent")
    parent.position = (px, py)
    parent.rotation = pr
    parent.set_uniform_scale(ps)
    
    child = TransformComponent("Child")
    child.parent = parent
    child.position = (lx, ly)
    child.rotation = lr
    child.set_uniform_scale(ls)
    
    # World Rotation check
    assert abs(child.world_rotation - (pr + lr)) < 0.001
    
    # World Scale check
    wsx, wsy = child.world_scale
    assert abs(wsx - (ps * ls)) < 0.001
    assert abs(wsy - (ps * ls)) < 0.001
    
    # World Position check
    wpx, wpy = child.world_position
    
    # Manual calculation
    rad = math.radians(pr)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    
    # Local scaled
    slx = lx * ps
    sly = ly * ps
    
    # Rotated
    rx = slx * cos_r - sly * sin_r
    ry = slx * sin_r + sly * cos_r
    
    expected_x = px + rx
    expected_y = py + ry
    
    assert abs(wpx - expected_x) < 0.001
    assert abs(wpy - expected_y) < 0.001

@given(
    x=st.floats(allow_nan=False, allow_infinity=False),
    y=st.floats(allow_nan=False, allow_infinity=False),
    rotation=st.floats(min_value=-360, max_value=360),
    sx=st.floats(min_value=0.01, max_value=100),
    sy=st.floats(min_value=0.01, max_value=100)
)
def test_transform_serialization_roundtrip(x, y, rotation, sx, sy):
    """
    Özellik 2: TransformComponent Serileştirme Round-Trip
    Gereksinim 1.7
    """
    t1 = TransformComponent()
    t1.x = x
    t1.y = y
    t1.rotation = rotation
    t1.scale_x = sx
    t1.scale_y = sy
    
    data = t1.serialize()
    
    t2 = TransformComponent()
    t2.deserialize(data)
    
    assert t2.x == x
    assert t2.y == y
    assert abs(t2.rotation - rotation) < 0.001
    assert t2.scale_x == sx
    assert t2.scale_y == sy
