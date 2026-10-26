"""Keep documentation in sync with the repository and the CLI."""

import re
from pathlib import Path

import pytest

from ontology_graph_generator.cli import build_parser

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_FILES = sorted(
    path for path in [*ROOT.glob("*.md"), *(ROOT / "docs").glob("*.md")] if path.is_file()
)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCED_BLOCK = re.compile(r"```[a-z]*\n(.*?)```", re.DOTALL)


@pytest.mark.parametrize("doc", MARKDOWN_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(doc):
    for target in LINK.findall(doc.read_text(encoding="utf-8")):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        path = (doc.parent / target.split("#")[0]).resolve()
        assert path.exists(), f"{doc.name} links to missing {target}"


@pytest.mark.parametrize("doc", MARKDOWN_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_documented_cli_flags_exist(doc):
    known = {opt for action in build_parser()._actions for opt in action.option_strings}

    for block in FENCED_BLOCK.findall(doc.read_text(encoding="utf-8")):
        # Join continuation lines so multi-line commands are checked as one
        for command in block.replace("\\\n", " ").splitlines():
            if "ontology-transform" not in command:
                continue
            for flag in re.findall(r"(?<!\S)--[a-z][a-z-]*", command):
                assert flag in known, f"{doc.name} documents unknown flag {flag}: {command}"
