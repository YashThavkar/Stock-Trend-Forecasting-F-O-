"""
WSGI entry for hosting the static site in ``docs/`` (e.g. Render).

Start locally:  gunicorn main:app --bind 127.0.0.1:8080
Render: set start command to  gunicorn main:app --bind 0.0.0.0:$PORT
"""
from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, send_from_directory

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

app = Flask(__name__)


def _under_docs(path: Path) -> bool:
    try:
        path.resolve().relative_to(DOCS.resolve())
    except ValueError:
        return False
    return True


@app.get("/")
def index() -> object:
    return send_from_directory(DOCS, "index.html")


@app.get("/<path:rel>")
def static_files(rel: str) -> object:
    if ".." in Path(rel).parts:
        abort(404)
    path = (DOCS / rel).resolve()
    if not _under_docs(path):
        abort(404)
    if path.is_dir():
        path = path / "index.html"
    if not path.is_file():
        abort(404)
    return send_from_directory(path.parent, path.name)
