"""
GUID System Tests.

Tests for Global Unique Identifier system.
GUIDs are used to uniquely identify every object in the engine.
"""



class TestGUID:
    """Test GUID class."""

    def test_guid_creation(self):
        """GUID should be creatable."""
        from core.guid import GUID
        guid = GUID()
        assert guid is not None

    def test_guid_has_value(self):
        """GUID should have a string value."""
        from core.guid import GUID
        guid = GUID()
        assert str(guid) is not None
        assert len(str(guid)) > 0

    def test_guid_unique(self):
        """Each GUID should be unique."""
        from core.guid import GUID
        guid1 = GUID()
        guid2 = GUID()
        assert guid1 != guid2

    def test_guid_from_string(self):
        """GUID can be created from existing string."""
        from core.guid import GUID
        original = "test-guid-123"
        guid = GUID(original)
        assert str(guid) == original

    def test_guid_equality(self):
        """GUIDs with same value should be equal."""
        from core.guid import GUID
        value = "same-guid-value"
        guid1 = GUID(value)
        guid2 = GUID(value)
        assert guid1 == guid2

    def test_guid_inequality(self):
        """GUIDs with different values should not be equal."""
        from core.guid import GUID
        guid1 = GUID("value-1")
        guid2 = GUID("value-2")
        assert guid1 != guid2

    def test_guid_hash(self):
        """GUID should be hashable for use in sets/dicts."""
        from core.guid import GUID
        guid1 = GUID("hashable-1")
        guid2 = GUID("hashable-2")
        guid_set = {guid1, guid2}
        assert len(guid_set) == 2
        assert guid1 in guid_set

    def test_guid_hash_consistency(self):
        """Same GUID value should have same hash."""
        from core.guid import GUID
        value = "same-value"
        guid1 = GUID(value)
        guid2 = GUID(value)
        assert hash(guid1) == hash(guid2)

    def test_guid_repr(self):
        """GUID should have useful repr."""
        from core.guid import GUID
        guid = GUID("test-repr")
        repr_str = repr(guid)
        assert "GUID" in repr_str
        assert "test-repr" in repr_str

    def test_guid_default_format_is_uuid(self):
        """Default GUID should be UUID format (36 chars with dashes)."""
        from core.guid import GUID
        guid = GUID()
        value = str(guid)
        # UUID format: 8-4-4-4-12 = 36 characters
        assert len(value) == 36
        assert value.count("-") == 4
