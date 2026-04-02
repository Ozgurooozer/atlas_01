"""
Input Buffer Tests.

Frame-based input buffer for responsive combat feel.
Layer 4 (Game/Input), depends on core.object.

TDD: RED phase — implementation does not exist yet.
"""
from __future__ import annotations


class FakeInputType:
    ATTACK = "attack"
    DASH = "dash"
    JUMP = "jump"
    SPECIAL = "special"


class TestInputBufferBasics:
    """Core InputBuffer behavior."""

    def test_create_buffer_default_capacity(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        assert buf.max_size == 4
        assert buf.is_empty

    def test_create_buffer_custom_capacity(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=8)
        assert buf.max_size == 8

    def test_push_single_input(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        assert not buf.is_empty
        assert buf.count == 1

    def test_push_multiple_inputs(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        buf.push(FakeInputType.JUMP, timestamp=0.032)
        assert buf.count == 3

    def test_buffer_evicts_oldest_when_full(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=3)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        buf.push(FakeInputType.JUMP, timestamp=0.032)
        buf.push(FakeInputType.SPECIAL, timestamp=0.048)
        assert buf.count == 3
        oldest = buf.consume(FakeInputType.ATTACK)
        assert oldest is None

    def test_clear_empties_buffer(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        buf.clear()
        assert buf.is_empty
        assert buf.count == 0


class TestInputBufferConsume:
    """Consume semantics: FIFO within matching type."""

    def test_consume_matching_type(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        buf.push(FakeInputType.ATTACK, timestamp=0.032)
        result = buf.consume(FakeInputType.ATTACK)
        assert result is not None
        assert result[0] == FakeInputType.ATTACK
        assert result[1] == 0.0
        assert buf.count == 2

    def test_consume_returns_oldest_matching(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.ATTACK, timestamp=0.032)
        buf.push(FakeInputType.ATTACK, timestamp=0.064)
        first = buf.consume(FakeInputType.ATTACK)
        assert first[1] == 0.0
        second = buf.consume(FakeInputType.ATTACK)
        assert second[1] == 0.032

    def test_consume_nonexistent_type_returns_none(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        result = buf.consume(FakeInputType.DASH)
        assert result is None

    def test_consume_empty_buffer_returns_none(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        result = buf.consume(FakeInputType.ATTACK)
        assert result is None

    def test_consume_all_of_type(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=6)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        buf.push(FakeInputType.ATTACK, timestamp=0.032)
        r1 = buf.consume(FakeInputType.ATTACK)
        r2 = buf.consume(FakeInputType.ATTACK)
        r3 = buf.consume(FakeInputType.ATTACK)
        assert r1 is not None
        assert r2 is not None
        assert r3 is None


class TestInputBufferPeek:
    """Peek without consuming."""

    def test_peek_returns_without_removing(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        result = buf.peek(FakeInputType.ATTACK)
        assert result is not None
        assert result[0] == FakeInputType.ATTACK
        assert buf.count == 1

    def test_peek_nonexistent_returns_none(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        result = buf.peek(FakeInputType.DASH)
        assert result is None


class TestInputBufferTimeout:
    """Old inputs get evicted after timeout."""

    def test_tick_removes_expired_inputs(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4, timeout=0.2)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.tick(current_time=0.25)
        assert buf.is_empty

    def test_tick_keeps_fresh_inputs(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4, timeout=0.2)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.tick(current_time=0.1)
        assert buf.count == 1

    def test_tick_selective_removal(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=6, timeout=0.2)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.15)
        buf.push(FakeInputType.JUMP, timestamp=0.25)
        buf.tick(current_time=0.3)
        assert buf.count == 2
        assert buf.consume(FakeInputType.ATTACK) is None


class TestInputBufferTimestamp:
    """Timestamp tracking."""

    def test_auto_timestamp(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK)
        assert buf.count == 1
        result = buf.consume(FakeInputType.ATTACK)
        assert result is not None
        assert result[1] > 0.0

    def test_manual_timestamp(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=1.5)
        result = buf.consume(FakeInputType.ATTACK)
        assert result[1] == 1.5

    def test_fifo_order_preserved(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=6)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.1)
        buf.push(FakeInputType.JUMP, timestamp=0.2)
        buf.push(FakeInputType.SPECIAL, timestamp=0.3)
        r1 = buf.consume(FakeInputType.ATTACK)
        r2 = buf.consume(FakeInputType.DASH)
        assert r1[1] == 0.0
        assert r2[1] == 0.1


class TestInputBufferSerialize:
    """Serialization support."""

    def test_serialize_empty(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        data = buf.serialize()
        assert "max_size" in data
        assert "entries" in data
        assert len(data["entries"]) == 0

    def test_serialize_with_data(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.1)
        data = buf.serialize()
        assert len(data["entries"]) == 2

    def test_deserialize(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        data = buf.serialize()
        buf2 = InputBuffer(max_size=4)
        buf2.deserialize(data)
        assert buf2.count == 1
        result = buf2.consume(FakeInputType.ATTACK)
        assert result is not None


class TestInputBufferEdgeCases:
    """Edge cases and stress tests."""

    def test_push_same_type_multiple_times(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=8)
        for i in range(8):
            buf.push(FakeInputType.ATTACK, timestamp=float(i) * 0.016)
        assert buf.count == 8
        consumed = 0
        while buf.consume(FakeInputType.ATTACK) is not None:
            consumed += 1
        assert consumed == 8

    def test_consume_during_iteration(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=6)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        buf.push(FakeInputType.ATTACK, timestamp=0.032)
        all_types = [FakeInputType.ATTACK, FakeInputType.DASH, FakeInputType.ATTACK]
        for expected in all_types:
            result = buf.consume(expected)
            assert result is not None, f"Expected {expected} but got None"

    def test_has_method(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=4)
        assert not buf.has(FakeInputType.ATTACK)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        assert buf.has(FakeInputType.ATTACK)
        buf.consume(FakeInputType.ATTACK)
        assert not buf.has(FakeInputType.ATTACK)

    def test_max_size_boundary(self):
        from game.input.input_buffer import InputBuffer
        buf = InputBuffer(max_size=1)
        buf.push(FakeInputType.ATTACK, timestamp=0.0)
        buf.push(FakeInputType.DASH, timestamp=0.016)
        assert buf.count == 1
        assert buf.consume(FakeInputType.DASH) is not None
        assert buf.consume(FakeInputType.ATTACK) is None
