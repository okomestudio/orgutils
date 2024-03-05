********************
orgutils
********************

*orgutils* for Python.


Annotation Exports in Org format
================================

Kindle
------

.. code-block:: shell

   python -m orgutils.kindle -h                 # help
   python -m orgutils.kindle -l en <json-dump>  # Org export of Bookcision dump (en)
   python -m orgutils.kindle -l ja <json_dump>  # Org export of Bookcision dump (ja)


Snipd
-----

.. code-block:: shell

   python -m orgutils.snipd -h               # help
   python -m orgutils.snipd <markdown-dump>  # Org export of Snipd dump


Zotero
------

.. code-block:: shell

   python -m orgutils.zotero -h            # help
   python -m orgutils.zotero list          # get doc IDs
   python -m orgutils.zotero extract <id>  # Org export of doc with ID
