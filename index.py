"""
Some hosts default to ``gunicorn index:app``. The real app is defined in ``main``; this file re-exports it.
"""
from main import app

__all__ = ["app"]
