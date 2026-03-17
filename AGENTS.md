# AGENTS.md - madOS Equalizer Development Guide

This document provides guidelines for agentic coding agents working on the madOS Audio Equalizer codebase.

## Project Overview

madOS Equalizer is a GTK3 application providing an 8-band parametric audio equalizer with PipeWire/PulseAudio backend integration. The application features:
- 8-band EQ (60Hz, 170Hz, 310Hz, 600Hz, 1kHz, 3kHz, 6kHz, 12kHz)
- PipeWire filter-chain with PulseAudio fallback
- 10 built-in presets + custom user presets
- Nord theme styling
- 6-language i18n support
- Master volume control

## Running the Application

```bash
python3 -m mados_equalizer
```

Or directly:
```bash
python3 __main__.py
```

## Build/Lint/Test Commands

This project does **not** have a formal build system (pyproject.toml/setup.py). It runs as a standalone Python module.

### Running the Application

```bash
python3 -m mados_equalizer
```

### Code Quality Tools

Since there are no configured linting/formatting tools, ensure code follows these manual guidelines.

### Running a Single Test

**No test framework is currently configured.** If tests are added in the future:

```bash
pytest tests/test_file.py::test_function_name -v
```

To run all tests:
```bash
pytest
```

## Code Style Guidelines

### Imports

Organize imports in the following order with blank lines between groups:

```python
# Standard library imports
import os
import json
import threading
from pathlib import Path
from contextlib import contextmanager

# Third-party imports (alphabetical)
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango
import cairo

# Local/application imports (absolute imports from package)
from . import __app_id__, __app_name__, __version__
from .backend import AudioBackend
from .database import EqualizerStateDB
```

- Always use absolute imports within the package (`from .module import ...`)
- Use `gi.require_version()` before importing GTK modules

### Formatting

- **Line length**: Maximum 100 characters (soft limit at 120)
- **Indentation**: 4 spaces (no tabs)
- **Blank lines**: Two between top-level definitions, one between method definitions
- **Spaces**: Around operators (`x = 1`), after commas in arguments (`func(a, b)`), but not before

### Types

This codebase uses **duck typing** for GTK objects. Type hints are optional but welcome for new code:

```python
# Preferred for new code
def apply_eq(self, gains: list[float] | None = None) -> tuple[bool, str]:
    pass

# Legacy style (acceptable)
def get_volume(self):
    """Get the current master volume level.
    
    Returns:
        Tuple of (volume: float, muted: bool).
    """
```

### Naming Conventions

| Element | Convention | Example |
|---------|-------------|---------|
| Modules | snake_case | `audio_backend.py` |
| Classes | PascalCase | `EqualizerApp` |
| Functions/methods | snake_case | `_build_ui()` |
| Constants | UPPER_SNAKE_CASE | `GAIN_MIN = -12.0` |
| Private methods | Leading underscore | `_on_destroy()` |
| Instance variables | snake_case | `self.enabled` |

### Docstrings

Use **Google-style docstrings** with `Args:` and `Returns:` sections:

```python
def apply_eq_async(self, gains=None, callback=None):
    """Apply equalizer settings asynchronously in a background thread.

    Args:
        gains: Optional list of 8 gain values in dB.
        callback: Optional callable(success, message) to invoke when done.
                  Will be called from the background thread.
    """
```

- Always document public methods and classes
- Private methods (starting with `_`) should have brief docstrings explaining purpose

### Error Handling

Follow these patterns:

```python
# 1. Return error tuples for operations that can fail
def enable_eq(self) -> tuple[bool, str]:
    self.enabled = True
    return self.apply_eq()

# 2. Use try/except for external commands with fallbacks
try:
    result = subprocess.run(args, capture_output=True, timeout=5)
    return result.returncode, result.stdout, result.stderr
except subprocess.TimeoutExpired:
    return -1, "", "Command timed out"
except FileNotFoundError:
    return -1, "", f"Command not found: {args[0]}"

# 3. Silent failures with logging for non-critical operations
try:
    EQ_CONFIG_FILE.unlink()
except OSError:
    pass  # Ignore if file doesn't exist
```

