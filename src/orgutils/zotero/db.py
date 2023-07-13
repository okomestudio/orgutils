"""Zotero database (sqlite)."""
import functools
import json
import sqlite3
from pathlib import Path
from typing import List


@functools.cache
def _find_zotero_data_dir(path: str = None) -> Path:
    paths = [path] if path else []
    paths.extend([Path("~") / "Zotero", Path("~") / ".local" / "var" / "zotero"])
    for path in paths:
        path = Path(path).expanduser()
        if (path / "zotero.sqlite").exists():
            return path


def connect(zotero_data_dir: str = None) -> sqlite3.Connection:
    """Get SQLite connection."""
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)
    conn = sqlite3.connect(zotero_data_dir / "zotero.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


SQL_LIST_ITEMS: str = """
SELECT
    parentItemID AS itemID,
    COUNT(*) AS num_annotations,
    itemDataValues.value AS filename
FROM itemAnnotations annotations
    LEFT JOIN items parents ON parents.itemID = annotations.parentItemID
    LEFT JOIN itemData ON itemData.itemID = parents.itemID AND itemData.fieldID = 1
    LEFT JOIN itemDataValues ON itemDataValues.valueID = itemData.valueID
GROUP BY parentItemID;
"""


SQL_GET_FILENAME_FOR_ID: str = """
SELECT
    parentItemID AS itemID,
    key,
    itemDataValues.value AS filename
FROM itemAnnotations annotations
    LEFT JOIN items parents ON parents.itemID = annotations.parentItemID
    LEFT JOIN itemData ON itemData.itemID = parents.itemID AND itemData.fieldID = 1
    LEFT JOIN itemDataValues ON itemDataValues.valueID = itemData.valueID
WHERE parentItemID = ?
GROUP BY parentItemID;
"""


def get_filename_for_id(id, zotero_data_dir=None) -> Path:  # noqa
    zotero_data_dir = _find_zotero_data_dir(zotero_data_dir)

    conn = connect(zotero_data_dir)
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

    conn = connect(zotero_data_dir)
    cur = conn.cursor()
    cur.execute(SQL_GET_ANNOTATIONS_FOR_ID, (id,))
    rows = cur.fetchall()

    def transform(row):
        row = dict(row)
        row["position"] = json.loads(row["position"])
        return row

    return [transform(row) for row in rows]
