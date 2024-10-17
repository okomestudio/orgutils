from importlib import resources as module_resources

import pytest

from orgutils.snipd import converter

from . import data


@pytest.fixture
def snipd_dump_2408():
    md_dump = module_resources.files(data) / "dump-2024-08.md"
    with md_dump.open() as f:
        return f.read()


@pytest.fixture
def snipd_dump_2410():
    md_dump = module_resources.files(data) / "dump-2024-10.md"
    with md_dump.open() as f:
        return f.read()


class TestToHtml:
    def test(self, snipd_dump_2410):
        snipd_dump = snipd_dump_2410
        org = converter.convert(snipd_dump, "org")
        assert "* John Doe - A Podcast Episode 2024-10" in org

    def test_ver_2024_08(self, snipd_dump_2408):
        snipd_dump = snipd_dump_2408
        org = converter.convert(snipd_dump, "org")

        assert "* John Doe - A Podcast Episode 2024-08" in org
