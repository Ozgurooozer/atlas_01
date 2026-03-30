"""
RenderConfig — Render pipeline konfigürasyonu tek yerden yönetir.

Known-good preset: oyun geliştirme için stabil, deneysel özellikler kapalı.

Layer: 2 (Engine)
Dependencies: dataclasses
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class RenderConfig:
    """
    Render pipeline konfigürasyonu.

    Tüm render parametreleri buradan okunur.
    Oyun kodu bu config'i değiştirerek render davranışını kontrol eder.

    Known-good preset (varsayılan):
    - SSAO kapalı
    - Deferred pipeline kapalı
    - Forward lighting, max 32 ışık
    - Post-process stack kapalı
    - Batch limit 1000
    """

    # --- Çözünürlük ---
    width: int = 1280
    height: int = 720
    vsync: bool = True

    # --- Lighting ---
    max_lights: int = 32          # LightRenderer.MAX_LIGHTS ile uyumlu
    ambient_intensity: float = 0.15
    ambient_color: Tuple[float, float, float] = (0.15, 0.15, 0.2)

    # --- Render path ---
    ssao_enabled: bool = False        # Feature freeze: kapalı
    deferred_enabled: bool = False    # Feature freeze: kapalı
    postprocess_enabled: bool = False # Feature freeze: kapalı

    # --- Batch ---
    batch_limit: int = 1000
    instancing_enabled: bool = True

    # --- Hata politikası ---
    missing_texture_color: Tuple[int, int, int, int] = (255, 0, 255, 255)  # magenta
    log_render_warnings: bool = True

    @classmethod
    def game_ready(cls) -> "RenderConfig":
        """
        Known-good preset — oyun geliştirme için stabil konfigürasyon.

        Deneysel özellikler kapalı, temel pipeline aktif.
        """
        return cls(
            width=1280,
            height=720,
            vsync=True,
            max_lights=32,
            ssao_enabled=False,
            deferred_enabled=False,
            postprocess_enabled=False,
            batch_limit=1000,
            instancing_enabled=True,
        )

    @classmethod
    def performance(cls) -> "RenderConfig":
        """
        Performans odaklı preset — düşük ışık limiti, instancing açık.
        """
        return cls(
            width=1280,
            height=720,
            vsync=False,
            max_lights=16,
            ssao_enabled=False,
            deferred_enabled=False,
            postprocess_enabled=False,
            batch_limit=2000,
            instancing_enabled=True,
        )

    @classmethod
    def quality(cls) -> "RenderConfig":
        """
        Kalite odaklı preset — daha fazla ışık, post-process açık.
        Deneysel: post-process pass'ler implement edilince aktif edilmeli.
        """
        return cls(
            width=1920,
            height=1080,
            vsync=True,
            max_lights=32,
            ssao_enabled=False,      # Henüz stabil değil
            deferred_enabled=False,  # Henüz stabil değil
            postprocess_enabled=False,
            batch_limit=1000,
            instancing_enabled=True,
        )
