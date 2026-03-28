"""
Tests for TimerValidator - İki timer sistemini karşılaştıran validator.

TimerValidator, LegacyTimer ve Scheduler sistemlerini paralel çalıştırarak
sonuçları karşılaştırır ve discrepancy (uyumsuzluk) tespit eder.

Layer: 1 (Core)
Dependencies: scheduler.py, legacy_timer.py

TDD Phase: RED - Bu testler implementation'dan ÖNCE yazıldı.
"""

import pytest


class TestTimerValidatorBasics:
    """TimerValidator temel özellik testleri."""

    def test_timer_validator_exists(self):
        """TimerValidator sınıfı olmalı."""
        from core.timer_validator import TimerValidator
        assert TimerValidator is not None

    def test_timer_validator_creation(self):
        """TimerValidator instance oluşturulabilmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert validator is not None

    def test_timer_validator_has_scheduler(self):
        """Scheduler property olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'scheduler')

    def test_timer_validator_has_legacy_timer(self):
        """legacy_timer property olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'legacy_timer')

    def test_timer_validator_has_register_delayed(self):
        """register_delayed metodu olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'register_delayed')
        assert callable(validator.register_delayed)

    def test_timer_validator_has_register_repeated(self):
        """register_repeated metodu olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'register_repeated')
        assert callable(validator.register_repeated)

    def test_timer_validator_has_tick(self):
        """tick metodu olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'tick')
        assert callable(validator.tick)


class TestTimerValidatorRegisterDelayed:
    """TimerValidator register_delayed testleri."""

    def test_register_delayed_returns_handle(self):
        """register_delayed bir handle döndürmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        handle = validator.register_delayed(1.0, lambda: None)
        assert handle is not None

    def test_register_delayed_fires_both_systems(self):
        """register_delayed her iki sistemde de tetiklenmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        scheduler_fired = []
        legacy_fired = []

        # Her iki sistemi de kontrol et
        validator.register_delayed(0.5, lambda: scheduler_fired.append(1))

        # Legacy timer'ı manuel kontrol et
        assert validator.legacy_timer.pending_count == 1
        assert validator.scheduler.pending_count == 1

    def test_register_delayed_callback_called_after_delay(self):
        """Callback gecikme sonrası çağrılmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        validator.register_delayed(0.5, lambda: fired.append(True))

        # Gecikme öncesi
        validator.tick(0.25)
        assert len(fired) == 0

        # Gecikme sonrası
        validator.tick(0.25)
        assert len(fired) == 1


class TestTimerValidatorRegisterRepeated:
    """TimerValidator register_repeated testleri."""

    def test_register_repeated_returns_handle(self):
        """register_repeated bir handle döndürmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        handle = validator.register_repeated(0.5, lambda: None)
        assert handle is not None

    def test_register_repeated_fires_multiple_times(self):
        """register_repeated birden fazla kez tetiklenmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        count = [0]

        validator.register_repeated(0.5, lambda: count.__setitem__(0, count[0] + 1))

        # İlk tetiklenme
        validator.tick(0.5)
        assert count[0] == 1

        # İkinci tetiklenme
        validator.tick(0.5)
        assert count[0] == 2

        # Üçüncü tetiklenme
        validator.tick(0.5)
        assert count[0] == 3


class TestTimerValidatorCancel:
    """TimerValidator cancel testleri."""

    def test_cancel_stops_callback(self):
        """İptal edilen timer tetiklenmemeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        handle = validator.register_delayed(0.5, lambda: fired.append(True))
        validator.cancel(handle)
        validator.tick(0.5)

        assert len(fired) == 0

    def test_cancel_returns_true_if_found(self):
        """İptal başarılıysa True dönmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        handle = validator.register_delayed(1.0, lambda: None)
        result = validator.cancel(handle)

        assert result is True


class TestTimerValidatorDiscrepancy:
    """TimerValidator discrepancy (uyumsuzluk) tespit testleri."""

    def test_discrepancy_count_zero_initially(self):
        """Başlangıçta discrepancy = 0 olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert validator.discrepancy_count == 0

    def test_discrepancy_count_zero_when_matching(self):
        """Eşleşen timer'larda discrepancy = 0 kalmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        validator.register_delayed(0.5, lambda: None)
        validator.tick(0.5)

        assert validator.discrepancy_count == 0

    def test_has_discrepancy_property(self):
        """has_discrepancy property olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'has_discrepancy')
        assert validator.has_discrepancy is False


class TestTimerValidatorReport:
    """TimerValidator raporlama testleri."""

    def test_get_report_returns_dict(self):
        """get_report dict dönmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        report = validator.get_report()
        assert isinstance(report, dict)

    def test_report_has_total_timers(self):
        """Rapor total_timers içermeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        report = validator.get_report()
        assert 'total_timers' in report

    def test_report_has_discrepancy_count(self):
        """Rapor discrepancy_count içermeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        report = validator.get_report()
        assert 'discrepancy_count' in report

    def test_accuracy_percentage(self):
        """accuracy_percentage property olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        assert hasattr(validator, 'accuracy_percentage')
        # Başlangıçta %100 olmalı
        assert validator.accuracy_percentage == 100.0


class TestTimerValidatorIntegration:
    """TimerValidator entegrasyon testleri."""

    def test_multiple_timers_no_discrepancy(self):
        """Birden fazla timer eşleşmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        results = []

        validator.register_delayed(0.1, lambda: results.append('a'))
        validator.register_delayed(0.2, lambda: results.append('b'))
        validator.register_delayed(0.3, lambda: results.append('c'))

        validator.tick(0.1)
        validator.tick(0.1)
        validator.tick(0.1)

        assert results == ['a', 'b', 'c']
        assert validator.discrepancy_count == 0

    def test_cancel_repeated_timer(self):
        """Tekrarlayan timer iptal edilebilmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        count = [0]

        handle = validator.register_repeated(0.1, lambda: count.__setitem__(0, count[0] + 1))

        validator.tick(0.1)
        validator.tick(0.1)
        assert count[0] == 2

        validator.cancel(handle)

        validator.tick(0.1)
        validator.tick(0.1)
        assert count[0] == 2  # Artmamalı
