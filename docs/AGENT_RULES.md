# ZORUNLU GELİŞTİRME KURALLARI
> Bu dosya AI agent tarafından geliştirme sürecinde SIKI SIKIYA uyulacaktır.
> İhlal = DURDUR ve düzelt. Devam etme.

---

## 1. İMPORT KURALLARI (KESİN İHLAL YASAK)

### 1.1 Yukarı Bağımlılık Kuralı
```
KATMAN NUMARASI: 0=HAL → 1=Core → 2=Engine → 3=World → 4=Game → 5=Scripting → 6=UI → 7=Editor

KURAL: Bir dosya SADECE kendi katmanındaki veya ALT katmanlardaki dosyaları import edebilir.
       ÜST katmandan import YASAKTIR.
```

**DOĞRU:**
```python
# engine/renderer/sprite.py - Katman 2
from core.object import Object        # ✓ Alt katman (1)
from core.vec import Vec2             # ✓ Alt katman (1)
from hal.interfaces import IWindow    # ✓ Alt katman (0)
```

**YASAK:**
```python
# core/object.py - Katman 1
from engine.renderer import Renderer  # ✗ ÜST katman - YASAK
from world.actor import Actor         # ✗ ÜST katman - YASAK
```

### 1.2 Döngüsel Import Yasağı
```
A → B → A  YASAKTIR
A → B → C → A  YASAKTIR
```

Çözüm:
- Type hint'ler için `from __future__ import annotations` + string olarak tip
- Late import: fonksiyon içinde import
- Interface/Protocol kullan

### 1.3 Import Çeşitliliği Sınırı
```
Bir dosya en fazla 5 farklı modülden import yapabilir.
Daha fazla = İHLAL → dosya çok büyük, böl.
```

### 1.4 Star Import Yasağı
```python
from module import *  # KESİNLİKLE YASAK
```

### 1.5 Third-Party Import Yerleşimi
```
Third-party kütüphaneler (pyglet, moderngl, pymunk, etc.)
SADECE kendi katmanlarında kullanılabilir.

pyglet, moderngl → hal/ (Layer 0)
pymunk           → engine/physics/ (Layer 2)
Pillow           → engine/asset/ (Layer 2)
watchdog         → engine/asset/ (Layer 2)
msgspec          → core/serializer.py (Layer 1)
dearpygui        → editor/ (Layer 7)
```

---

## 2. BAĞIMLILIK KURALLARI

### 2.1 Interface Bağımlılığı
```
Somut sınıfa bağımlılık YERİNE interface'e bağımlılık.
```

**DOĞRU:**
```python
# engine/renderer/renderer.py
from abc import ABC, abstractmethod

class IRenderer(ABC):
    @abstractmethod
    def draw_sprite(self, sprite: "Sprite") -> None: ...

# Somut implementation
class Renderer2D(IRenderer):
    def draw_sprite(self, sprite: "Sprite") -> None: ...
```

**KULLANIM:**
```python
# Diğer subsystem'ler IRenderer'ı bilir, Renderer2D'yi değil
def __init__(self, renderer: IRenderer):  # ✓ Interface
```

### 2.2 Dependency Injection Zorunluluğu
```
Global singleton YASAK (Engine hariç).
Gereken bağımlılıklar __init__ ile enjekte edilir.
```

**YASAK:**
```python
class Actor:
    def update(self):
        Engine.get().renderer.draw(...)  # ✗ Global erişim
```

**DOĞRU:**
```python
class Actor:
    def __init__(self, renderer: IRenderer):
        self._renderer = renderer
    
    def update(self):
        self._renderer.draw(...)  # ✓ Enjekte edilmiş
```

### 2.3 Event Bus İstisnası
```
Loose coupling için EventBus kullanılabilir.
EventBus core katmanındadır.
Event adları string değil enum/constant olmalı.
```

---

## 3. OVER-ENGINEER YASAKLARI

### 3.1 YAGNI (You Aren't Gonna Need It)
```
Şu an kullanılmayan kod YAZMA.
"İleride lazım olur" = YASAK.
```

### 3.2 Premature Abstraction Yasağı
```
Aynı pattern 3 kez görülmeden abstract/interface yazma.
```

**YASAK:**
```python
# Tek implementation varken interface yazma
class IWeapon(ABC): ...  # ✗ Henüz gereksiz
class Sword(IWeapon): ...
# Hiç başka weapon yok!
```

**DOĞRU:**
```python
class Sword: ...  # Önce somut yaz
class Bow: ...    # İkinci geldi
class Axe: ...    # Üçüncü geldi
# Şimdi IWeapon abstract edilebilir
```

### 3.3 Factory Factory Yasağı
```
Factory pattern maksimum 1 seviye.
AbstractFactoryFactory YASAK.
```

### 3.4 Magic Method Sınırı
```
__getattr__, __setattr__, __metaclass__ kullanımı:
- Core Object sistemi için ZORUNLU ise İZİN VAR
- Başka yerde YASAK
```

---

## 4. TEST ZORUNLULUĞU

### 4.1 Test-Olmadan-Commit Yasağı
```
Test dosyası OLMADAN implementation dosyası yazılamaz.
Her .py dosyasının tests/test_{name}.py karşılığı ZORUNLU.
```

### 4.2 Test Sırası
```
1. ÖNCE test yaz (RED)
2. SONRA implementation yaz (GREEN)
3. EN SON refactor yap (REFACTOR)
```

