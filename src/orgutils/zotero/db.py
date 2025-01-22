"""Zotero database (sqlite)."""

import contextlib
import functools
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Generator, List, Optional


@functools.cache
def _find_zotero_data_dir(path: Optional[str | Path] = None) -> Path:
    paths = [path] if path else []
    paths.extend([Path("~") / "Zotero", Path("~") / ".local" / "var" / "zotero"])
    for path in paths:
        path = Path(path).expanduser()
        if (path / "zotero.sqlite").exists():
            return path
    raise ValueError("Zotedo data directory not found")


@contextlib.contextmanager
def connect(
    zotero_data_dir: Optional[str | Path] = None,
) -> Generator[sqlite3.Connection, None, None]:
    """Get SQLite connection."""
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    db_src = zotero_data_dir / "zotero.sqlite"

    # Zotero locks the database too aggressively; make a (temporary)
    # copy and work with the copy.
    with tempfile.NamedTemporaryFile("w") as tf:
        dbf = tf.name
        shutil.copy(db_src, dbf)

        conn = sqlite3.connect(dbf)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


SQL_LIST_ITEMS: str = """-- sql
SELECT
    items.key,
    itemDataValues.value
FROM items
    LEFT JOIN itemData ON itemData.itemID = items.itemID
    LEFT JOIN itemDataValues ON itemDataValues.valueID = itemData.valueID
    LEFT JOIN fieldsCombined ON fieldsCombined.fieldID = itemData.fieldID
WHERE
    itemDataValues.value LIKE '%Evolution%'
    AND fieldsCombined.fieldName = 'title'
"""


def get_item_list(zotero_data_dir: Optional[str | Path] = None) -> list:
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_LIST_ITEMS)
        rows = cur.fetchall()

    return rows


SQL_LIST_DOCS: str = """-- sql
SELECT
    anno.parentItemID AS id,
    COUNT(*) AS annotationCount,
    SUBSTR(attach.path, 9) AS filename
FROM itemAnnotations anno
    LEFT JOIN items parents ON parents.itemID = anno.parentItemID
    LEFT JOIN itemAttachments attach ON attach.itemID = parents.itemID
GROUP BY id;
"""


def get_doc_list(zotero_data_dir: Optional[str | Path] = None) -> List:
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_LIST_DOCS)
        rows = cur.fetchall()

    return rows


SQL_GET_FILENAME_FOR_ID: str = """-- sql
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


def get_filename_for_id(id: str, zotero_data_dir: Optional[str | Path] = None) -> Path:
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_FILENAME_FOR_ID, (id,))
        row = cur.fetchone()

    if not row:
        raise ValueError("Item for ID does not exist")

    return zotero_data_dir / "storage" / str(row[1]) / str(row[2])


SQL_GET_ANNOTATIONS_FOR_ID = """-- sql
SELECT
    CAST(pageLabel AS INTEGER) AS page,
    position,
    text,
    comment
FROM itemAnnotations
WHERE parentItemID = ?
"""


def get_annotations_for_id(
    id: str, zotero_data_dir: Optional[str | Path] = None
) -> List[dict]:
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    with connect(zotero_data_dir) as conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_ANNOTATIONS_FOR_ID, (id,))
        rows = cur.fetchall()

    def _transform(row: sqlite3.Row) -> dict:
        row_as_dict = dict(row)
        row_as_dict["position"] = json.loads(row_as_dict["position"])
        return row_as_dict

    return [_transform(row) for row in rows]