- Return `(success: bool, message: str)` tuples from public methods
- Catch specific exceptions rather than bare `except:`
- Use `print()` for errors in backend (GTK logging is not available in backend module)

### Threading

When performing blocking operations that update the UI:

```python
# Use threading.Thread with daemon=True for background work
threading.Thread(
    target=self.backend.set_volume,
    args=(volume_float,),
    daemon=True,
).start()

# Use GLib.idle_add() to update UI from background threads
def _detect():
    device_name = self.backend.refresh_output_device()
    GLib.idle_add(self._update_device_label, device_name)

threading.Thread(target=_detect, daemon=True).start()
```

- Always use `daemon=True` for background threads
- Use `GLib.idle_add()` callback to update GTK widgets from other threads

### Database Patterns

The codebase uses SQLite with WAL mode. Always use the transaction context manager:

```python
@contextmanager
def _transaction(self):
    try:
        yield self._conn
        self._conn.commit()
    except Exception:
        self._conn.rollback()
        raise
```

### GTK3 Patterns

- Always call `gi.require_version("Gtk", "3.0")` before importing GTK
- Use `show_all()` after adding all widgets
- Connect signals with `connect("signal-name", handler)`
- Use CSS provider for theming (see `theme.py`)
- Set `app_id` and role on window for compositor integration

### File Organization

```
mados-equalizer/
├── __init__.py      # Package metadata (__version__, __app_id__)
├── __main__.py      # Entry point (python -m mados_equalizer)
├── app.py           # Main GTK3 application window
├── backend.py       # PipeWire/PulseAudio integration
├── database.py      # SQLite state persistence
├── presets.py       # Built-in and custom presets
├── translations.py  # i18n strings and utilities
├── theme.py         # Nord theme CSS
```

### Adding New Features

1. **Presets**: Add to `BUILTIN_PRESETS` dict and `BUILTIN_PRESET_ORDER` list in `presets.py`
2. **Translations**: Add key to all language dicts in `translations.py`
3. **Frequency bands**: Update `FREQUENCY_BANDS`, `BAND_LABELS`, and `BAND_KEYS` in `presets.py`
4. **Gain range**: Modify `GAIN_MIN`, `GAIN_MAX` in `presets.py`

### Common Patterns to Maintain

1. **Debouncing slider changes**:
```python
# Cancel any pending debounced apply
if self._eq_apply_timeout_id is not None:
    GLib.source_remove(self._eq_apply_timeout_id)
# Schedule a new apply after 150 ms
self._eq_apply_timeout_id = GLib.timeout_add(150, self._apply_eq_debounced)
```

2. **Atomic file writes**:
```python
tmp_file = EQ_CONFIG_FILE.with_suffix(".tmp")
with open(tmp_file, "w") as f:
    f.write(config_content)
tmp_file.rename(EQ_CONFIG_FILE)
```

3. **Updating UI state with flags**:
```python
self._updating_sliders = True
for i, gain in enumerate(gains):
    self.band_scales[i].set_value(float(gain))
self._updating_sliders = False
```

## Architecture Notes

- **Backend**: Handles PipeWire filter-chain config generation and process management
- **Database**: SQLite in `~/.local/share/mados-equalizer/state.db` (WAL mode)
- **Threading**: Background operations for EQ apply, volume control, device detection
- **Persistence**: Auto-saves on window close via `_on_delete` handler

## GTK/Display Dependencies

This application requires a display server (X11 or Wayland). It will fail in headless environments without `DISPLAY` or `WAYLAND_DISPLAY` set.

## Important File Paths

- EQ config: `~/.config/mados/equalizer/filter-chain.conf`
- Custom presets: `~/.config/mados/equalizer/presets.json`
- State DB: `~/.local/share/mados-equalizer/state.db`