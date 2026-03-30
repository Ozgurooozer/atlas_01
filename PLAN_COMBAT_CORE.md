# Combat Core Kurulum Planı

## Not: Physics2D Kapsam Kararı

- Hades-benzeri isometric roguelike action için mevcut `Physics2D` yeterli başlangıç seviyesindedir.
- Bu fazda hedef gerçekçi fizik değil, combat hissi ve tutarlı kurallardır.
- Bu yüzden plan:
  - kinematik hareket
  - overlap tabanlı hitbox/hurtbox
  - cooldown + i-frame + basit status etkileri
  - minimum gerekli çarpışma kuralları
  ile ilerler.

## Amaç

- Mevcut altyapıyı (Actor/Component, Overlap, Scheduler, EventBus, Script/StateMachine) kullanarak oyunda hemen kullanılabilir bir Combat Core kurmak.
- Combat Core; hasar çözümü, hit/hurtbox, cooldown, i-frame, durum efektleri ve olay yayınını tek bir omurgada toplar.
- Render/engine feature genişletmesi yapılmaz; sadece gerekli entegrasyon ve bugfix yapılır.

## Uygulama Aşamaları

1. Domain + Health/Stats/Combatant
2. Hitbox/Hurtbox + overlap mapping
3. Damage system + combat events
4. Cooldown + i-frame + 2 status effect (poison/burn)
5. Input/AI bağlama
6. Combat polish köprüsü + save + test genişletme

## Önerilen Dosyalar

- `game/combat/model.py`
- `game/combat/system.py`
- `game/combat/effects.py`
- `world/components/health_component.py`
- `world/components/combat_stats_component.py`
- `world/components/combatant_component.py`
- `world/components/combat_state_component.py`
- `world/components/hitbox_component.py`
- `world/components/hurtbox_component.py`

## Entegrasyon Dokunuşları

- `world/components/engine_context.py`
- `world/world.py`
- `engine/physics/overlap.py`
- `game/controller.py`
- `engine/input/input_handler.py`
- `game/save/save.py`
- `engine/game/combat_polish.py`

## Test Planı

- `tests/game/test_combat_damage.py`
- `tests/game/test_combat_hitbox_hurtbox.py`
- `tests/game/test_combat_cooldown_iframe.py`
- `tests/game/test_combat_effects.py`

## Done Kriteri

- Oyuncu ve düşman arasında kararlı hasar alışverişi var.
- Cooldown, i-frame ve team filter doğru çalışıyor.
- Combat eventleri polish/UI katmanına güvenli akıyor.
- Save/load sonrası combat state bozulmuyor.
- En az bir vertical slice odasında 10+ dakika crashsiz combat oynanabiliyor.
