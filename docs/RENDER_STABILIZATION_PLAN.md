# Render Stabilization Plan (Game-First Freeze)

Bu dokümanın amacı render tarafını optimize etmek değil, **stabil ve öngörülebilir hale getirip oyun geliştirmeye geçmeyi** sağlamaktır.

## Kapsam (Yeterli Seviye)

Render tarafında aşağıdakiler desteklenirse yeterli kabul edilir:

- `Side Scroller` kamera/projeksiyon
- `Isometric` kamera/projeksiyon
- Temel sprite çizimi
- Temel batch akışı
- Temel ışık (gerekirse limitli)

## Feature Freeze Kararı

Bu aşamada aşağıdaki gelişmiş/deneysel parçalar varsayılan olarak kapalı tutulur:

- SSAO
- Deferred pipeline (oyun ihtiyacı netleşene kadar)
- Deneysel/yarım post-process pass'ler
- Render path içinde davranışı belirsiz fallback'ler

Not: Kapatmak silmek anlamına gelmez. Kod durur ama oyun runtime'ında aktif edilmez.

## Stabilizasyon İlkeleri

- Tek runtime render yolu: oyun için birincil ve sabit pipeline.
- Public API dışına erişim yok (`_internal` alan kullanımı yok).
- Sessiz hata yok: log + fallback.
- Frame kontratı sabit:
  - `begin_frame -> draw calls -> end_frame -> present`
- Render config tek yerden yönetilir (known-good preset).

## Minimum Teknik Checklist

## 1) API Kilitleme

- Oyun kodunun kullanacağı API netleştirilir:
  - `Renderer2D`
  - `SpriteBatch`
  - `Camera` (side scroller + isometric)
  - `LightRenderer` (temel kullanım)
- Bu API dışında erişim engellenir.

## 2) Mod Sabitleme

- Varsayılan kamera modu side scroller.
- Isometric mod açık ve testli.
- Runtime sırasında gereksiz mod değişimi kapatılır veya sınırlandırılır.

## 3) Render Hata Politikası

- Eksik texture: placeholder (ör. magenta) ile çizim.
- Shader derleme/bağlama hatası: tek tip hata + fallback shader/material.
- `print` yerine merkezi logger kullanımı.

## 4) Test ve Smoke Gate

- Aşağıdaki testler merge öncesi sürekli çalışır:
  - `tests/engine/renderer`
  - `tests/hal/test_moderngl_device.py`
- 2 adet smoke sahne:
  - side scroller gameplay sahnesi
  - isometric gameplay sahnesi
- Hedef: crash, siyah ekran, frame akışı bozulması yakalamak.

## 5) Konfigürasyon Donması

- Aşağıdaki değerler release profiline sabitlenir:
  - çözünürlük stratejisi
  - light limiti
  - batch limiti
  - vsync / frame pacing

## "Done" Tanımı (Stabil Render)

Aşağıdaki koşullar sağlanınca render tarafı “game-ready stable” kabul edilir:

- 1 hafta aktif geliştirmede render kaynaklı kritik crash yok.
- Side scroller ve isometric sahneler smoke testte sürekli geçiyor.
- Oyun ekibi yeni render feature istemeden içerik üretmeye devam edebiliyor.
- Bilinen render limitleri ve workaround'lar dokümante edilmiş durumda.

## Oyun Geliştirmeye Geçiş Kararı

Bu dokümanla birlikte yaklaşım şudur:

- Engine render tarafında yeni feature ekleme durdurulur.
- Sadece bugfix + stabilite odaklı bakım yapılır.
- Ana geliştirme odağı: oyun mekaniği, seviye, içerik, asset entegrasyonu.

