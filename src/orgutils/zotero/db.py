"""Zotero database (sqlite)."""
import contextlib
import functools
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Generator, List


@functools.cache
def _find_zotero_data_dir(path: str = None) -> Path:
    paths = [path] if path else []
    paths.extend([Path("~") / "Zotero", Path("~") / ".local" / "var" / "zotero"])
    for path in paths:
        path = Path(path).expanduser()
        if (path / "zotero.sqlite").exists():
            return path


@contextlib.contextmanager
def connect(zotero_data_dir: str = None) -> Generator[sqlite3.Connection, None, None]:
    """Get SQLite connection."""
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    db_src = zotero_data_dir / "zotero.sqlite"

    # Zotero locks the database too aggressively; make a (temporary) copy and work with
    # it.
    with tempfile.NamedTemporaryFile("w") as tf:
        dbf = tf.name
        shutil.copy(db_src, dbf)

        conn = sqlite3.connect(dbf)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


SQL_LIST_ITEMS: str = """
SELECT
    anno.parentItemID AS id,
    COUNT(*) AS annotationCount,
    SUBSTR(attach.path, 9) AS filename
FROM itemAnnotations anno
    LEFT JOIN items parents ON parents.itemID = anno.parentItemID
    LEFT JOIN itemAttachments attach ON attach.itemID = parents.itemID
GROUP BY id;
"""


def get_item_list(zotero_data_dir=None) -> List:  # noqa
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_LIST_ITEMS)
        rows = cur.fetchall()

    return rows


SQL_GET_FILENAME_FOR_ID: str = """
SELECT
    anno.parentItemID AS itemID,
    parents.key,
    SUBSTR(attach.path, 9) AS filename
FROM itemAnnotations anno
    LEFT JOIN items parents ON parents.itemID = anno.parentItemID
    LEFT JOIN itemAttachments attach ON attach.itemID = parents.itemID
WHERE anno.parentItemID = ?
GROUP BY anno.parentItemID;
"""


def get_filename_for_id(id, zotero_data_dir=None) -> Path:  # noqa
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_FILENAME_FOR_ID, (id,))
        row = cur.fetchone()

    if not row:
        raise ValueError("Item for ID does not exist")

    return zotero_data_dir / "storage" / row[1] / row[2]


SQL_GET_ANNOTATIONS_FOR_ID = """
SELECT
    CAST(pageLabel AS INTEGER) AS page,
    position,
    text,
    comment
FROM itemAnnotations
WHERE parentItemID = ?
"""


def get_annotations_for_id(id, zotero_data_dir=None) -> List[dict]:  # noqa
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_ANNOTATIONS_FOR_ID, (id,))
        rows = cur.fetchall()

    def transform(row):
        row = dict(row)
        row["position"] = json.loads(row["position"])
        return row

    return [transform(row) for row in rows]
