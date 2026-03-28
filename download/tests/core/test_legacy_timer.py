"""
Tests for LegacyTimer - Eski manuel timer sisteminin wrapper'ı.

LegacyTimer, mevcut Shooter demo'sundaki manuel timer mantığını 
kapsülleyerek TimerValidator ile karşılaştırma yapmayı sağlar.

Layer: 1 (Core)
Dependencies: None (stdlib only)

TDD Phase: RED - Bu testler implementation'dan ÖNCE yazıldı.
"""

import pytest


class TestLegacyTimerBasics:
    """LegacyTimer temel özellik testleri."""

    def test_legacy_timer_exists(self):
        """LegacyTimer sınıfı olmalı."""
        from core.legacy_timer import LegacyTimer
        assert LegacyTimer is not None

    def test_legacy_timer_creation(self):
        """LegacyTimer instance oluşturulabilmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        assert timer is not None

    def test_legacy_timer_has_add_timer(self):
        """add_timer metodu olmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        assert hasattr(timer, 'add_timer')
        assert callable(timer.add_timer)

    def test_legacy_timer_has_tick(self):
        """tick metodu olmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        assert hasattr(timer, 'tick')
        assert callable(timer.tick)

    def test_legacy_timer_has_cancel(self):
        """cancel metodu olmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        assert hasattr(timer, 'cancel')
        assert callable(timer.cancel)

    def test_legacy_timer_has_pending_count(self):
        """pending_count property olmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        assert hasattr(timer, 'pending_count')


class TestLegacyTimerAddTimer:
    """LegacyTimer add_timer testleri."""

    def test_add_timer_returns_handle(self):
        """add_timer bir handle (int) döndürmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        handle = timer.add_timer(1.0, lambda: None)
        assert isinstance(handle, int)

    def test_add_timer_increases_pending_count(self):
        """Timer eklenince pending_count artmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        
        assert timer.pending_count == 0
        
        timer.add_timer(1.0, lambda: None)
        assert timer.pending_count == 1
        
        timer.add_timer(2.0, lambda: None)
        assert timer.pending_count == 2

    def test_add_timer_handles_unique(self):
        """Her timer unique handle almalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        
        handle1 = timer.add_timer(1.0, lambda: None)
        handle2 = timer.add_timer(2.0, lambda: None)
        handle3 = timer.add_timer(3.0, lambda: None)
        
        assert handle1 != handle2
        assert handle2 != handle3
        assert handle1 != handle3


class TestLegacyTimerTick:
    """LegacyTimer tick testleri."""

    def test_tick_fires_callback_after_delay(self):
        """Timer gecikme sonrası callback'i tetiklemeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        timer.add_timer(0.5, lambda: fired.append(True))

        # Gecikme öncesi
        timer.tick(0.25)
        assert len(fired) == 0

        # Gecikme sonrası
        timer.tick(0.25)
        assert len(fired) == 1

    def test_tick_fires_only_once(self):
        """Timer sadece bir kez tetiklenmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        count = [0]

        timer.add_timer(0.5, lambda: count.__setitem__(0, count[0] + 1))

        # İlk tetiklenme
        timer.tick(0.5)
        assert count[0] == 1

        # Tekrar tick - tekrar tetiklenmemeli
        timer.tick(0.5)
        timer.tick(0.5)
        assert count[0] == 1

    def test_tick_removes_fired_timer(self):
        """Tetiklenen timer pending'den kaldırılmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()

        timer.add_timer(0.5, lambda: None)

        assert timer.pending_count == 1

        timer.tick(0.5)

        assert timer.pending_count == 0

    def test_tick_with_zero_delay(self):
        """Sıfır gecikme hemen tetiklenmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        timer.add_timer(0.0, lambda: fired.append(True))
        timer.tick(0.0)

        assert len(fired) == 1

    def test_tick_with_negative_delay(self):
        """Negatif gecikme hemen tetiklenmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        timer.add_timer(-1.0, lambda: fired.append(True))
        timer.tick(0.0)

        assert len(fired) == 1

    def test_tick_multiple_timers(self):
        """Birden fazla timer doğru sırada tetiklenmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        order = []

        timer.add_timer(1.0, lambda: order.append('c'))
        timer.add_timer(0.5, lambda: order.append('b'))
        timer.add_timer(0.25, lambda: order.append('a'))

        timer.tick(0.25)
        assert order == ['a']

        timer.tick(0.25)
        assert order == ['a', 'b']

        timer.tick(0.5)
        assert order == ['a', 'b', 'c']


