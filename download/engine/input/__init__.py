"""
Input Subsystem.

Provides keyboard and mouse input handling.

Layer: 2 (Engine)
Dependencies: engine.subsystem
"""

from engine.input.input_handler import IInput, InputHandler

__all__ = [
    "IInput",
    "InputHandler",
]
