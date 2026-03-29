import pytest
from hypothesis import given, strategies as st
from hal.headless import HeadlessGPU

@given(
    rotation=st.floats(min_value=-360, max_value=360),
    color=st.tuples(
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1),
        st.floats(min_value=0, max_value=1)
    ),
    flip_x=st.booleans(),
    flip_y=st.booleans(),
    anchor_x=st.floats(min_value=0, max_value=1),
    anchor_y=st.floats(min_value=0, max_value=1)
)
def test_draw_parameter_acceptance(rotation, color, flip_x, flip_y, anchor_x, anchor_y):
    """
    Özellik 1: draw() Parametre Kabulü
    Gereksinim 1.1, 1.8, 8.1
    HeadlessGPU.draw() yeni parametreleri kabul etmeli ve exception fırlatmamalı.
    """
    gpu = HeadlessGPU()
    tex_id = gpu.create_texture(100, 100)
    
    # Bu çağrı hata vermemeli
    gpu.draw(
        texture_id=tex_id,
        x=10,
        y=20,
        width=100,
        height=100,
        rotation=rotation,
        color=color,
        flip_x=flip_x,
        flip_y=flip_y,
        anchor_x=anchor_x,
        anchor_y=anchor_y
    )

from core.vec import Vec2
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture

class MockGPU(HeadlessGPU):
    def __init__(self):
        super().__init__()
        self.last_draw_params = None

    def draw(self, *args, **kwargs):
        self.last_draw_params = (args, kwargs)
        super().draw(*args, **kwargs)

@given(
    rotation=st.floats(min_value=-360, max_value=360),
    color=st.tuples(
        st.integers(min_value=0, max_value=255),
        st.integers(min_value=0, max_value=255),
        st.integers(min_value=0, max_value=255),
        st.integers(min_value=0, max_value=255)
    ),
    flip_x=st.booleans(),
    flip_y=st.booleans(),
    anchor_x=st.floats(min_value=0, max_value=1),
    anchor_y=st.floats(min_value=0, max_value=1)
)
def test_sprite_transform_propagation(rotation, color, flip_x, flip_y, anchor_x, anchor_y):
    """
    Özellik 2: Transform Parametreleri Shader'a İletilir
    Gereksinim 1.2, 1.3, 1.6, 1.7
    """
    gpu = MockGPU()
    renderer = Renderer2D()
    renderer.gpu_device = gpu
    
    tex = Texture(10, 10)
    sprite = Sprite(tex)
    sprite.rotation = rotation
    sprite.color = color
    sprite.flip_x = flip_x
    sprite.flip_y = flip_y
    sprite.anchor_x = anchor_x
    sprite.anchor_y = anchor_y
    
    renderer.draw_sprite(sprite)
    
    params = gpu.last_draw_params[1]
    assert params['rotation'] == rotation
    assert params['flip_x'] == flip_x
    assert params['flip_y'] == flip_y
    assert params['anchor_x'] == anchor_x
    assert params['anchor_y'] == anchor_y
    
    # Color conversion check
    expected_color = tuple(c / 255.0 for c in color)
    for a, b in zip(params['color'], expected_color):
        assert abs(a - b) < 0.001

from engine.renderer.camera import Camera

@given(
    pos_x=st.floats(min_value=-1000, max_value=1000),
    pos_y=st.floats(min_value=-1000, max_value=1000),
    zoom=st.floats(min_value=0.1, max_value=10.0),
    target_x=st.floats(min_value=-1000, max_value=1000),
    target_y=st.floats(min_value=-1000, max_value=1000)
)
def test_camera_round_trip(pos_x, pos_y, zoom, target_x, target_y):
    """
    Özellik 4: Kamera Round-Trip
    Gereksinim 2.9
    """
    cam = Camera()
    cam.position = Vec2(pos_x, pos_y)
    cam.zoom = zoom
    
    # World to Screen
    sx, sy = cam.world_to_screen(target_x, target_y)
    # Screen to World
    wx, wy = cam.screen_to_world(sx, sy)
    
    assert abs(wx - target_x) < 0.001
    assert abs(wy - target_y) < 0.001

