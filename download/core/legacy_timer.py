"""
Legacy Timer - Eski manuel timer sisteminin wrapper'ı.

Bu modül, TimerValidator ile karşılaştırma yapmak için
eski manuel timer davranışını taklit eder.

Layer: 1 (Core)
Dependencies: None (stdlib only)

Kullanım:
    timer = LegacyTimer()
    handle = timer.add_timer(1.0, my_callback)
    timer.tick(dt)  # Her frame'de çağır
    timer.cancel(handle)  # İptal et
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TimerEntry:
    """
    Tek bir timer kaydı.

    Attributes:
        handle: Timer'ın unique ID'si.
        remaining: Kalan süre (saniye).
        callback: Tetiklenecek fonksiyon.
    """
    handle: int
    remaining: float
    callback: Callable[[], None]


class LegacyTimer:
    """
    Eski manuel timer sisteminin davranışını taklit eder.

    Shooter demo'sundaki manuel timer mantığını kapsüller:
    - add_timer: Timer ekler
    - tick: Zamanı ilerletir, süresi dolan callback'leri çağırır
    - cancel: Timer'ı iptal eder

    Example:
        >>> timer = LegacyTimer()
        >>> timer.add_timer(2.0, lambda: print("2 saniye geçti"))
        >>> timer.tick(1.0)  # Henüz tetiklenmez
        >>> timer.tick(1.0)  # Tetiklenir
    """

    def __init__(self):
        """Boş bir timer sistemi oluştur."""
        self._timers: Dict[int, TimerEntry] = {}
        self._next_handle: int = 1

    @property
    def pending_count(self) -> int:
        """
        Bekleyen timer sayısını döndür.

        Returns:
            Henüz tetiklenmemiş timer sayısı.
        """
        return len(self._timers)

    def add_timer(self, delay: float, callback: Callable[[], None]) -> int:
        """
        Yeni bir timer ekle.

        Args:
            delay: Gecikme süresi (saniye).
                   Negatif veya sıfır ise hemen tetiklenir.
            callback: Süre dolduğunda çağrılacak fonksiyon.

        Returns:
            Timer handle (iptal için kullanılır).

        Example:
            >>> handle = timer.add_timer(0.5, my_func)
        """
        handle = self._next_handle
        self._next_handle += 1

        # Negatif gecikmeyi sıfıra çevir
        actual_delay = max(0.0, delay)

        self._timers[handle] = TimerEntry(
            handle=handle,
            remaining=actual_delay,
            callback=callback
        )

        return handle

    def tick(self, dt: float) -> None:
        """
        Zamanı ilerlet ve süresi dolan timer'ları tetikle.

        Args:
            dt: Geçen süre (saniye).

        Note:
            Callback'ler sırasıyla tetiklenir. Callback içinde
            yeni timer eklenebilir. Exception'lar yutulur.
        """
        # Süresi dolan timer'ları bul
        to_fire: List[TimerEntry] = []

        for timer in self._timers.values():
            timer.remaining -= dt
            if timer.remaining <= 0:
                to_fire.append(timer)

        # Tetikle ve kaldır
        for timer in to_fire:
            # Önce kaldır (callback içinde cancel olabilir)
            if timer.handle in self._timers:
                del self._timers[timer.handle]

                # Callback'i çağır (exception'ı yakala)
                try:
                    timer.callback()
                except Exception:
                    pass  # Exception yutulur

    def cancel(self, handle: int) -> bool:
        """
        Timer'ı iptal et.

        Args:
            handle: add_timer'dan dönen handle.

        Returns:
            True: Timer bulundu ve iptal edildi.
            False: Timer bulunamadı (zaten tetiklenmiş olabilir).

        Example:
            >>> handle = timer.add_timer(5.0, my_func)
            >>> timer.cancel(handle)
            True
        """
        if handle in self._timers:
            del self._timers[handle]
            return True
        return False

    def clear(self) -> None:
        """
        Tüm timer'ları kaldır.

        Oyun resetlenirken kullanılır.
        """
        self._timers.clear()


__all__ = ['LegacyTimer', 'TimerEntry']
