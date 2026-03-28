# 2D Game Engine Renderer Development Prompt

## PROJE BİLGİSİ

Bu prompt, 7 katmanlı 2D oyun motoru için profesyonel seviye GPU tabanlı renderer geliştirmek için hazırlanmıştır. Hedef: **Celeste / Hollow Knight kalitesinde 2D grafikler**.

---

## MİMARİ YAPI

```
KATMANLAR (Dıştan içe doğru):
0. HAL         → Platform abstraction (window, GPU, filesystem)
1. CORE        → Temel yapılar (object, eventbus, serializer)
2. ENGINE      → Alt sistemler (renderer, physics, audio)
3. WORLD       → Oyun dünyası (actor, component, level)
4. GAME        → Oyun mantığı (gamemode, controller, save)
5. SCRIPTING   → AI ve scripting (statemachine, behaviour_tree)
6. UI          → Kullanıcı arayüzü (widget, canvas)
7. EDITOR      → Editör araçları (viewport, hierarchy)
```

**KURAL:** Bir katman SADECE kendi katmanındaki veya ALT katmanlardaki dosyaları import edebilir. Üst katman import YASAKTIR.

---

## ZORUNLU KURALLAR

### 1. Sınıf Boyutu
```
MAKSİMUM 200 SATIR / SINIF
Daha fazla = BÖL (Single Responsibility)
```

### 2. Import Kuralları
```python
# DOĞRU - Alt katmanlardan import
from core.object import Object      # Engine (2) → Core (1) ✓
from hal.interfaces import IGPUDevice  # Engine (2) → HAL (0) ✓

# YASAK - Üst katmandan import
from world.actor import Actor       # Engine (2) → World (3) ✗
```

### 3. Test Driven Development (TDD)
```
1. ÖNCE test yaz (RED)
2. SONRA implementation yaz (GREEN)
3. EN SON refactor yap (REFACTOR)
```

### 4. Mock Yasağı
```python
# YASAK
@patch('engine.renderer.Renderer')
def test_something(mock_renderer):  # ✗

# DOĞRU
def test_something():
    renderer = HeadlessGPU()  # ✓ Gerçek test double
```

### 5. Interface Kullanımı
```python
# Somut sınıfa değil interface'e bağımlılık
class Renderer2D:
    def __init__(self, gpu_device: IGPUDevice):  # ✓ Interface
        self._gpu = gpu_device
```

### 6. Third-Party Kütüphane Yerleşimi
```
moderngl, pyglet  → HAL katmanı (Layer 0)
Pillow            → engine/asset/ (Layer 2)
numpy             → core/math/ (Layer 1) veya engine/renderer/ (Layer 2)
```

---

## HEDEF ÖZELLİKLER (MAX SEVİYE)

### FAZ 1: Temel Render Pipeline (Temel)
| Modül | Satır | Açıklama |
|-------|-------|----------|
| Shader | 150 | Vertex + Fragment shader wrapper |
| Quad | 100 | GPU quad mesh (sprite için) |
| Texture | 150 | GPU texture yönetimi |
| Renderer2D | 180 | Ana render sınıfı |
| Camera | 120 | 2D kamera (pan, zoom, rotate) |

### FAZ 2: Sprite & Animation (Oyun Kalitesi)
| Modül | Satır | Açıklama |
|-------|-------|----------|
| Sprite | 150 | Transform, texture region |
| SpriteBatch | 180 | Batch rendering (1000+ sprite) |
| Animation | 150 | Frame-based animation |
| Spritesheet | 120 | Texture atlas desteği |

### FAZ 3: Lighting & Effects (İleri Seviye)
| Modül | Satır | Açıklama |
|-------|-------|----------|
| Light2D | 150 | Point light, ambient |
| LightRenderer | 180 | Light map rendering |
| Framebuffer | 150 | FBO wrapper |
| PostProcess | 180 | Bloom, blur pipeline |

### FAZ 4: Particles & VFX (Profesyonel)
| Modül | Satır | Açıklama |
|-------|-------|----------|
| Particle | 120 | Particle data class |
| ParticleEmitter | 150 | Emitter logic |
| ParticleRenderer | 180 | GPU particle rendering |
| EffectsManager | 150 | Screen shake, vignette |

---

## DOSYA YAPISI

