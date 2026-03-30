import pytest
import math
from hypothesis import given, strategies as st
from engine.renderer.instance_data import InstanceData

# Finite float strategy
finite_floats = st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6)

@given(
    pos=st.tuples(finite_floats, finite_floats),
    size=st.tuples(finite_floats, finite_floats),
    rot=finite_floats,
    color=st.tuples(st.floats(0, 1), st.floats(0, 1), st.floats(0, 1), st.floats(0, 1)),
    anchor=st.tuples(st.floats(0, 1), st.floats(0, 1)),
    flip=st.tuples(st.sampled_from([0.0, 1.0]), st.sampled_from([0.0, 1.0])),
    uv_off=st.tuples(st.floats(0, 1), st.floats(0, 1)),
    uv_size=st.tuples(st.floats(0, 1), st.floats(0, 1))
)
def test_instance_data_round_trip(pos, size, rot, color, anchor, flip, uv_off, uv_size):
    """Gereksinim 3.3: to_bytes() -> from_bytes() round-trip testi."""
    original = InstanceData(
        position=pos, size=size, rotation=rot, color=color,
        anchor=anchor, flip=flip, uv_offset=uv_off, uv_size=uv_size
    )
    
    data_bytes = original.to_bytes()
    recovered = InstanceData.from_bytes(data_bytes)
    
    # Compare with small epsilon for floats
    assert recovered.position[0] == pytest.approx(original.position[0])
    assert recovered.position[1] == pytest.approx(original.position[1])
    assert recovered.size[0] == pytest.approx(original.size[0])
    assert recovered.size[1] == pytest.approx(original.size[1])
    assert recovered.rotation == pytest.approx(original.rotation)
    assert recovered.color == pytest.approx(original.color)
    assert recovered.anchor == pytest.approx(original.anchor)
    assert recovered.flip == pytest.approx(original.flip)
    assert recovered.uv_offset == pytest.approx(original.uv_offset)
    assert recovered.uv_size == pytest.approx(original.uv_size)

def test_instance_data_nan_validation():
    """Gereksinim 3.4: NaN/Inf validasyon testi."""
    with pytest.raises(ValueError):
        InstanceData(position=(float('nan'), 0.0))
    
    with pytest.raises(ValueError):
        InstanceData(rotation=float('inf'))
