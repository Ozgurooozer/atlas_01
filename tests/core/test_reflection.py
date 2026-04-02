"""
Reflection System Tests.

Tests for @reflect decorator and PropertyMeta system.
Reflection enables automatic property discovery for Editor and Serialization.
"""



class TestPropertyMeta:
    """Test PropertyMeta class."""

    def test_property_meta_creation(self):
        """PropertyMeta should be creatable."""
        from core.reflection import PropertyMeta
        meta = PropertyMeta(name="test", type_hint="float")
        assert meta is not None

    def test_property_meta_has_name(self):
        """PropertyMeta should have name."""
        from core.reflection import PropertyMeta
        meta = PropertyMeta(name="health", type_hint="float")
        assert meta.name == "health"

    def test_property_meta_has_type_hint(self):
        """PropertyMeta should have type_hint."""
        from core.reflection import PropertyMeta
        meta = PropertyMeta(name="health", type_hint="float")
        assert meta.type_hint == "float"

    def test_property_meta_has_default_value(self):
        """PropertyMeta can have default value."""
        from core.reflection import PropertyMeta
        meta = PropertyMeta(name="health", type_hint="float", default=100.0)
        assert meta.default == 100.0

    def test_property_meta_has_category(self):
        """PropertyMeta can have category."""
        from core.reflection import PropertyMeta
        meta = PropertyMeta(name="health", type_hint="float", category="Stats")
        assert meta.category == "Stats"

    def test_property_meta_has_min_max(self):
        """PropertyMeta can have min/max constraints."""
        from core.reflection import PropertyMeta
        meta = PropertyMeta(name="health", type_hint="float", min=0.0, max=100.0)
        assert meta.min == 0.0
        assert meta.max == 100.0


class TestReflectDecorator:
    """Test @reflect decorator."""

    def test_reflect_on_property(self):
        """@reflect can decorate a property."""
        from core.reflection import reflect, PropertyMeta

        class TestClass:
            def __init__(self):
                self._health = 100.0

            @reflect("float", min=0, max=100)
            def health(self) -> float:
                return self._health

        # Check property is decorated
        assert hasattr(TestClass.health, '_property_meta')
        meta = TestClass.health._property_meta
        assert isinstance(meta, PropertyMeta)
        assert meta.type_hint == "float"

    def test_reflect_sets_property_name(self):
        """@reflect should set property name automatically."""
        from core.reflection import reflect

        class TestClass:
            @reflect("float")
            def health(self) -> float:
                return 100.0

        meta = TestClass.health._property_meta
        assert meta.name == "health"

    def test_reflect_with_category(self):
        """@reflect can specify category."""
        from core.reflection import reflect

        class TestClass:
            @reflect("float", category="Stats")
            def health(self) -> float:
                return 100.0

        meta = TestClass.health._property_meta
        assert meta.category == "Stats"


class TestReflectionRegistry:
    """Test class reflection discovery."""

    def test_get_properties_returns_list(self):
        """get_properties should return list of PropertyMeta."""
        from core.reflection import reflect, get_properties

        class TestClass:
            @reflect("float")
            def health(self) -> float:
                return 100.0

        props = get_properties(TestClass)
        assert isinstance(props, list)

    def test_get_properties(self):
        """get_properties should return all reflected properties."""
        from core.reflection import reflect, get_properties

        class TestClass:
            @reflect("float")
            def health(self) -> float:
                return 100.0

            @reflect("str")
            def name(self) -> str:
                return "Test"

        props = get_properties(TestClass)
        assert len(props) == 2
        names = [p.name for p in props]
        assert "health" in names
        assert "name" in names

    def test_instance_get_property_value(self):
        """get_property_value should return actual value."""
        from core.reflection import reflect, get_property_value

        class TestClass:
            def __init__(self):
                self._health = 75.0

            @reflect("float")
            def health(self) -> float:
                return self._health

        obj = TestClass()
        value = get_property_value(obj, "health")
        assert value == 75.0

    def test_instance_set_property_value(self):
        """set_property_value should set actual value via setter."""
        from core.reflection import reflect, set_property_value

        class TestClass:
            def __init__(self):
                self._health = 100.0

            @reflect("float")
            def health(self) -> float:
                return self._health

            @health.setter
            def health(self, value: float):
                self._health = value

        obj = TestClass()
        set_property_value(obj, "health", 50.0)
        assert obj.health == 50.0