class TestLegacyTimerCancel:
    """LegacyTimer cancel testleri."""

    def test_cancel_prevents_callback(self):
        """İptal edilen timer tetiklenmemeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        handle = timer.add_timer(0.5, lambda: fired.append(True))
        timer.cancel(handle)
        timer.tick(0.5)

        assert len(fired) == 0

    def test_cancel_returns_true_if_found(self):
        """İptal başarılıysa True dönmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()

        handle = timer.add_timer(1.0, lambda: None)
        result = timer.cancel(handle)

        assert result is True

    def test_cancel_returns_false_if_not_found(self):
        """Timer bulunamazsa False dönmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()

        result = timer.cancel(999)

        assert result is False

    def test_cancel_decreases_pending_count(self):
        """İptal sonrası pending_count azalmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()

        handle = timer.add_timer(1.0, lambda: None)
        assert timer.pending_count == 1

        timer.cancel(handle)
        assert timer.pending_count == 0

    def test_cancel_already_fired_timer(self):
        """Zaten tetiklenmiş timer iptal edilemez."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()

        handle = timer.add_timer(0.1, lambda: None)
        timer.tick(0.1)

        result = timer.cancel(handle)
        assert result is False


class TestLegacyTimerClear:
    """LegacyTimer clear testleri."""

    def test_clear_removes_all_timers(self):
        """clear tüm timer'ları kaldırmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()

        timer.add_timer(1.0, lambda: None)
        timer.add_timer(2.0, lambda: None)
        timer.add_timer(3.0, lambda: None)

        assert timer.pending_count == 3

        timer.clear()

        assert timer.pending_count == 0

    def test_clear_prevents_all_callbacks(self):
        """clear sonrası hiçbir callback tetiklenmemeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        timer.add_timer(0.1, lambda: fired.append(1))
        timer.add_timer(0.2, lambda: fired.append(2))

        timer.clear()
        timer.tick(0.3)

        assert len(fired) == 0


class TestLegacyTimerEdge:
    """LegacyTimer edge case testleri."""

    def test_tick_with_zero_dt(self):
        """tick(0.0) sorun çıkarmamalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        count = [0]

        timer.add_timer(0.1, lambda: count.__setitem__(0, count[0] + 1))
        timer.tick(0.0)
        timer.tick(0.0)

        assert count[0] == 0

    def test_callback_exception_does_not_crash(self):
        """Callback exception'ı scheduler'ı çökertmemeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        count = [0]

        def bad_callback():
            raise ValueError("Test exception")

        def good_callback():
            count.__setitem__(0, count[0] + 1)

        timer.add_timer(0.1, bad_callback)
        timer.add_timer(0.1, good_callback)

        # Exception olsa bile good_callback çalışmalı
        timer.tick(0.1)

        assert count[0] == 1

    def test_callback_can_add_new_timer(self):
        """Callback içinde yeni timer eklenebilmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        order = []

        def add_another():
            order.append(1)
            timer.add_timer(0.1, lambda: order.append(2))

        timer.add_timer(0.1, add_another)

        timer.tick(0.1)
        assert order == [1]

        timer.tick(0.1)
        assert order == [1, 2]

    def test_large_delay(self):
        """Büyük gecikme değerleri çalışmalı."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        timer.add_timer(1000.0, lambda: fired.append(True))

        for _ in range(999):
            timer.tick(1.0)
        assert len(fired) == 0

        timer.tick(1.0)
        assert len(fired) == 1

    def test_multiple_ticks_accumulate(self):
        """Birden fazla tick zamanı birikmeli."""
        from core.legacy_timer import LegacyTimer
        timer = LegacyTimer()
        fired = []

        timer.add_timer(1.0, lambda: fired.append(True))

        # Floating point hassasiyeti için 0.11 kullan
        # 9 x 0.11 = 0.99, 10. tick'te 1.0'ı geçer
        for _ in range(9):
            timer.tick(0.11)

        assert len(fired) == 0  # Henüz tetiklenmemeli

        timer.tick(0.11)
        assert len(fired) == 1  # Şimdi tetiklendi
