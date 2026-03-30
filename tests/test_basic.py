#!/usr/bin/env python3
"""Basic tests for mados-equalizer - verify modules compile."""

import py_compile
import os

test_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(test_dir)

def test_translations_compile():
    """Test translations.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/translations.py", doraise=True)


def test_presets_compile():
    """Test presets.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/presets.py", doraise=True)


def test_backend_compile():
    """Test backend.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/backend.py", doraise=True)


def test_app_compile():
    """Test app.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/app.py", doraise=True)


if __name__ == "__main__":
    test_translations_compile()
    test_presets_compile()
    test_backend_compile()
    test_app_compile()
    print("All tests passed!")