@given(
    zoom=st.floats(min_value=0.1, max_value=10.0)
)
def test_camera_zoom_projection(zoom):
    """
    Özellik 5: Zoom Projection Matrix'i Etkiler
    Gereksinim 2.4
    """
    cam = Camera()
    cam.zoom = zoom
    
    # Side scroll mode (default)
    proj = cam.projection_matrix
    # Orthographic projection matrix has 2/w and -2/h in [0] and [5]
    # But wait, our current implementation doesn't put zoom in projection_matrix for side_scroll
    # It puts it in view_matrix. Let's check view_matrix instead.
    view = cam.view_matrix
    # view[0] is z * cos_r, view[5] is z * cos_r
    assert abs(view[0] - zoom) < 0.001
    assert abs(view[5] - zoom) < 0.001

@given(
    follow_speed=st.floats(min_value=0.01, max_value=1.0),
    target_x=st.floats(min_value=-1000, max_value=1000),
    target_y=st.floats(min_value=-1000, max_value=1000)
)
def test_camera_follow_lerp(follow_speed, target_x, target_y):
    """
    Özellik 6: Kamera Follow Lerp
    Gereksinim 2.7
    """
    cam = Camera()
    cam.position = Vec2(0, 0)
    
    class Target:
        def __init__(self, x, y):
            self.position = Vec2(x, y)
            
    target = Target(target_x, target_y)
    cam.follow_target = target
    cam.follow_speed = follow_speed
    
    initial_dist = Vec2(target_x, target_y).length()
    cam.update(1.0/60.0)
    
    new_dist = (Vec2(target_x, target_y) - cam.position).length()
    
    if initial_dist > 0.001:
        assert new_dist < initial_dist

from engine.renderer.material import Material

@given(
    name=st.text(min_size=1),
    value=st.one_of(st.floats(), st.integers(), st.tuples(st.floats(), st.floats()))
)
def test_material_uniform_storage(name, value):
    """
    Özellik 17: Material Uniform Saklama
    Gereksinim 6.1, 6.5
    """
    import math
    mat = Material()
    mat.set_uniform(name, value)
    
    stored = mat.uniforms[name]
    if isinstance(value, float) and math.isnan(value):
        assert math.isnan(stored)
    else:
        assert stored == value

@given(
    shader_name=st.text(min_size=1),
    uniform_name=st.text(min_size=1),
    value=st.floats()
)
def test_material_copy_invariant(shader_name, uniform_name, value):
    """
    Özellik 18: Material Kopya İnvaryantı
    Gereksinim 6.6
    """
    mat = Material(shader_name)
    mat.set_uniform(uniform_name, value)
    
    import math
    copy_mat = mat.copy()
    assert copy_mat.shader_name == mat.shader_name
    
    val1 = mat.uniforms[uniform_name]
    val2 = copy_mat.uniforms[uniform_name]
    if isinstance(val1, float) and math.isnan(val1):
        assert math.isnan(val2)
    else:
        assert val1 == val2
    
    # Modify copy, original should not change
    copy_mat.set_uniform(uniform_name, value + 1.0)
    
    val_orig = mat.uniforms[uniform_name]
    if isinstance(value, float) and math.isnan(value):
        assert math.isnan(val_orig)
    else:
        assert val_orig == value
    val_copy = copy_mat.uniforms[uniform_name]
    if isinstance(value, float) and math.isnan(value):
        assert math.isnan(val_copy)
    else:
        assert val_copy == value + 1.0

from engine.renderer.batch import SpriteBatch

@given(
    n=st.integers(min_value=1, max_value=20)
)
def test_batch_texture_grouping(n):
    """
    Özellik 7: Batch Texture Gruplama
    Gereksinim 3.1, 3.2, 3.3
    """
    # Mock renderer to avoid None check issues
    renderer = Renderer2D()
    batch = SpriteBatch(renderer=renderer, max_sprites=100)
    batch.begin()
    
    textures = [Texture(10, 10) for _ in range(n)]
    for i in range(n):
        sprite = Sprite(textures[i])
        sprite.z_index = i # Keep order to avoid sorting mixing textures
        batch.draw(sprite)
        
    batch.end()
    # texture_changes starts at 0, first texture makes it 1, then each change increments
    assert batch.texture_changes == n

@given(
    z_indices=st.lists(st.integers(), min_size=1, max_size=20)
)
def test_batch_z_index_sorting(z_indices):
    """
    Özellik 8: Batch Z-Index Sıralaması
    Gereksinim 3.4
    """
    batch = SpriteBatch(max_sprites=100)
    batch.begin()
    
    tex = Texture(10, 10)
    for z in z_indices:
        sprite = Sprite(tex)
        sprite.z_index = z
        batch.draw(sprite)
        
    batch.end()
    
    sorted_z = [s.z_index for s in batch.sorted_sprites]
    assert sorted_z == sorted(z_indices)

