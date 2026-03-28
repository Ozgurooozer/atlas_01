# AGENTS.md - Development Guide for AI Agents

This file provides essential information for AI agents working on this 2D game engine codebase.

---

## 1. Build, Lint, and Test Commands

### Running Tests
```bash
# Run all tests
pytest

# Run a single test file (most common)
pytest tests/core/test_guid.py -v

# Run a single test function
pytest tests/core/test_guid.py::TestGUID::test_creation -v

# Run tests matching a pattern
pytest -k "test_guid" -v

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run in headless mode (no GPU required)
pytest --headless
```

### Running the Application
```bash
python -m engine.run      # Run game engine
python -m editor.main     # Run editor
```

### Code Quality
```bash
ruff check .              # Run linter
ruff format .             # Format code
mypy src/                 # Type checking
pre-commit run --all-files # All checks
```

---

## 2. Project Structure

```
Layer 0: HAL         - Window, GPU, Filesystem, Clock (pyglet, moderngl)
Layer 1: CORE        - Object, Reflection, EventBus, Serializer (msgspec)
Layer 2: ENGINE      - Renderer, Physics (pymunk), Audio, Input, Asset
Layer 3: WORLD        - World, Level, Actor, Component, System, Prefab
Layer 4: GAME         - GameMode, Controller, Inventory, Quest, Save
Layer 5: SCRIPTING    - StateMachine, BehaviourTree, EventGraph
Layer 6: UI           - Widget, Canvas, Label, Button, Layout
Layer 7: EDITOR       - Viewport, Hierarchy, Properties (DearPyGui)
```

---

## 3. Import Rules (MANDATORY)

### Layer Dependency Rule
Files can ONLY import from their own layer or LOWER layers.

**CORRECT:** Layer 2 imports from Layer 1 or 0
**FORBIDDEN:** Layer 1 imports from Layer 2+

### Circular Import Prohibition
A → B → A  FORBIDDEN | A → B → C → A  FORBIDDEN

### Import Diversity Limit
Maximum 5 different modules per file.

### Star Import Prohibition
`from module import *`  STRICTLY FORBIDDEN

### Third-Party Library Locations
- pyglet, moderngl → hal/ (Layer 0)
- pymunk → engine/physics/ (Layer 2)
- Pillow → engine/asset/ (Layer 2)
- watchdog → engine/asset/ (Layer 2)
- msgspec → core/serializer.py (Layer 1)
- dearpygui → editor/ (Layer 7)

---

## 4. Dependency Rules

### Interface Dependency
Depend on interfaces, NOT concrete implementations.

**CORRECT:** `def __init__(self, renderer: IRenderer):`
**FORBIDDEN:** `def __init__(self, renderer: Renderer2D):`

### Dependency Injection Required
Global singletons FORBIDDEN (Engine excepted).

**FORBIDDEN:** `Engine.get().renderer.draw(...)`
**CORRECT:** `self._renderer.draw(...)` via `__init__`

---

## 5. Code Style Guidelines

- **Class Size:** Max 200 lines
- **Function Size:** Max 30 lines
- **Parameters:** Max 4 per function
- **Docstrings:** Required for all public functions

### Naming Conventions
- Classes: `PascalCase` (e.g., `GameEngine`)
- Functions: `snake_case` (e.g., `get_position`)
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`
- Interfaces: `I` prefix (e.g., `IRenderer`)

### Type Hints
All functions MUST have type hints:
```python
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
```

### Error Handling
- Use custom exception classes for domain-specific errors
- Never swallow exceptions without logging
- Handle expected errors with try/except at appropriate level
- Raise exceptions for unrecoverable errors, not return codes

---

## 6. Test Requirements

### Test-First Development
1. FIRST write test (RED)
2. THEN write implementation (GREEN)
3. FINALLY refactor

### Mock Prohibition
Mock usage FORBIDDEN. Use real test doubles (HeadlessWindow, HeadlessGPU).

---

## 7. Over-Engineering Prohibitions

- **YAGNI:** Don't write code not currently used
- **Premature Abstraction:** Don't create interface until 3 implementations exist
- **Factory Factory:** Max 1 level of factory pattern

---

## 8. Prohibited Patterns Summary

| PROHIBITED | DESCRIPTION |
|------------|-------------|
| `import *` | Star import |
| Upper layer import | Import from higher layer |
| Circular import | A→B→A |
| Global singleton | Engine.get() excepted |
| Mock | Use real test doubles |
| Dead code | Unused function/class |
| Magic number | Use constants |
| `type: ignore` | Hide mypy errors |

---

## 9. Development Workflow

1. Read `download/agent_state.json` to understand current state
2. Read relevant documentation (AGENT_RULES.md, ARCHITECTURE.md)
3. Write test file FIRST (will fail - RED)
4. Run test to confirm RED
5. Write implementation
6. Run test to confirm GREEN
7. Update `agent_state.json` with completed step
8. Proceed to next step

---

**VIOLATION = STOP AND FIX. DO NOT PROCEED.**
