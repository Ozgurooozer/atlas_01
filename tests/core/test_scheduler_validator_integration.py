"""
Tests for Scheduler + Validator Integration.

Bu modül, Scheduler ve TimerValidator sistemlerinin birlikte
doğru çalışıp çalışmadığını test eder.

Layer: 1 (Core)
Dependencies: scheduler.py, timer_validator.py

TDD Phase: RED - Bu testler implementation'dan ÖNCE yazıldı.
"""

import pytest


class TestSchedulerValidatorIntegration:
    """Scheduler + TimerValidator entegrasyon testleri."""

    def test_scheduler_matches_legacy_single_timer(self):
        """Tek timer karşılaştırması başarılı olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        validator.register_delayed(0.5, lambda: fired.append(True))
        validator.tick(0.5)

        assert len(fired) == 1
        assert validator.discrepancy_count == 0

    def test_scheduler_matches_legacy_multiple_timers(self):
        """Birden fazla timer karşılaştırması başarılı olmalı."""
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

    def test_scheduler_matches_legacy_repeated_timer(self):
        """Tekrarlayan timer Scheduler ile çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        count = [0]

        validator.register_repeated(0.1, lambda: count.__setitem__(0, count[0] + 1))

        validator.tick(0.1)
        validator.tick(0.1)
        validator.tick(0.1)

        assert count[0] == 3

    def test_scheduler_matches_legacy_cancel(self):
        """İptal işlemi her iki sistemde de çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        handle = validator.register_delayed(0.5, lambda: fired.append(True))
        result = validator.cancel(handle)

        assert result is True
        validator.tick(0.5)
        assert len(fired) == 0


class TestEndToEndScenarios:
    """End-to-end senaryo testleri."""

    def test_game_loop_simulation(self):
        """Oyun döngüsü simülasyonu."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        events = []
        dt = 1/60  # 60 FPS

        # Spawn timer - her 2 saniyede
        validator.register_repeated(2.0, lambda: events.append('spawn'))

        # Delayed event - 3 saniye sonra
        validator.register_delayed(3.0, lambda: events.append('timeout'))

        # 3.1 saniye simüle et (186 frame) - floating point toleransı
        for _ in range(186):
            validator.tick(dt)

        # Spawn: 2.0 saniyede 1 kez tetiklenir
        # Timeout: 3.0 saniyede tetiklenir
        assert 'spawn' in events
        assert 'timeout' in events

    def test_multiple_delayed_timers_with_different_delays(self):
        """Farklı gecikmeli birden fazla timer."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        order = []
        validator.register_delayed(0.3, lambda: order.append(3))
        validator.register_delayed(0.1, lambda: order.append(1))
        validator.register_delayed(0.2, lambda: order.append(2))

        # 0.1'lik tick'ler
        validator.tick(0.1)  # 0.1 -> 1 tetiklenir
        validator.tick(0.1)  # 0.2 -> 2 tetiklenir
        validator.tick(0.1)  # 0.3 -> 3 tetiklenir

        assert order == [1, 2, 3]

    def test_timer_chain_reaction(self):
        """Timer zincirleme reaksiyonu."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        chain = []

        def create_chain_timer(step):
            chain.append(step)
            if step < 3:
                validator.register_delayed(0.1, lambda: create_chain_timer(step + 1))

        validator.register_delayed(0.1, lambda: create_chain_timer(1))

        validator.tick(0.1)  # step 1
        validator.tick(0.1)  # step 2
        validator.tick(0.1)  # step 3

        assert chain == [1, 2, 3]

    def test_parallel_timers_independent(self):
        """Paralel timer'lar bağımsız çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        timer_a = []
        timer_b = []

        validator.register_repeated(0.1, lambda: timer_a.append(1))
        validator.register_repeated(0.2, lambda: timer_b.append(2))

        validator.tick(0.1)  # a: 1, b: 0
        assert len(timer_a) == 1
        assert len(timer_b) == 0

        validator.tick(0.1)  # a: 2, b: 1
        assert len(timer_a) == 2
        assert len(timer_b) == 1

        validator.tick(0.2)  # a: 4, b: 2
        assert len(timer_a) == 4
        assert len(timer_b) == 2


class TestStressScenarios:
    """Stres testi senaryoları."""

    def test_100_timers_same_delay(self):
        """100 timer aynı gecikme ile."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        count = [0]

        for _ in range(100):
            validator.register_delayed(0.5, lambda: count.__setitem__(0, count[0] + 1))

        validator.tick(0.5)

        assert count[0] == 100

    def test_rapid_register_cancel(self):
        """Hızlı kayıt ve iptal."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        fired = []

        for i in range(10):
            handle = validator.register_delayed(0.1, lambda i=i: fired.append(i))
            if i % 2 == 0:
                validator.cancel(handle)

        validator.tick(0.1)

        # Sadece tek sayılı index'ler kalmış olmalı (0, 2, 4, 6, 8 iptal)
        assert len(fired) == 5

    def test_long_running_validation(self):
        """Uzun süreli validation."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        count = [0]

        validator.register_repeated(0.01, lambda: count.__setitem__(0, count[0] + 1))

        # 1000 tick = 10 saniye
        for _ in range(1000):
            validator.tick(0.01)

        assert count[0] == 1000
        assert validator.discrepancy_count == 0


class TestErrorRecovery:
    """Hata kurtarma testleri."""

    def test_callback_error_does_not_stop_others(self):
        """Callback hatası diğerlerini durdurmamalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        results = []

        def bad():
            raise RuntimeError("Test error")

        validator.register_delayed(0.1, bad)
        validator.register_delayed(0.1, lambda: results.append('good'))
        validator.register_delayed(0.1, lambda: results.append('good2'))

        validator.tick(0.1)

        assert results == ['good', 'good2']

    def test_cancel_during_callback_safe(self):
        """Callback sırasında iptal güvenli olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        handle_ref = [None]
        fired = []

        def callback():
            fired.append(1)
            if handle_ref[0]:
                validator.cancel(handle_ref[0])

        handle_ref[0] = validator.register_delayed(0.2, lambda: fired.append(2))
        validator.register_delayed(0.1, callback)

        validator.tick(0.1)  # callback çalışır, 0.2'yi iptal eder
        validator.tick(0.1)  # iptal edilen timer tetiklenmez

        assert fired == [1]  # 2 iptal edildi

    def test_clear_during_tick_safe(self):
        """Tick sırasında clear güvenli olmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        validator.register_delayed(0.1, lambda: validator.clear())
        validator.register_delayed(0.2, lambda: None)

        # Hata vermemeli
        validator.tick(0.1)
