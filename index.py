"""Optional alias for ``gunicorn index:app``. Prefer ``wsgi:app`` (see ``wsgi.py``)."""
from main import app

__all__ = ["app"]
