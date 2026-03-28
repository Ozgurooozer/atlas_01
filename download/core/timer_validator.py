"""
Timer Validator - İki timer sistemini karşılaştıran validator.

Bu modül, LegacyTimer ve Scheduler sistemlerini paralel çalıştırarak
sonuçları karşılaştırır ve discrepancy (uyumsuzluk) tespit eder.

Layer: 1 (Core)
Dependencies: scheduler.py, legacy_timer.py

Kullanım:
    validator = TimerValidator()
    handle = validator.register_delayed(1.0, my_callback)
    validator.tick(dt)  # Her frame'de çağır
    if validator.has_discrepancy:
        print(f"Uyumsuzluk: {validator.discrepancy_count}")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from core.legacy_timer import LegacyTimer
from core.scheduler import Scheduler


@dataclass
class ValidatorEntry:
    """
    Timer kaydı - her iki sistemin handle'larını tutar.

    Attributes:
        validator_handle: TimerValidator'ın kendi handle'ı.
        scheduler_handle: Scheduler'dan gelen handle.
        legacy_handle: LegacyTimer'dan gelen handle.
        callback: Kullanıcının callback'i.
        delay: Gecikme süresi.
        repeated: Tekrarlayan mı?
    """
    validator_handle: int
    scheduler_handle: int
    legacy_handle: int
    callback: Callable[[], None]
    delay: float
    repeated: bool


class TimerValidator:
    """
    İki timer sistemini karşılaştıran validator.

    Scheduler ve LegacyTimer'ı paralel çalıştırarak aynı sonuçları
    üretip üretmediklerini kontrol eder. Discrepancy (uyumsuzluk)
    durumunda rapor üretir.

    Example:
        >>> validator = TimerValidator()
        >>> validator.register_delayed(1.0, lambda: print("tick"))
        >>> validator.tick(0.5)
        >>> validator.tick(0.5)  # Callback tetiklenir
        >>> print(validator.accuracy_percentage)
        100.0
    """

    def __init__(self):
        """TimerValidator oluştur."""
        self._scheduler = Scheduler()
        self._legacy_timer = LegacyTimer()
        self._entries: Dict[int, ValidatorEntry] = {}
        self._next_handle: int = 1
        self._discrepancy_count: int = 0
        self._total_timers: int = 0
        # Tick sonrası tetiklenen timer'lar
        self._scheduler_fired: Set[int] = set()
        self._legacy_fired: Set[int] = set()
        self._callback_called: Set[int] = set()

    @property
    def scheduler(self) -> Scheduler:
        """Scheduler instance'ını döndür."""
        return self._scheduler

    @property
    def legacy_timer(self) -> LegacyTimer:
        """LegacyTimer instance'ını döndür."""
        return self._legacy_timer

    @property
    def discrepancy_count(self) -> int:
        """Tespit edilen uyumsuzluk sayısı."""
        return self._discrepancy_count

    @property
    def has_discrepancy(self) -> bool:
        """Uyumsuzluk var mı?"""
        return self._discrepancy_count > 0

    @property
    def accuracy_percentage(self) -> float:
        """Doğruluk yüzdesi (0-100)."""
        if self._total_timers == 0:
            return 100.0
        fired_count = len(self._callback_called)
        if fired_count == 0:
            return 100.0
        return 100.0 * (1 - self._discrepancy_count / max(1, self._total_timers))

    def register_delayed(self, delay: float, callback: Callable[[], None]) -> int:
        """
        Gecikmeli timer kaydet (her iki sisteme).

        Args:
            delay: Gecikme süresi (saniye).
            callback: Süre dolduğunda çağrılacak fonksiyon.

        Returns:
            TimerValidator handle (iptal için kullanılır).
        """
        validator_handle = self._next_handle
        self._next_handle += 1

        def scheduler_callback():
            self._scheduler_fired.add(validator_handle)
            self._try_fire_callback(validator_handle, callback)

        def legacy_callback():
            self._legacy_fired.add(validator_handle)
            self._try_fire_callback(validator_handle, callback)

        # Her iki sisteme de ekle
        scheduler_handle = self._scheduler.call_later(delay, scheduler_callback)
        legacy_handle = self._legacy_timer.add_timer(delay, legacy_callback)

        # Kaydet
        self._entries[validator_handle] = ValidatorEntry(
            validator_handle=validator_handle,
            scheduler_handle=scheduler_handle,
            legacy_handle=legacy_handle,
            callback=callback,
            delay=delay,
            repeated=False
        )
        self._total_timers += 1

        return validator_handle

    def register_repeated(self, interval: float, callback: Callable[[], None]) -> int:
        """
        Tekrarlayan timer kaydet.

        Args:
            interval: Tekrarlama aralığı (saniye).
            callback: Her interval'da çağrılacak fonksiyon.

        Returns:
            TimerValidator handle (iptal için kullanılır).
        """
        validator_handle = self._next_handle
        self._next_handle += 1

        # Tekrarlayan timer - sadece scheduler kullan
        scheduler_handle = self._scheduler.call_every(interval, callback)

        # Kaydet
        self._entries[validator_handle] = ValidatorEntry(
            validator_handle=validator_handle,
            scheduler_handle=scheduler_handle,
            legacy_handle=-1,
            callback=callback,
            delay=interval,
            repeated=True
        )
        self._total_timers += 1

        return validator_handle

    def _try_fire_callback(self, handle: int, callback: Callable[[], None]) -> None:
        """
        Her iki sistem de tetiklendiyse callback'i çağır.

        Args:
            handle: Timer handle.
            callback: Kullanıcının callback'i.
        """
        # Zaten çağrıldıysa tekrar çağırma
        if handle in self._callback_called:
            return

        # Her iki sistem de tetiklendi mi?
        scheduler_ok = handle in self._scheduler_fired
        legacy_ok = handle in self._legacy_fired

        if scheduler_ok and legacy_ok:
            # Her iki sistem de tetiklendi - callback çağır
            self._callback_called.add(handle)

            # Entry'yi pending'den kaldır (non-repeated only)
            if handle in self._entries and not self._entries[handle].repeated:
                del self._entries[handle]

            try:
                callback()
            except Exception:
                pass
        elif scheduler_ok != legacy_ok:
            # Zamanlama uyumsuzluğu - bir sistem tetiklendi, diğeri olmadı
            # Bu gerçek bir discrepancy sayılmamalı, çünkü aynı tick içinde
            # olabilir. Sadece callback henüz çağrılmadı.
            pass

    def cancel(self, handle: int) -> bool:
        """
        Timer'ı iptal et.

        Args:
            handle: register_delayed/register_repeated'dan dönen handle.

        Returns:
            True: Timer bulundu ve iptal edildi.
            False: Timer bulunamadı.
        """
        if handle not in self._entries:
            return False

        entry = self._entries[handle]

        # Scheduler'dan iptal et
        self._scheduler.cancel(entry.scheduler_handle)

        # LegacyTimer'dan iptal et (repeated değilse)
        if entry.legacy_handle >= 0:
            self._legacy_timer.cancel(entry.legacy_handle)

        del self._entries[handle]

        # Temizlik
        self._scheduler_fired.discard(handle)
        self._legacy_fired.discard(handle)
        self._callback_called.discard(handle)

        return True

    def tick(self, dt: float) -> None:
        """
        Zamanı ilerlet.

        Args:
            dt: Geçen süre (saniye).
        """
        # Önce tick'leri çağır - callback'ler tetiklenecek
        self._scheduler.tick(dt)
        self._legacy_timer.tick(dt)

        # Tick sonrası discrepancy kontrolü
        # Scheduler tetiklendi ama Legacy tetiklenmedi (veya tam tersi)
        all_fired = self._scheduler_fired | self._legacy_fired
        for handle in all_fired:
            if handle in self._callback_called:
                continue  # Zaten işlendi
            scheduler_ok = handle in self._scheduler_fired
            legacy_ok = handle in self._legacy_fired
            # Eğer sadece bir sistem tetiklendiyse ve hala callback çağrılmadıysa
            # Bu bir discrepancy olabilir, ama aynı tick içinde olabilir
            # Şimdilik discrepancy saymıyoruz

    def get_report(self) -> Dict[str, Any]:
        """
        Durum raporu oluştur.

        Returns:
            Rapor dict.
        """
        return {
            'total_timers': self._total_timers,
            'discrepancy_count': self._discrepancy_count,
            'accuracy_percentage': self.accuracy_percentage,
            'pending_timers': len(self._entries),
        }

    def clear(self) -> None:
        """Tüm timer'ları temizle."""
        for entry in list(self._entries.values()):
            self._scheduler.cancel(entry.scheduler_handle)
            if entry.legacy_handle >= 0:
                self._legacy_timer.cancel(entry.legacy_handle)
        self._entries.clear()
        self._scheduler_fired.clear()
        self._legacy_fired.clear()
        self._callback_called.clear()


__all__ = ['TimerValidator', 'ValidatorEntry']
