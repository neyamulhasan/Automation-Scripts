#!/usr/bin/env python3
"""Restore Google Takeout capture dates from JSON sidecars.

Dry-run is the default. Use --apply only after reviewing the preview.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mp", ".mp~2"}
SUPPORTED_EXTENSIONS = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS
NUMBERED_SIDECAR = re.compile(r"^(?P<media>.+)\.supplemental-metadata(?:\(\d+\))?\.json$")


def media_from_sidecar(sidecar: Path) -> Path | None:
    match = NUMBERED_SIDECAR.match(sidecar.name)
    if match:
        return sidecar.with_name(match.group("media"))
    if sidecar.name.endswith(".json"):
        return sidecar.with_name(sidecar.name[:-5])
    return None


def capture_time(sidecar: Path) -> tuple[int, str] | None:
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        raw_timestamp = data["photoTakenTime"]["timestamp"]
        timestamp = int(raw_timestamp)
        instant = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, OverflowError):
        return None
    return timestamp, instant.strftime("%Y:%m:%d %H:%M:%SZ")


def discover(
    root: Path, conflict_rule: str = "skip"
) -> tuple[list[tuple[Path, Path, int, str]], Counter[str]]:
    plans: list[tuple[Path, Path, int, str]] = []
    counts: Counter[str] = Counter()
    planned_media: set[Path] = set()
    sidecars_by_media: dict[Path, list[Path]] = {}
    for sidecar in root.rglob("*.json"):
        media = media_from_sidecar(sidecar)
        if media is None:
            counts["unsupported_sidecar_name"] += 1
            continue
        sidecars_by_media.setdefault(media, []).append(sidecar)

    for media, sidecars in sidecars_by_media.items():
        if media.suffix.lower() not in SUPPORTED_EXTENSIONS:
            counts["unsupported_media"] += len(sidecars)
            continue
        if not media.is_file():
            counts["missing_media"] += len(sidecars)
            continue
        parsed_sidecars = [(sidecar, capture_time(sidecar)) for sidecar in sidecars]
        valid = [(sidecar, parsed) for sidecar, parsed in parsed_sidecars if parsed is not None]
        if not valid:
            counts["invalid_timestamp"] += len(sidecars)
            continue
        timestamps = {parsed[0] for _, parsed in valid}
        if len(timestamps) > 1:
            if conflict_rule == "unnumbered":
                preferred = next(
                    ((sidecar, parsed) for sidecar, parsed in valid
                     if sidecar.name.endswith(".supplemental-metadata.json")),
                    None,
                )
                if preferred is None:
                    counts["ambiguous_timestamp"] += 1
                    continue
                valid = [preferred]
            elif conflict_rule in {"earliest", "latest"}:
                valid = [min(valid, key=lambda item: item[1][0])] if conflict_rule == "earliest" else [
                    max(valid, key=lambda item: item[1][0])
                ]
            else:
                counts["ambiguous_timestamp"] += 1
                continue
        if len(valid) != len(sidecars):
            counts["invalid_timestamp"] += len(sidecars) - len(valid)
        sidecar, (timestamp, exif_time) = valid[0]
        plans.append((media, sidecar, timestamp, exif_time))
        planned_media.add(media)

        # Google Motion Photos store the short video beside a JPEG whose
        # sidecar carries the capture timestamp.
        motion_video = None
        if media.name.endswith(".MP.jpg"):
            motion_video = media.with_name(media.name[: -len(".jpg")])
        elif media.name.endswith(".MP~2.jpg"):
            motion_video = media.with_name(media.name[: -len(".jpg")])
        if motion_video and motion_video.is_file() and motion_video not in planned_media:
            plans.append((motion_video, sidecar, timestamp, exif_time))
            planned_media.add(motion_video)
    return plans, counts


def exiftool_args(media: Path, exif_time: str) -> list[str]:
    if media.suffix.lower() in PHOTO_EXTENSIONS:
        return [
            "-EXIF:DateTimeOriginal=" + exif_time,
            "-EXIF:CreateDate=" + exif_time,
            "-EXIF:ModifyDate=" + exif_time,
            "-EXIF:OffsetTimeOriginal=+00:00",
            "-EXIF:OffsetTimeDigitized=+00:00",
        ]
    # QuickTime date fields are UTC when written with a trailing Z.
    return [
        "-QuickTime:CreateDate=" + exif_time,
        "-QuickTime:ModifyDate=" + exif_time,
        "-QuickTime:TrackCreateDate=" + exif_time,
        "-QuickTime:TrackModifyDate=" + exif_time,
        "-QuickTime:MediaCreateDate=" + exif_time,
        "-QuickTime:MediaModifyDate=" + exif_time,
        "-Keys:CreationDate=" + exif_time,
    ]


def apply_one(media: Path, exif_time: str, timestamp: int) -> None:
    command = [
        "exiftool",
        "-overwrite_original_in_place",
        "-api",
        "QuickTimeUTC=1",
        *exiftool_args(media, exif_time),
        str(media),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.utime(media, (timestamp, timestamp))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="write metadata and filesystem timestamps")
    parser.add_argument("--preview-limit", type=int, default=20)
    parser.add_argument(
        "--resolve-conflicts",
        choices=("skip", "unnumbered", "earliest", "latest"),
        default="skip",
        help="resolve conflicting sidecars with an explicit rule instead of skipping",
    )
    args = parser.parse_args()

    if shutil.which("exiftool") is None:
        print("ERROR: exiftool was not found on PATH.", file=sys.stderr)
        return 2
    root = args.root.resolve()
    plans, skipped = discover(root, args.resolve_conflicts)
    print(f"Root: {root}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print(f"Exact supported matches: {len(plans)}")
    print(f"Skipped: {sum(skipped.values())} ({dict(sorted(skipped.items()))})")
    print("\nPreview:")
    for media, sidecar, timestamp, exif_time in plans[: max(args.preview_limit, 0)]:
        kind = "photo" if media.suffix.lower() in PHOTO_EXTENSIONS else "video"
        print(f"{kind}\t{exif_time}\t{media}\t<- {sidecar}")
    if len(plans) > max(args.preview_limit, 0):
        print(f"... {len(plans) - max(args.preview_limit, 0)} more")

    if not args.apply:
        print("\nNo files changed. Review this preview, then rerun with --apply to execute.")
        return 0

    results: Counter[str] = Counter()
    for media, _sidecar, timestamp, exif_time in plans:
        try:
            apply_one(media, exif_time, timestamp)
        except (OSError, subprocess.CalledProcessError) as exc:
            results["failed"] += 1
            print(f"FAILED\t{media}\t{exc}", file=sys.stderr)
        else:
            results["repaired"] += 1
    print(f"\nResults: repaired={results['repaired']} failed={results['failed']} skipped={sum(skipped.values())}")
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
