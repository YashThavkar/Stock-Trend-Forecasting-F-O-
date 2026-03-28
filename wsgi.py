"""
WSGI entry for Gunicorn on Render.

Use exactly:  gunicorn wsgi:app --bind 0.0.0.0:$PORT

Do not use index.html here — that is static HTML under docs/, not a Python module.
"""
from main import app

__all__ = ["app"]