```
engine/
├── hal/
│   ├── interfaces.py          # IGPUDevice, IWindow, IShader
│   ├── pyglet_backend.py      # PygletWindow, ModernGLDevice
│   └── headless.py            # HeadlessGPU (test için)
│
├── core/
│   ├── vec.py                 # Vec2, Vec3, Mat4
│   ├── color.py               # Color, ColorUtils
│   └── object.py              # Temel Object sınıfı
│
├── engine/
│   └── renderer/
│       ├── __init__.py
│       ├── shader.py          # Shader sınıfı
│       ├── quad.py            # Quad mesh
│       ├── texture.py         # Texture sınıfı
│       ├── renderer.py        # Renderer2D
│       ├── camera.py          # Camera2D
│       ├── sprite.py          # Sprite
│       ├── batch.py           # SpriteBatch
│       ├── animation.py       # Animation, AnimationPlayer
│       ├── spritesheet.py     # Spritesheet
│       ├── light.py           # Light2D
│       ├── light_renderer.py  # LightRenderer
│       ├── framebuffer.py     # Framebuffer
│       ├── postprocess.py     # PostProcess
│       ├── particle.py        # Particle
│       ├── particle_emitter.py # ParticleEmitter
│       ├── particle_renderer.py # ParticleRenderer
│       └── effects.py         # EffectsManager
│
└── tests/
    └── engine/
        └── renderer/
            ├── test_shader.py
            ├── test_quad.py
            ├── test_texture.py
            └── ... (her modül için test)
```

---

## ADIM ADIM GELİŞTİRME PLANI

### ADIM 1: Shader Sınıfı
**Girdi:**
- Vertex shader source (string)
- Fragment shader source (string)

**Çıktı:**
- Compiled shader program
- Uniform setter methods

**Test Senaryoları:**
```python
def test_shader_creation():
    """Shader oluşturulabilmeli"""
    gpu = HeadlessGPU()
    shader = Shader(gpu.context, vertex_src, fragment_src)
    assert shader.is_valid

def test_shader_uniform_set():
    """Uniform değer set edilebilmeli"""
    shader.set_uniform("u_color", (1.0, 0.0, 0.0, 1.0))
    assert shader.get_uniform("u_color") == (1.0, 0.0, 0.0, 1.0)
```

---

### ADIM 2: Quad Mesh
**Girdi:**
- Shader program
- Texture (opsiyonel)

**Çıktı:**
- GPU vertex buffer
- VAO (Vertex Array Object)
- draw() metodu

**Test Senaryoları:**
```python
def test_quad_creation():
    """Quad oluşturulabilmeli"""
    gpu = HeadlessGPU()
    quad = Quad(gpu.context)
    assert quad.vertex_count == 6  # 2 triangle

def test_quad_with_texture():
    """Texture'lı quad çizilebilmeli"""
    quad.set_texture(texture)
    assert quad.has_texture
```

---

### ADIM 3: Texture
**Girdi:**
- Image data (bytes) veya dosya yolu
- Width, height

**Çıktı:**
- GPU texture ID
- bind() / unbind() metodları

**Test Senaryoları:**
```python
def test_texture_from_file():
    """Dosyadan texture yüklenmeli"""
    tex = Texture.from_file("test.png")
    assert tex.width > 0
    assert tex.height > 0
    assert tex.data is not None

def test_texture_upload_to_gpu():
    """Texture GPU'ya upload edilmeli"""
    gpu = HeadlessGPU()
    tex = Texture.from_color(64, 64, (255, 0, 0, 255))
    gpu_id = gpu.create_texture(tex.width, tex.height, tex.data)
    assert gpu_id > 0
```

---

### ADIM 4: Renderer2D
**Girdi:**
- IGPUDevice instance
- Camera instance

**Çıktı:**
- begin() / end() frame yönetimi
- draw_sprite() metodu
- draw_texture() metodu

**Test Senaryoları:**
```python
def test_renderer_begin_end():
    """Frame başlangıç ve bitiş"""
    renderer = Renderer2D(gpu_device)
    renderer.begin()
    # ... draw calls
    renderer.end()

def test_renderer_draw_sprite():
    """Sprite çizilebilmeli"""
    sprite = Sprite(texture, position=Vec2(100, 100))
    renderer.draw_sprite(sprite)
    assert renderer.draw_count == 1
```

---

### ADIM 5: Camera2D
**Girdi:**
- Viewport size (width, height)

