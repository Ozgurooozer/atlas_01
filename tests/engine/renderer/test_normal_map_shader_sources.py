from engine.renderer.shader import NORMAL_MAP_VERTEX_SRC, NORMAL_MAP_FRAGMENT_SRC

def test_normal_map_shader_sources_not_empty():
    """Gereksinim 1.1, 1.2: Shader kaynakları boş olmamalı."""
    assert NORMAL_MAP_VERTEX_SRC.strip() != ""
    assert NORMAL_MAP_FRAGMENT_SRC.strip() != ""

def test_normal_map_shader_sources_contain_keywords():
    """Gereksinim 1.1, 1.2: Shader kaynakları gerekli anahtar kelimeleri içermeli."""
    # Vertex shader
    assert "v_world_pos" in NORMAL_MAP_VERTEX_SRC
    assert "u_projection" in NORMAL_MAP_VERTEX_SRC
    assert "u_view" in NORMAL_MAP_VERTEX_SRC
    
    # Fragment shader
    assert "u_normal_map" in NORMAL_MAP_FRAGMENT_SRC
    assert "u_lights[8]" in NORMAL_MAP_FRAGMENT_SRC
    assert "u_light_count" in NORMAL_MAP_FRAGMENT_SRC
    assert "u_ambient" in NORMAL_MAP_FRAGMENT_SRC
    assert "struct Light" in NORMAL_MAP_FRAGMENT_SRC
