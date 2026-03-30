"""
Serializer - msgspec Serialization System.

Provides fast serialization using msgspec instead of stdlib json.
Works with reflected properties to automatically serialize/deserialize.

Layer: 1 (Core)
Dependencies: core.reflection, core.object, msgspec
"""

from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING

import msgspec

if TYPE_CHECKING:
    from core.object import Object
    from hal.interfaces import IFilesystem


class Serializer:
    """
    msgspec serializer with support for Object serialization.

    Can serialize:
    - Basic types (str, int, float, bool, None)
    - Lists and dicts
    - Object instances with reflected properties
    
    Uses msgspec for fast JSON encoding/decoding.
    """
    
    def __init__(self):
        """Initialize serializer with msgspec encoder/decoder."""
        self._encoder = msgspec.json.Encoder()
        self._decoder = msgspec.json.Decoder()

    def serialize(self, data: Any) -> str:
        """
        Serialize data to JSON string.

        Args:
            data: Data to serialize

        Returns:
            JSON string
        """
        return self._encoder.encode(data).decode("utf-8")

    def deserialize(self, json_str: str) -> Any:
        """
        Deserialize JSON string to Python object.

        Args:
            json_str: JSON string

        Returns:
            Deserialized data
        """
        return self._decoder.decode(json_str)


def serialize_object(obj: "Object") -> Dict[str, Any]:
    """
    Serialize an Object instance to a dictionary.

    Uses reflection to discover and serialize all reflected properties.

    Args:
        obj: Object instance to serialize

    Returns:
        Dictionary containing object data
    """
    from core.reflection import get_properties, get_property_value

    # Get base object serialization
    data = obj.serialize()

    # Add reflected properties
    properties = get_properties(obj)
    if properties:
        data["properties"] = {}
        for prop in properties:
            try:
                value = get_property_value(obj, prop.name)
                data["properties"][prop.name] = value
            except Exception:
                # Skip properties that can't be read
                pass

    return data


def deserialize_object(obj: "Object", data: Dict[str, Any]) -> None:
    """
    Deserialize a dictionary into an Object instance.

    Uses reflection to set reflected properties.

    Args:
        obj: Object instance to deserialize into
        data: Dictionary containing object data
    """
    from core.reflection import set_property_value

    # First deserialize base Object properties
    obj.deserialize(data)

    # Then set reflected properties
    if "properties" in data:
        for prop_name, value in data["properties"].items():
            try:
                set_property_value(obj, prop_name, value)
            except Exception:
                # Skip properties that can't be set
                pass


def write_json(filesystem: "IFilesystem", path: str, data: Dict[str, Any]) -> None:
    """
    Write data to a JSON file.

    Args:
        filesystem: Filesystem to write to
        path: File path
        data: Data to write
    """
    serializer = Serializer()
    json_str = serializer.serialize(data)
    filesystem.write_file(path, json_str.encode("utf-8"))


def read_json(filesystem: "IFilesystem", path: str) -> Dict[str, Any]:
    """
    Read data from a JSON file.

    Args:
        filesystem: Filesystem to read from
        path: File path

    Returns:
        Deserialized data
    """
    serializer = Serializer()
    json_bytes = filesystem.read_file(path)
    json_str = json_bytes.decode("utf-8")
    return serializer.deserialize(json_str)