**Çıktı:**
- view matrix
- projection matrix
- pan, zoom, rotate metodları

**Test Senaryoları:**
```python
def test_camera_pan():
    """Kamera hareket ettirilebilmeli"""
    camera = Camera2D(800, 600)
    camera.pan(100, 50)
    assert camera.position == Vec2(100, 50)

def test_camera_zoom():
    """Kamera zoom yapılabilmeli"""
    camera.zoom(2.0)
    assert camera.zoom_level == 2.0
```

---

### ADIM 6: Sprite
**Girdi:**
- Texture reference
- Position, scale, rotation

**Çıktı:**
- Transform matrix
- Bounding box
- Serialization desteği

---

### ADIM 7: SpriteBatch
**Girdi:**
- List of sprites (aynı texture)

**Çıktı:**
- Tek draw call ile tüm spritelar
- Performance gain (1000+ sprites)

---

### ADIM 8-15: İleri Seviye Özellikler
(Her biri için detaylı spec aşağıda)

---

## SHADER SOURCE CODE

### Vertex Shader (sprite.vert)
```glsl
#version 330 core

in vec2 a_position;
in vec2 a_texcoord;
in vec4 a_color;

uniform mat4 u_projection;
uniform mat4 u_view;

out vec2 v_texcoord;
out vec4 v_color;

void main() {
    gl_Position = u_projection * u_view * vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
    v_color = a_color;
}
```

### Fragment Shader (sprite.frag)
```glsl
#version 330 core

in vec2 v_texcoord;
in vec4 v_color;

uniform sampler2D u_texture;

out vec4 frag_color;

void main() {
    vec4 tex_color = texture(u_texture, v_texcoord);
    frag_color = tex_color * v_color;

    // Alpha test
    if (frag_color.a < 0.01) discard;
}
```

### Post-Process Vertex Shader (post.vert)
```glsl
#version 330 core

in vec2 a_position;
in vec2 a_texcoord;

out vec2 v_texcoord;

void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
}
```

### Bloom Bright Extract (bright_extract.frag)
```glsl
#version 330 core

in vec2 v_texcoord;

uniform sampler2D u_texture;
uniform float u_threshold;
uniform float u_soft_threshold;

out vec4 frag_color;

float luminance(vec3 color) {
    return dot(color, vec3(0.2126, 0.7152, 0.0722));
}

void main() {
    vec4 color = texture(u_texture, v_texcoord);
    float brightness = luminance(color.rgb);

    float soft_knee = u_threshold - u_soft_threshold;
    float contribution = 0.0;

    if (brightness > u_threshold) {
        contribution = 1.0;
    } else if (brightness > soft_knee) {
        contribution = smoothstep(soft_knee, u_threshold, brightness);
    }

    frag_color = color * contribution;
}
```

### Gaussian Blur (blur.frag)
```glsl
#version 330 core

in vec2 v_texcoord;

uniform sampler2D u_texture;
uniform vec2 u_direction;
uniform vec2 u_texel_size;

out vec4 frag_color;

const float weights[3] = float[](0.227027, 0.316216, 0.070270);
const float offsets[2] = float[](1.384615, 3.230769);

void main() {
    vec4 color = texture(u_texture, v_texcoord) * weights[0];
    vec2 texel_offset = u_direction * u_texel_size;

    for (int i = 1; i < 3; i++) {
        color += texture(u_texture, v_texcoord + texel_offset * offsets[i-1]) * weights[i];
        color += texture(u_texture, v_texcoord - texel_offset * offsets[i-1]) * weights[i];
    }

    frag_color = color;
}
```

### Bloom Composite (bloom.frag)
```glsl
#version 330 core

in vec2 v_texcoord;

uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform float u_intensity;
uniform float u_exposure;
uniform int u_tone_mapping;

out vec4 frag_color;

vec3 reinhard(vec3 color) {
    return color / (color + vec3(1.0));
}

vec3 filmic(vec3 color) {
    vec3 x = max(vec3(0.0), color - 0.004);
    return (x * (6.2 * x + 0.5)) / (x * (6.2 * x + 1.7) + 0.06);
}

void main() {
    vec4 scene = texture(u_scene, v_texcoord);
    vec4 bloom = texture(u_bloom, v_texcoord);

    vec3 result = scene.rgb + bloom.rgb * u_intensity;
    result *= u_exposure;

    // Tone mapping
    if (u_tone_mapping == 1) {
        result = reinhard(result);
    } else if (u_tone_mapping == 2) {
        result = filmic(result);
    }

    // Gamma correction
    result = pow(result, vec3(1.0 / 2.2));

    frag_color = vec4(result, scene.a);
}
```

