"""Zotero database (sqlite)."""
import sqlite3
from pathlib import Path

ZOTERO_DIR = Path("~/.local/var/zotero").expanduser()
ZOTERO_DB = ZOTERO_DIR / "zotero.sqlite"


def connect():  # noqa
    conn = sqlite3.connect(ZOTERO_DB)
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


def get_filename_for_id(id):  # noqa
    conn = connect()
    cur = conn.cursor()
    cur.execute(SQL_GET_FILENAME_FOR_ID, (id,))
    row = cur.fetchone()
    if row is None:
        raise ValueError("Item for ID does not exist")

    path = ZOTERO_DIR / "storage" / row[1] / row[2]
    return path


SQL_GET_ANNOTATIONS_FOR_ID = """
SELECT
    pageLabel,
    text,
    comment
FROM itemAnnotations
WHERE parentItemID = ?
"""


def get_annotations_for_id(id):  # noqa
    conn = connect()
    cur = conn.cursor()
    cur.execute(SQL_GET_ANNOTATIONS_FOR_ID, (id,))
    rows = cur.fetchall()
    return rows
