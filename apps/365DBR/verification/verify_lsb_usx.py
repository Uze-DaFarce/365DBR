"""Validate local LSB USX extraction against the canonical verse inventory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from bible_common import BIBLE_DATA  # noqa: E402
from lsb_usx import extract_directory, inventory_usx  # noqa: E402


def expected_ids(book: str) -> set[str]:
    return {
        f"{book}.{chapter}.{verse}"
        for chapter, count in enumerate(BIBLE_DATA[book], start=1)
        for verse in range(1, count + 1)
    }


def verify(directory: Path) -> list[str]:
    extracted = extract_directory(directory)
    issues: list[str] = []
    inventory: set[str] = set()
    paths = sorted(directory.rglob("*.usx"))
    if len(paths) != len(BIBLE_DATA):
        issues.append(f"expected {len(BIBLE_DATA)} USX books, found {len(paths)}")
    for path in paths:
        file_inventory = inventory_usx(path)
        duplicates = inventory & file_inventory
        if duplicates:
            issues.append(f"{path.name}: duplicate verse IDs {', '.join(sorted(duplicates))}")
        inventory.update(file_inventory)

    missing = sorted(inventory - set(extracted))
    empty = sorted(vid for vid in inventory if vid in extracted and not extracted[vid])
    if missing:
        issues.append(f"missing extracted text: {', '.join(missing)}")
    if empty:
        issues.append(f"empty extracted text: {', '.join(empty)}")

    for book in sorted(BIBLE_DATA):
        book_ids = sorted(
            (vid for vid in inventory if vid.startswith(f"{book}.")),
            key=lambda vid: tuple(int(part) for part in vid.split(".")[1:]),
        )
        chapters = {int(vid.split(".")[1]) for vid in book_ids}
        expected_chapters = set(range(1, len(BIBLE_DATA[book]) + 1))
        if chapters != expected_chapters:
            print(
                f"versification chapters: {book} LSB={sorted(chapters)}, "
                f"API-canonical={sorted(expected_chapters)}"
            )
        for chapter in sorted(chapters):
            chapter_verses = sorted(int(vid.split(".")[2]) for vid in book_ids if int(vid.split(".")[1]) == chapter)
            if chapter_verses and chapter_verses != list(range(1, max(chapter_verses) + 1)):
                issues.append(f"{book}.{chapter}: non-contiguous verse milestones {chapter_verses}")

        usx_count = len(book_ids)
        canonical_count = sum(BIBLE_DATA[book])
        if usx_count != canonical_count:
            print(f"versification: {book} LSB={usx_count}, API-canonical={canonical_count}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify all LSB USX books and verses.")
    parser.add_argument("directory", nargs="?", type=Path, default=APP_DIR / "data" / "LSB")
    args = parser.parse_args()
    issues = verify(args.directory)
    if issues:
        print("LSB USX verification failed:")
        print("\n".join(f"- {issue}" for issue in issues))
        return 1
    total = len(extract_directory(args.directory))
    print(f"LSB USX verification passed: {len(BIBLE_DATA)} books, {total} non-empty verses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