### 4.3 Mock Yasağı
```
Mock kullanımı YASAK - gerçek implementation test et.
Integration test yoluyla gerçek bağımlılıkları kullan.
```

**YASAK:**
```python
@patch('engine.renderer.Renderer')
def test_actor(mock_renderer):  # ✗ Mock
```

**DOĞRU:**
```python
def test_actor():
    renderer = HeadlessGPU()  # ✓ Gerçek test double
    actor = Actor(renderer=renderer)
```

### 4.4 Headless Backend Zorunluluğu
```
HAL katmanında IWindow, IGPUDevice interfaceleri vardır.
Test için HeadlessWindow, HeadlessGPU implementasyonları ZORUNLU.
Bu sayede CI ortamında GPU olmadan test çalışır.
```

---

## 5. KOD STANDARTLARI

### 5.1 Sınıf Boyutu Sınırı
```
Bir sınıf maksimum 200 satır.
Daha fazla = BÖL.
```

### 5.2 Fonksiyon Boyutu Sınırı
```
Bir fonksiyon maksimum 30 satır.
Daha fazla = BÖL.
```

### 5.3 Parametre Sayısı Sınırı
```
Bir fonksiyon maksimum 4 parametre.
Daha fazla = config object kullan.
```

### 5.4 Docstring Zorunluluğu
```python
def func(self, x: int) -> bool:
    """
    Kısa açıklama.
    
    Args:
        x: Parametre açıklaması
    
    Returns:
        Dönüş değeri açıklaması
    """
```

---

## 6. DİSİPLİN PROSEDÜRÜ

### 6.1 Adım Prosedürü
```
1. agent_state.json OKU → mevcut durumu anla
2. Test DOSYASINI yaz (henüz implementation yok)
3. Test'i ÇALIŞTIR → RED olduğunu gör
4. Implementation YAZ
5. Test'i ÇALIŞTIR → GREEN olduğunu gör
6. agent_state.json GÜNCELLE
7. Sonraki adıma geç
```

### 6.2 İhlal Durumunda
```
İhlal tespit edilirse:
1. DURDUR
2. İhlali düzelt
3. Tekrar test et
4. Devam et
```

### 6.3 Onay Mekanizması
```
Her adım bitiminde:
- Test GREEN mi?
- Import kuralları OK mu?
- Bağımlılık kuralları OK mu?
- Over-engineer YOK mu?

Hepsi EVET → İleri git
Bir tane HAYIR → Düzelt
```

---

## 7. YASAKLAR LİSTESİ (ÖZET)

| YASAK | AÇIKLAMA |
|-------|----------|
| `import *` | Star import |
| Üst katman import | Daha yüksek numaralı katmandan import |
| Döngüsel import | A→B→A veya A→B→C→A |
| Global singleton | Engine.get() hariç |
| Mock | Gerçek test double kullan |
| Dead code | Kullanılmayan fonksiyon/sınıf |
| Commented code | Yorum satırında kod |
| Magic number | Sabit tanımla |
| Premature abstraction | 3 kez görmeden interface yazma |
| Unused import | Import edilip kullanılmayan |
| Type: ignore | mypy hatasını gizleme |

---

## 8. KATMAN REFERANSI

```
0. HAL         - window (pyglet), gpu (moderngl), filesystem, clock
1. CORE        - object, reflection, eventbus, serializer (msgspec)
2. ENGINE      - subsystem, renderer, physics (pymunk), audio, input, asset (Pillow)
3. WORLD       - world, level, actor, component, system, prefab
4. GAME        - gamemode, controller, inventory, quest, save
5. SCRIPTING   - statemachine, behaviour_tree, event_graph
6. UI          - widget, canvas, label, button
7. EDITOR      - viewport, hierarchy, properties (DearPyGui)
```

---

## 9. THIRD-PARTY KÜTÜPHANE KULLANIMI

### 9.1 Pyglet (Window/Input)
```python
# SADECE hal/pyglet_backend.py içinde
import pyglet
from pyglet.window import Window

class PygletWindow(IWindow):
    def __init__(self, width: int, height: int):
        self._window = pyglet.window.Window(width, height)
```

### 9.2 ModernGL (GPU)
```python
# SADECE hal/pyglet_backend.py ve engine/renderer/ içinde
import moderngl

class ModernGLDevice(IGPUDevice):
    def __init__(self):
        self._ctx = moderngl.create_context()
```

### 9.3 Pymunk (Physics)
```python
# SADECE engine/physics/ içinde
import pymunk

class Physics2D(ISubsystem):
    def __init__(self):
        self._space = pymunk.Space()
```

### 9.4 Pillow (Images)
```python
# SADECE engine/asset/ içinde
from PIL import Image

class AssetLoader:
    def load_texture(self, path: str) -> Texture:
        img = Image.open(path)
```

### 9.5 msgspec (Serialization)
```python
# SADECE core/serializer.py içinde
import msgspec

class Serializer:
    def serialize(self, data: Any) -> bytes:
        return msgspec.json.encode(data)
```

### 9.6 DearPyGui (Editor)
```python
# SADECE editor/ içinde
import dearpygui.dearpygui as dpg

class Editor:
    def run(self):
        dpg.create_context()
        # ...
```

---

**BU KURALLAR TARTIŞILAMAZ. İHLAL = DURDUR.**
