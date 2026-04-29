from pathlib import Path

FORBIDDEN_PUBLIC_STRINGS = [
    "REDACTED",
    "REDACTED",
    "REDACTED",
    "REDACTED",
    "REDACTED",
    "AWS_" + "Ontology",
]


def test_public_docs_do_not_contain_known_private_markers():
    text_files = [
        *Path(".").glob("*.md"),
        *Path("docs").glob("*.md"),
        *Path("tools").glob("*.md"),
        Path("requirements.txt"),
        Path("pyproject.toml"),
    ]

    combined = "\n".join(path.read_text(encoding="utf-8") for path in text_files)
    lowered = combined.lower()

    for marker in FORBIDDEN_PUBLIC_STRINGS:
        assert marker.lower() not in lowered
