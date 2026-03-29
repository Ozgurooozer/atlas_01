"""
RenderLogger — Merkezi render uyarı/hata loglama.

print() yerine bu kullanılır. Sessiz hata yok.

Layer: 2 (Engine)
Dependencies: warnings, logging
"""
from __future__ import annotations
import logging
import warnings
from typing import Optional

_logger = logging.getLogger("engine.renderer")


class RenderLogger:
    """
    Merkezi render log yöneticisi.

    Kullanım:
        RenderLogger.warn("Texture missing: player.png")
        RenderLogger.error("Shader compile failed", exc=e)
    """

    _enabled: bool = True

    @classmethod
    def warn(cls, message: str, category: type = UserWarning) -> None:
        """
        Render uyarısı üret.

        Hem Python warnings sistemine hem de logger'a yazar.
        """
        if not cls._enabled:
            return
        _logger.warning("[Render] %s", message)
        warnings.warn(f"[Render] {message}", category, stacklevel=2)

    @classmethod
    def error(cls, message: str, exc: Optional[Exception] = None) -> None:
        """
        Render hatası logla. Exception varsa zincire ekle.
        """
        if exc is not None:
            _logger.error("[Render] %s: %s", message, exc, exc_info=exc)
        else:
            _logger.error("[Render] %s", message)

    @classmethod
    def debug(cls, message: str) -> None:
        """Debug seviyesinde log."""
        _logger.debug("[Render] %s", message)

    @classmethod
    def silence(cls) -> None:
        """Tüm render loglarını sustur (test ortamı için)."""
        cls._enabled = False

    @classmethod
    def unsilence(cls) -> None:
        """Render loglarını tekrar aktif et."""
        cls._enabled = True
