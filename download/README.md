# 🔥 2D Game Engine

Unreal Engine felsefesiyle 2D oyun motoru - Python'da modüler, test edilebilir, genişletilebilir.

## 🎯 Özellikler

- **Her şey Object** - Actor, Component, Widget hepsi Object'ten türetilir
- **Reflection sistemi** - Editor otomatik çalışır, ek kod gerektirmez
- **Subsystem pattern** - Modüler genişleme, yeni subsystem eklemek kolay
- **Test-driven** - 1340 test, %100 coverage hedefi
- **Headless testing** - CI'da GPU olmadan çalışır
- **Sprite rendering** - Texture yükleme, sprite çizme, batch rendering
- **Camera sistemi** - Zoom, rotation, bounds, follow target
- **Advanced Renderer** - Shader, Animation, Light, Spritesheet

## 📦 Bağımlılıklar

| Paket | Amaç |
|-------|------|
| pyglet >= 2.0 | Window/GL context |
| moderngl >= 5.10 | Modern OpenGL |
| pymunk >= 7.2 | 2D Physics |
| Pillow >= 10.0 | Texture loading |
| msgspec >= 0.18 | Fast serialization |
| watchdog >= 4.0 | Hot reload |
| dearpygui >= 1.13 | Editor UI |

## 🚀 Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Testleri çalıştır
pytest tests/ -v
```

## 📁 Proje Yapısı

```
engine/
├── hal/                    # Layer 0: Hardware Abstraction
│   ├── interfaces.py       # IWindow, IGPUDevice, IFilesystem, IClock
│   ├── headless.py         # Test implementations
│   ├── pyglet_backend.py   # Real window/GPU
│   └── os_filesystem.py    # Real filesystem
│
├── core/                   # Layer 1: Foundation
│   ├── guid.py             # Unique identifiers
│   ├── object.py           # Base class for everything
│   ├── reflection.py       # @reflect decorator
│   ├── eventbus.py         # Pub/sub system
│   ├── signal.py           # Signal/Slot
│   ├── config.py           # Config system
│   ├── logger.py           # Logging
│   ├── vec.py              # Vec2, Vec3
│   ├── scheduler.py        # Delayed callbacks
│   └── profiler.py         # Performance profiling
│
├── engine/                 # Layer 2: Subsystems
│   ├── engine.py           # Engine class
│   ├── subsystem.py        # ISubsystem interface
│   ├── renderer/           # 2D Rendering
│   │   ├── renderer.py     # Renderer2D
│   │   ├── texture.py      # Texture + TextureLoader
│   │   ├── sprite.py       # Sprite class
│   │   ├── batch.py        # SpriteBatch
│   │   └── camera.py       # Camera system
│   ├── physics/            # 2D Physics (Pymunk)
│   ├── input/              # Input handling
│   └── asset/              # Asset management
│
├── world/                  # Layer 3: Actor/Component
│   ├── world.py            # World container
│   ├── actor.py            # Actor class
│   ├── component.py        # Component base
│   ├── transform.py        # TransformComponent
│   ├── level.py            # Level management
│   └── prefab.py           # Prefab system
│
├── game/                   # Layer 4: Game logic
│   ├── gamemode.py         # GameMode base
│   ├── controller.py       # Controllers
│   ├── inventory/          # Inventory system
│   ├── quest/              # Quest system
│   └── dialogue/           # Dialogue system
│
├── scripting/              # Layer 5: AI/Scripting
│   ├── statemachine.py     # Hierarchical State Machine
│   └── behaviour_tree.py   # Behaviour Tree
│
├── ui/                     # Layer 6: Widgets
│   ├── widget.py           # Widget base
│   ├── canvas.py           # Canvas container
│   ├── label.py            # Label widget
│   ├── button.py           # Button widget
│   └── panel.py            # Panel widget
│
└── editor/                 # Layer 7: Editor
    ├── main.py             # Editor application
    ├── viewport.py         # Scene viewport
    ├── hierarchy.py        # Hierarchy panel
    ├── properties.py       # Properties panel
    └── asset_browser.py    # Asset browser
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Coverage ile
pytest tests/ --cov=. --cov-report=html
```

## 📖 Dokümantasyon

- [AGENT_RULES.md](AGENT_RULES.md) - Geliştirme kuralları
- [ARCHITECTURE.md](ARCHITECTURE.md) - Mimari tasarım
- [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md) - AI development prosedürü

## 📊 Durum

**FAZ 1: Foundation** ✅ TAMAMLANDI
**FAZ 2: Engine Skeleton** ✅ TAMAMLANDI
**FAZ 3: World/ECS** ✅ TAMAMLANDI
**FAZ 4: Subsystems** ✅ TAMAMLANDI
- Renderer2D (draw_sprite, draw_texture)
- Texture (from_file, from_bytes, save)
- SpriteBatch (z-sorting, texture batching)
- Camera (zoom, rotation, bounds, follow)

**FAZ 5: Game & UI** ✅ TAMAMLANDI
**FAZ 6: Editor** ✅ TAMAMLANDI

**Toplam: 770 test geçiyor** ✅

## 📜 Lisans

MIT