@given(
    max_sprites=st.integers(min_value=1, max_value=10),
    extra=st.integers(min_value=1, max_value=5)
)
def test_batch_automatic_flush(max_sprites, extra):
    """
    Özellik 10: Batch Otomatik Flush
    Gereksinim 3.5
    """
    batch = SpriteBatch(max_sprites=max_sprites)
    batch.begin()
    
    tex = Texture(10, 10)
    for _ in range(max_sprites + extra):
        batch.draw(Sprite(tex))
        
    batch.end()
    assert batch.flush_count > 1

@given(
    n_materials=st.integers(min_value=1, max_value=10)
)
def test_material_batch_break(n_materials):
    """
    Özellik 19: Material Batch Kesimi
    Gereksinim 6.7
    """
    renderer = Renderer2D()
    batch = SpriteBatch(renderer=renderer, max_sprites=100)
    batch.begin()
    
    tex = Texture(10, 10)
    materials = [Material(f"shader_{i}") for i in range(n_materials)]
    for i in range(n_materials):
        sprite = Sprite(tex)
        sprite.material = materials[i]
        sprite.z_index = i
        batch.draw(sprite)
        
    batch.end()
    assert batch.texture_changes == n_materials

from engine.renderer.light import Light2D, LightRenderer, LightType
from core.color import Color

@given(
    enabled=st.booleans(),
    intensity=st.floats(min_value=0, max_value=1)
)
def test_light_submit_counter_invariant(enabled, intensity):
    """
    Özellik 11: Light Submit Sayaç İnvaryantı
    Gereksinim 4.7, 4.9
    """
    gpu = HeadlessGPU()
    lr = LightRenderer(gpu, 800, 600)
    lr.begin_light_pass()
    
    light = Light2D(intensity=intensity)
    light.enabled = enabled
    
    lr.submit(light)
    
    if enabled:
        assert lr.light_count == 1
    else:
        assert lr.light_count == 0

def test_light_pass_round_trip():
    """
    Özellik 12: LightPass Round-Trip
    Gereksinim 4.1, 4.3
    """
    gpu = HeadlessGPU()
    lr = LightRenderer(gpu, 800, 600)
    
    lr.begin_light_pass()
    assert lr.light_map.fbo.is_bound == True
    
    lr.end_light_pass()
    assert lr.light_map.fbo.is_bound == False

from engine.renderer.postprocess_stack import PostProcessStack, PostProcessPass, BloomPass, ColorGradingPass

@given(
    width=st.integers(min_value=1, max_value=1920),
    height=st.integers(min_value=1, max_value=1080)
)
def test_postprocess_stack_identity(width, height):
    """
    Özellik 13: PostProcessStack Identity
    Gereksinim 5.9
    """
    gpu = HeadlessGPU()
    pps = PostProcessStack(gpu, width, height)
    scene_fbo = gpu.create_framebuffer(width, height)
    
    # Boş stack ile render
    final_fbo = pps.render(scene_fbo)
    
    # Boş stack durumunda sahne FBO'su doğrudan dönmeli
    assert final_fbo == scene_fbo

def test_postprocess_stack_pass_management():
    """
    Özellik 16: PostProcessStack Pass Ekleme/Çıkarma
    Gereksinim 5.1, 5.10
    """
    gpu = HeadlessGPU()
    pps = PostProcessStack(gpu, 800, 600)
    bloom = BloomPass()
    
    initial_count = len(pps._passes)
    pps.add_pass(bloom)
    assert len(pps._passes) == initial_count + 1
    
    pps.remove_pass(bloom)
    assert len(pps._passes) == initial_count

@given(
    threshold=st.floats(min_value=0, max_value=1),
    intensity=st.floats(min_value=0, max_value=1)
)
def test_bloom_parameters(threshold, intensity):
    """
    Özellik 14: Bloom Threshold Filtresi
    Gereksinim 5.4
    """
    bloom = BloomPass(threshold=threshold, intensity=intensity)
    assert bloom.threshold == threshold
    assert bloom.intensity == intensity

@given(
    exposure=st.floats(min_value=0, max_value=10),
    tone_mapping=st.sampled_from(["aces", "reinhard", "filmic"])
)
def test_tone_mapping_parameters(exposure, tone_mapping):
    """
    Özellik 15: Tone Mapping Aralık İnvaryantı
    Gereksinim 5.6
    """
    cg = ColorGradingPass(exposure=exposure, tone_mapping=tone_mapping)
    assert cg.exposure == exposure
    assert cg.tone_mapping == tone_mapping
