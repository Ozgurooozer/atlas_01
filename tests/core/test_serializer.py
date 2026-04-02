"""
Serializer System Tests.

Tests for JSON serialization system using reflection.
Serializer works with Object and reflected properties.
"""



class TestSerializer:
    """Test Serializer class."""

    def test_serializer_creation(self):
        """Serializer should be creatable."""
        from core.serializer import Serializer
        ser = Serializer()
        assert ser is not None

    def test_serialize_dict(self):
        """Should serialize simple dict."""
        from core.serializer import Serializer
        ser = Serializer()
        data = {"name": "test", "value": 42}
        result = ser.serialize(data)
        assert isinstance(result, str)
        assert "name" in result
        assert "test" in result

    def test_deserialize_dict(self):
        """Should deserialize to dict."""
        from core.serializer import Serializer
        ser = Serializer()
        original = {"name": "test", "value": 42}
        json_str = ser.serialize(original)
        result = ser.deserialize(json_str)
        assert result == original


class TestObjectSerialization:
    """Test Object serialization with reflection."""

    def test_serialize_object_with_reflected_properties(self):
        """Should serialize Object with reflected properties."""
        from core.object import Object
        from core.serializer import serialize_object
        from core.reflection import reflect

        class TestObject(Object):
            def __init__(self, name=None):
                super().__init__(name=name)
                self._health = 100.0
                self._entity_name = "TestEntity"

            @reflect("float", min=0, max=100)
            def health(self) -> float:
                return self._health

            @health.setter
            def health(self, value: float):
                self._health = value

            @reflect("str")
            def entity_name(self) -> str:
                return self._entity_name

            @entity_name.setter
            def entity_name(self, value: str):
                self._entity_name = value

        obj = TestObject(name="MyEntity")
        data = serialize_object(obj)

        assert "guid" in data
        assert "name" in data
        assert "properties" in data
        assert data["properties"]["health"] == 100.0
        assert data["properties"]["entity_name"] == "TestEntity"

    def test_deserialize_object_with_reflected_properties(self):
        """Should deserialize Object with reflected properties."""
        from core.object import Object
        from core.serializer import serialize_object, deserialize_object
        from core.reflection import reflect

        class TestObject(Object):
            def __init__(self, name=None):
                super().__init__(name=name)
                self._health = 0.0
                self._entity_name = ""

            @reflect("float")
            def health(self) -> float:
                return self._health

            @health.setter
            def health(self, value: float):
                self._health = value

            @reflect("str")
            def entity_name(self) -> str:
                return self._entity_name

            @entity_name.setter
            def entity_name(self, value: str):
                self._entity_name = value

        # Create and serialize
        obj1 = TestObject(name="Original")
        obj1.health = 75.0
        obj1.entity_name = "TestEntity"
        data = serialize_object(obj1)

        # Deserialize into new object
        obj2 = TestObject()
        deserialize_object(obj2, data)

        assert obj2.health == 75.0
        assert obj2.entity_name == "TestEntity"
        assert obj2.name == "Original"


class TestJSONFileIO:
    """Test JSON file read/write."""

    def test_write_json_file(self):
        """Should write JSON to file."""
        from core.serializer import write_json
        from hal.headless import MemoryFilesystem

        fs = MemoryFilesystem()
        data = {"test": "value", "number": 123}
        write_json(fs, "test.json", data)

        assert fs.file_exists("test.json")

    def test_read_json_file(self):
        """Should read JSON from file."""
        from core.serializer import write_json, read_json
        from hal.headless import MemoryFilesystem

        fs = MemoryFilesystem()
        original = {"test": "value", "number": 123}
        write_json(fs, "test.json", original)

        result = read_json(fs, "test.json")
        assert result == original
