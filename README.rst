********************
orgutils
********************

The PKM helper for Emacs Org mode written in Python.

This tool currently supports Org-format conversion of notes/annotations/highlights dumps
from several PKM services and devices.


Annotation Exports in Org format
================================

Kindle
------

To convert an export JSON dump from Kindle notes and highlights using `Bookcision
<https://readwise.io/bookcision>`_ to an Org file, use ``org-from-kindle``.

.. code-block:: shell

   org-from-kindle -h                 # help
   org-from-kindle -l en <json-dump>  # dump is in English
   org-from-kindle -l ja <json_dump>  # dump is in Japanese


Snipd
-----

To convert an export Markdown dump from `Snipd <https://www.snipd.com/>`_ to an Org file,
use ``org-from-snipd``.

.. code-block:: shell

   org-from-snipd -h               # help
   org-from-snipd <markdown-dump>  # Org export of Snipd dump


Zotero
------

To export a PDF document from a local `Zotero <https://www.zotero.org/>`_ installation to
an Org file, use ``org-from-zotero``.

.. code-block:: shell

   org-from-zotero -h            # help
   org-from-zotero list          # get doc IDs
   org-from-zotero extract <id>  # Org export of doc with ID


Installation
============

The ``orgutils`` is a pure Python package. As such, it is best to install it to a clean
virtual environment. We assume the following install commands are run within such an
environment.

.. code-block:: shell

   pip install .
   pip install .[dev,test]  # for local development

The Snipd submodule uses `pandoc <https://pandoc.org/installing.html>`_. Install it
separately if you need it.