---

## INTERFACE TANIMLARI

### IGPUDevice (hal/interfaces.py)
```python
class IGPUDevice(ABC):
    @abstractmethod
    def create_texture(self, width: int, height: int, data: bytes = None) -> int: pass

    @abstractmethod
    def create_shader(self, vertex_src: str, fragment_src: str) -> int: pass

    @abstractmethod
    def create_buffer(self, data: bytes, usage: str = 'static') -> int: pass

    @abstractmethod
    def create_vertex_array(self, buffer_id: int, attributes: list) -> int: pass

    @abstractmethod
    def clear(self, r: float, g: float, b: float, a: float = 1.0) -> None: pass

    @abstractmethod
    def draw(self, vao_id: int, count: int, mode: str = 'triangles') -> None: pass

    @abstractmethod
    def set_uniform(self, shader_id: int, name: str, value: Any) -> None: pass

    @abstractmethod
    def flush(self) -> None: pass
```

### IShader (engine/renderer/shader.py)
```python
class IShader(ABC):
    @abstractmethod
    def use(self) -> None: pass

    @abstractmethod
    def set_uniform(self, name: str, value: Any) -> None: pass

    @abstractmethod
    def get_uniform_location(self, name: str) -> int: pass
```

### IRenderer (engine/renderer/renderer.py)
```python
class IRenderer(ISubsystem):
    @abstractmethod
    def begin(self) -> None: pass

    @abstractmethod
    def end(self) -> None: pass

    @abstractmethod
    def draw_sprite(self, sprite: "Sprite") -> None: pass

    @abstractmethod
    def draw_texture(self, texture: "Texture", x: float, y: float) -> None: pass
```

---

## TEST YAZMA KURALLARI

### Test Dosya Adı
```
Kaynak: engine/renderer/shader.py
Test: tests/engine/renderer/test_shader.py
```

### Test Sınıfı
```python
class TestShader:
    """Shader sınıfı testleri."""

    def setup_method(self):
        """Her test öncesi çalışır."""
        self.gpu = HeadlessGPU()
        self.ctx = self.gpu.context

    def teardown_method(self):
        """Her test sonrası çalışır."""
        # Cleanup
        pass

    def test_shader_creation(self):
        """Shader oluşturulabilmeli."""
        shader = Shader(self.ctx, VERTEX_SRC, FRAGMENT_SRC)
        assert shader.is_valid

    def test_shader_invalid_source(self):
        """Geçersiz kaynak hatası vermeli."""
        with pytest.raises(ShaderCompileError):
            Shader(self.ctx, "invalid", "invalid")
```

---

## PERFORMANS HEDEFLERİ

| Metrik | Hedef |
|--------|-------|
| 1000 sprite | 60 FPS |
| 10000 particle | 60 FPS |
| Bloom enabled | 60 FPS (1920x1080) |
| Draw calls | < 100 / frame |
| Texture memory | < 512 MB |

---

## ÇIKTI FORMATI

Her modül için şu formatta çıktı üret:

```
## [MODÜL ADI]

### Açıklama
[Modülün ne işe yaradığı]

### Girdi
- [Input 1]: [Tip] - [Açıklama]
- [Input 2]: [Tip] - [Açıklama]

### Çıktı
- [Output 1]: [Tip] - [Açıklama]

### Kod

```python
# tests/engine/renderer/test_[module].py
[Test kodu]
```

```python
# engine/renderer/[module].py
[Implementation kodu]
```

### Notlar
- [Önemli notlar]
- [Dikkat edilmesi gerekenler]
```

---

## BAŞLANGIÇ

Lütfen **ADIM 1: Shader Sınıfı** ile başla. TDD kurallarına uy:
1. Önce test yaz
2. Sonra implementation yaz
3. Her sınıf max 200 satır
4. Interface'leri kullan
5. Mock kullanma, HeadlessGPU kullan

---

**NOT:** Bu prompt bir yapay zeka modeline verilecek şekilde tasarlanmıştır. Her adımda sadece o adıma odaklanılmalı, diğer adımlara geçilmeden önce mevcut adım tamamlanmalı ve testler geçmelidir.
