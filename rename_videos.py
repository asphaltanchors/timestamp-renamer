#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Python 3.9+

PACIFIC = ZoneInfo("America/Los_Angeles")
VIDEO_EXTS = {".mov": "iphone", ".mp4": "android"}  # extension -> prefix


def run_ffprobe_datetime(path: str) -> datetime | None:
    """
    Try to extract a creation timestamp via ffprobe.
    Returns an aware UTC datetime if found, else None.
    """
    # Ask for creation_time in both container and stream tags, JSON for reliability
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_entries",
        "format_tags=creation_time:stream_tags=creation_time",
        path
    ]
    try:
        out = subprocess.check_output(cmd)
        data = json.loads(out.decode("utf-8", errors="replace"))
    except Exception:
        return None

    # Possible places creation_time may appear (container first, then streams)
    candidates = []
    fmt_tags = data.get("format", {}).get("tags", {})
    if "creation_time" in fmt_tags:
        candidates.append(fmt_tags["creation_time"])

    for stream in data.get("streams", []):
        tags = stream.get("tags", {})
        if "creation_time" in tags:
            candidates.append(tags["creation_time"])

    # Parse the first valid ISO-ish timestamp we can
    for ts in candidates:
        dt = _parse_iso_to_utc(ts)
        if dt:
            return dt
    return None


def _parse_iso_to_utc(s: str) -> datetime | None:
    """
    Parse common ffprobe date formats into an aware UTC datetime.
    Examples:
      '2025-08-20T18:23:45.000000Z'
      '2025-08-20T18:23:45Z'
      '2025-08-20 18:23:45'
    """
    s = s.strip()
    try:
        # If it ends with Z or includes offset, fromisoformat (with tweaks) can handle it
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        # Some files use space instead of T
        s = s.replace(" ", "T")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            # Assume UTC if no tz in metadata
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        # Try a couple of common fallback formats
        fmts = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        for f in fmts:
            try:
                dt = datetime.strptime(s, f).replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
    return None


def get_file_time_utc(path: str) -> datetime:
    """Fallback: file modification time as UTC-aware datetime."""
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def pacific_stamp(dt_utc: datetime) -> str:
    """Convert UTC dt to Pacific and format YYYYMMDD-HHMMSS."""
    dt_local = dt_utc.astimezone(PACIFIC)
    return dt_local.strftime("%Y%m%d-%H%M%S")


def unique_target(dirpath: str, base: str, ext: str) -> str:
    """
    Ensure the target filename is unique by appending -1, -2, ...
    Returns the full path.
    """
    target = os.path.join(dirpath, f"{base}{ext.lower()}")
    if not os.path.exists(target):
        return target
    i = 1
    while True:
        candidate = os.path.join(dirpath, f"{base}-{i}{ext.lower()}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


def main():
    ap = argparse.ArgumentParser(
        description="Rename .mov (iPhone) and .mp4 (Android) videos based on metadata timestamp (Pacific time)."
    )
    ap.add_argument("directory", help="Path to the directory containing videos")
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen without renaming")
    ap.add_argument("--iphone-prefix", default="iphone", help="Prefix for .mov files (default: iphone)")
    ap.add_argument("--android-prefix", default="android", help="Prefix for .mp4 files (default: android)")
    args = ap.parse_args()

    dirpath = os.path.abspath(args.directory)
    if not os.path.isdir(dirpath):
        print(f"Not a directory: {dirpath}")
        return

    renamed = 0
    skipped = 0

    for name in sorted(os.listdir(dirpath)):
        src = os.path.join(dirpath, name)
        if not os.path.isfile(src):
            continue

        root, ext = os.path.splitext(name)
        ext_lower = ext.lower()
        if ext_lower not in VIDEO_EXTS:
            continue

        prefix = args.iphone_prefix if ext_lower == ".mov" else args.android_prefix

        # Get timestamp (ffprobe -> mtime fallback)
        dt_utc = run_ffprobe_datetime(src)
        if dt_utc is None:
            dt_utc = get_file_time_utc(src)

        stamp = pacific_stamp(dt_utc)
        base = f"{stamp}-{prefix}"

        # Preserve original extension
        dst = unique_target(dirpath, base, ext_lower)

        if os.path.abspath(src) == os.path.abspath(dst):
            print(f"Skip (already named): {name}")
            skipped += 1
            continue

        rel_src = os.path.relpath(src, dirpath)
        rel_dst = os.path.relpath(dst, dirpath)

        if args.dry_run:
            print(f"[DRY] {rel_src} -> {rel_dst}")
        else:
            os.rename(src, dst)
            print(f"{rel_src} -> {rel_dst}")
        renamed += 1

    if args.dry_run:
        print(f"\nDry run complete. Candidates processed: {renamed + skipped}.")
    else:
        print(f"\nDone. Renamed: {renamed}, Skipped: {skipped}.")


if __name__ == "__main__":
    main()
