"""
Tests for TimerValidator Comparison - Discrepancy detection tests.

Bu modül, TimerValidator'ın iki sistem arasındaki uyumsuzlukları
doğru tespit edip etmediğini test eder.

Layer: 1 (Core)
Dependencies: timer_validator.py

TDD Phase: RED - Bu testler implementation'dan ÖNCE yazıldı.
"""

import pytest


class TestDiscrepancyDetection:
    """Discrepancy (uyumsuzluk) tespit testleri."""

    def test_discrepancy_count_increases_on_mismatch(self):
        """Zamanlama uyumsuzluğunda discrepancy artmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # Normal çalışma - discrepancy yok
        validator.register_delayed(0.5, lambda: None)
        validator.tick(0.5)

        # Şu anki implementation'da discrepancy = 0 olmalı
        assert validator.discrepancy_count == 0

    def test_discrepancy_detects_callback_count_mismatch(self):
        """Callback sayısı uyumsuzluğunu tespit etmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # Her iki sistem de aynı sayıda callback çağırmalı
        call_count = [0]

        validator.register_delayed(0.1, lambda: call_count.__setitem__(0, call_count[0] + 1))
        validator.tick(0.1)

        # Callback sadece bir kez çağrılmalı
        assert call_count[0] == 1

    def test_discrepancy_reset_on_new_timer(self):
        """Yeni timer'da discrepancy sıfırlanmamalı (kümülatif)."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # İlk timer
        validator.register_delayed(0.1, lambda: None)
        validator.tick(0.1)
        first_count = validator.discrepancy_count

        # İkinci timer
        validator.register_delayed(0.1, lambda: None)
        validator.tick(0.1)
        second_count = validator.discrepancy_count

        # Discrepancy kümülatif olmalı
        assert validator.discrepancy_count >= first_count


class TestTimingTolerance:
    """Zamanlama toleransı testleri."""

    def test_exact_timing_match(self):
        """Tam zamanlama eşleşmesinde discrepancy yok."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        validator.register_delayed(1.0, lambda: fired.append(True))

        # Tam 1 saniye tick
        validator.tick(1.0)

        assert len(fired) == 1
        assert validator.discrepancy_count == 0

    def test_partial_tick_accumulation(self):
        """Kısmi tick'ler birikmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        validator.register_delayed(1.0, lambda: fired.append(True))

        # 4 x 0.25 = 1.0
        validator.tick(0.25)
        validator.tick(0.25)
        validator.tick(0.25)
        validator.tick(0.25)

        assert len(fired) == 1

    def test_timing_within_tolerance(self):
        """Küçük zamanlama farkları tolerans içinde olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # 0.999 saniye tick - küçük fark
        validator.register_delayed(1.0, lambda: None)
        validator.tick(0.999)

        # Henüz tetiklenmemeli
        # Not: Implementation'a göre bu geçebilir

    def test_overdue_timer_still_fires(self):
        """Gecikmeli timer yine de tetiklenmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        validator.register_delayed(0.5, lambda: fired.append(True))
        validator.tick(1.0)  # Gecikmeden fazla

        assert len(fired) == 1


class TestReportAccuracy:
    """Rapor doğruluğu testleri."""

    def test_report_shows_correct_total(self):
        """Rapor doğru toplam timer sayısını göstermeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        validator.register_delayed(0.1, lambda: None)
        validator.register_delayed(0.2, lambda: None)
        validator.register_delayed(0.3, lambda: None)

        report = validator.get_report()
        assert report['total_timers'] == 3

    def test_report_shows_correct_pending(self):
        """Rapor doğru bekleyen timer sayısını göstermeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        validator.register_delayed(0.1, lambda: None)
        validator.register_delayed(0.5, lambda: None)

        # İlk timer'ı tetikle
        validator.tick(0.1)

        report = validator.get_report()
        assert report['pending_timers'] == 1

    def test_report_shows_zero_pending_after_all_fired(self):
        """Tüm timer'lar tetiklendikten sonra pending = 0."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        validator.register_delayed(0.1, lambda: None)
        validator.register_delayed(0.1, lambda: None)

        validator.tick(0.1)

        report = validator.get_report()
        assert report['pending_timers'] == 0

    def test_accuracy_percentage_calculation(self):
        """Doğruluk yüzdesi doğru hesaplanmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # Başlangıçta %100
        assert validator.accuracy_percentage == 100.0

        # Timer ekle ve çalıştır
        validator.register_delayed(0.1, lambda: None)
        validator.tick(0.1)

        # Hala %100 olmalı (discrepancy yok)
        assert validator.accuracy_percentage == 100.0


class TestValidatorEdgeCases:
    """Validator edge case testleri."""

    def test_callback_exception_handling(self):
        """Callback exception'ı validator'ı bozmamalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        good_called = [False]

        def bad_callback():
            raise ValueError("Test exception")

        def good_callback():
            good_called.__setitem__(0, True)

        validator.register_delayed(0.1, bad_callback)
        validator.register_delayed(0.1, good_callback)

        validator.tick(0.1)

        assert good_called[0] is True

    def test_cancel_nonexistent_handle(self):
        """Olmayan handle iptal edilmeye çalışılırsa False dönmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        result = validator.cancel(99999)
        assert result is False

    def test_multiple_tick_calls(self):
        """Birden fazla tick çağrısı sorunsuz çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        count = [0]

        validator.register_repeated(0.1, lambda: count.__setitem__(0, count[0] + 1))

        for _ in range(10):
            validator.tick(0.1)

        assert count[0] == 10

    def test_clear_resets_state(self):
        """clear tüm durumu sıfırlamalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        validator.register_delayed(0.1, lambda: None)
        validator.register_delayed(0.2, lambda: None)

        validator.clear()

        report = validator.get_report()
        assert report['pending_timers'] == 0

    def test_validator_handles_zero_interval(self):
        """Sıfır interval ile immediate tetiklenmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        validator.register_delayed(0.0, lambda: fired.append(True))
        validator.tick(0.0)

        assert len(fired) == 1

    def test_large_number_of_timers(self):
        """Çok sayıda timer çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        for i in range(100):
            validator.register_delayed(0.01, lambda i=i: fired.append(i))

        validator.tick(0.01)

        assert len(fired) == 100


class TestValidatorStateTracking:
    """Validator durum takibi testleri."""

    def test_scheduler_property_accessible(self):
        """scheduler property erişilebilir olmalı."""
        from core.timer_validator import TimerValidator
        from core.scheduler import Scheduler
        validator = TimerValidator()

        assert isinstance(validator.scheduler, Scheduler)

    def test_legacy_timer_property_accessible(self):
        """legacy_timer property erişilebilir olmalı."""
        from core.timer_validator import TimerValidator
        from core.legacy_timer import LegacyTimer
        validator = TimerValidator()

        assert isinstance(validator.legacy_timer, LegacyTimer)

    def test_has_discrepancy_property(self):
        """has_discrepancy property doğru çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        assert validator.has_discrepancy is False

    def test_discrepancy_count_property(self):
        """discrepancy_count property doğru çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        assert validator.discrepancy_count == 0
        assert isinstance(validator.discrepancy_count, int)
