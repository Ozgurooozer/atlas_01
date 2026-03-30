# Render Quick Wins Raporu

Bu rapor, projede en hızlı değer üretecek 5 iyileştirmeyi listeler.  
Odak: 1-2 saat içinde uygulanabilir, riski düşük, etkisi yüksek adımlar.

## 1) `.hypothesis/` çıktısını git dışında tut

- **Sorun:** Test artefaktları repoya düşüyor, PR ve diff gürültüsü oluşuyor.
- **Etki:** Temiz repo, daha anlaşılır PR, daha az yanlış conflict.
- **Efor:** 5 dakika.
- **Uygulama:**
  - `.gitignore` dosyasına aşağıdakini ekle:
    - `.hypothesis/`

## 2) Render performans benchmark komutu ekle

- **Sorun:** "Hangi çözünürlükte ne kadar FPS?" sorusuna ölçüm yok.
- **Etki:** Teknik kararlar veriyle alınır; Unity/GameMaker kıyası netleşir.
- **Efor:** 1-2 saat.
- **Uygulama (minimum):**
  - `scripts/benchmark_render.py` oluştur.
  - 3 senaryo ölç:
    - 5k sprite, ışık kapalı
    - 5k sprite + 32 point light
    - 10k sprite + postprocess açık
  - Çözünürlük matrisi:
    - `1280x720`, `1920x1080`, `2560x1440`
  - Çıktı:
    - Ortalama FPS
    - p95 frametime (ms)
    - draw call sayısı

## 3) Post-process pass’lerinde "gerçek efekt yoksa fail-fast" davranışı

- **Sorun:** Bazı pass’ler iskelet/no-op; aktif görünüp etkisiz kalabilir.
- **Etki:** Sessiz kalite kaybı önlenir, debug süresi azalır.
- **Efor:** 1 saat.
- **Uygulama:**
  - `PostProcessPass` türevlerinde efekt uygulanmıyorsa:
    - ya `enabled=False` ile varsayılan kapat
    - ya da bir uyarı/log üret (`debug` seviyesinde)
  - "Boş pass yanlışlıkla açık" durumuna test ekle.

## 4) Renderer ve LightRenderer arasına küçük API sınırı koy

- **Sorun:** İç alanlara (`_lights` gibi) erişim bağımlılığı var.
- **Etki:** Refactor güvenliği artar, modüller daha temiz olur.
- **Efor:** 1-2 saat.
- **Uygulama (minimum):**
  - `LightRenderer` içine salt-okunur getter ekle:
    - `get_visible_point_lights(max_count=8)`
  - `Renderer2D` tarafında doğrudan `_lights` yerine bu API kullan.
  - Mevcut davranışı koruyan 1-2 test ekle.

## 5) Render smoke test’i CI’ye hızlı gate olarak ekle

- **Sorun:** Tüm testler geçse de render akış regresyonları geç fark edilebilir.
- **Etki:** Erken kırılım yakalama, daha güvenli merge.
- **Efor:** 30-60 dakika.
- **Uygulama:**
  - CI’de ayrı bir job:
    - `tests/engine/renderer`
    - `tests/hal/test_moderngl_device.py`
  - Kriter:
    - PR’da bu set fail olursa merge bloklansın.

---

## Öncelik Sırası (önerilen)

1. `.hypothesis/` ignore
2. CI render smoke gate
3. Post-process fail-fast
4. Light API sınırı
5. Benchmark script

## Beklenen Sonuç (kısa vade)

- Daha temiz repo ve daha güvenli PR akışı
- Render regressions daha erken yakalanır
- Çözünürlük/FPS iddiaları ölçülebilir hale gelir
- Mimari sürdürülebilirlik artar (daha az private coupling)
