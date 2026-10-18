#!/usr/bin/env python3
"""Preview or apply batch file renames safely."""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path


Plan = tuple[Path, Path]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rename files with a preview shown by default."
    )
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--prefix", default="", help="Add text to each filename.")
    parser.add_argument("--suffix", default="", help="Add text before each extension.")
    parser.add_argument(
        "--replace",
        nargs=2,
        metavar=("OLD", "NEW"),
        help="Replace text in each filename.",
    )
    parser.add_argument(
        "--extension",
        help="Only rename files with this extension, such as .jpg or jpg.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include files in subdirectories.",
    )
    parser.add_argument(
        "--number",
        action="store_true",
        help="Add sequential numbers before each file extension.",
    )
    parser.add_argument("--start", type=int, default=1, help="First number (default: 1).")
    parser.add_argument(
        "--digits",
        type=int,
        default=0,
        help="Minimum number width, for example 3 produces 001 (default: no padding).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the planned renames. Without this option, only a preview is shown.",
    )
    return parser


def matching_files(root: Path, recursive: bool, extension: str | None) -> list[Path]:
    paths = root.rglob("*") if recursive else root.iterdir()
    normalized_extension = None
    if extension:
        normalized_extension = extension if extension.startswith(".") else "." + extension
        normalized_extension = normalized_extension.casefold()
    return sorted(
        (
            path
            for path in paths
            if path.is_file()
            and (normalized_extension is None or path.suffix.casefold() == normalized_extension)
        ),
        key=lambda path: str(path).casefold(),
    )


def new_name(
    path: Path,
    prefix: str,
    suffix: str,
    replacement: tuple[str, str] | None,
    number: int | None,
    digits: int,
) -> str:
    stem = path.stem
    if replacement:
        stem = stem.replace(*replacement)
    if number is not None:
        formatted_number = str(number).zfill(digits)
        stem = f"{formatted_number}_{stem}"
    return f"{prefix}{stem}{suffix}{path.suffix}"


def plan_renames(
    files: list[Path],
    prefix: str,
    suffix: str,
    replacement: tuple[str, str] | None,
    start: int,
    number: bool,
    digits: int,
) -> list[Plan]:
    return [
        (path, path.with_name(new_name(path, prefix, suffix, replacement,
                                       start + index if number else None, digits)))
        for index, path in enumerate(files)
    ]


def validate_plan(plans: list[Plan]) -> list[str]:
    errors: list[str] = []
    moving_sources = {
        source.resolve() for source, destination in plans if source != destination
    }
    destinations: dict[Path, Path] = {}
    for source, destination in plans:
        resolved_destination = destination.resolve()
        if source == destination:
            continue
        if resolved_destination in destinations:
            errors.append(
                f"multiple files would become {destination}: "
                f"{destinations[resolved_destination]} and {source}"
            )
        destinations[resolved_destination] = source
        if destination.exists() and resolved_destination not in moving_sources:
            errors.append(f"destination already exists: {destination}")
    return errors


def apply_plan(plans: list[Plan]) -> int:
    temporary: list[tuple[Path, Path, Path]] = []
    try:
        for source, destination in plans:
            if source == destination:
                continue
            temporary_path = source.with_name(f".{source.name}.rename-{uuid.uuid4().hex}")
            os.rename(source, temporary_path)
            temporary.append((temporary_path, destination, source))
        for temporary_path, destination, _source in temporary:
            os.rename(temporary_path, destination)
    except OSError as exc:
        for temporary_path, _destination, source in reversed(temporary):
            if temporary_path.exists() and not source.exists():
                os.rename(temporary_path, source)
        print(f"ERROR: rename failed: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.digits < 0:
        parser.error("--digits cannot be negative")
    if args.number and args.start < 0:
        parser.error("--start cannot be negative when numbering is enabled")
    if not any((args.prefix, args.suffix, args.replace, args.number)):
        parser.error("choose at least one rename option")

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: directory not found: {root}", file=sys.stderr)
        return 2

    files = matching_files(root, args.recursive, args.extension)
    plans = plan_renames(
        files, args.prefix, args.suffix, tuple(args.replace) if args.replace else None,
        args.start, args.number, args.digits,
    )
    errors = validate_plan(plans)
    print(f"Root: {root}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print(f"Files found: {len(files)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("\nPreview:")
    for source, destination in plans:
        if source != destination:
            print(f"{source}  ->  {destination}")
    changes = sum(source != destination for source, destination in plans)
    if not args.apply:
        print(f"\nPlanned changes: {changes}")
        print("No files changed. Review this preview, then rerun with --apply.")
        return 0
    result = apply_plan(plans)
    if result == 0:
        print(f"\nRenamed: {changes}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
