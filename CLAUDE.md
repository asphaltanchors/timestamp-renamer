# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python utility for renaming video and image files based on their metadata timestamps. The core functionality is in `rename_videos.py`, which:

- Detects device type (iPhone/Android) from file metadata using exiftool
- Extracts creation timestamps from video/image metadata using ffprobe  
- Falls back to file extension-based device detection and mtime for timestamps
- Renames files to format: `YYYYMMDD-HHMMSS-device.ext` in Pacific timezone
- Supports .mov, .mp4, .heic, .jpg, .jpeg files

## Dependencies

The script requires these external tools to be installed:
- `exiftool` - for extracting device metadata from files
- `ffprobe` (part of FFmpeg) - for extracting creation timestamps from video files

Python dependencies are standard library only (no pip packages required):
- `argparse`, `json`, `os`, `re`, `subprocess`, `datetime`, `zoneinfo`

## Key Architecture

- `detect_device_from_metadata()` - Uses exiftool to determine if file is from iPhone or Android
- `run_ffprobe_datetime()` - Extracts creation timestamp from media metadata  
- `pacific_stamp()` - Converts UTC datetime to Pacific timezone formatted string
- `is_already_renamed()` - Checks if file is already in target format to avoid re-processing
- `unique_target()` - Handles filename conflicts by appending -1, -2, etc.

## Running the Script

```bash
# Basic usage
python3 rename_videos.py /path/to/media/folder

# Dry run to see what would happen
python3 rename_videos.py --dry-run /path/to/media/folder

# Custom prefixes
python3 rename_videos.py --iphone-prefix "iphone" --android-prefix "android" /path/to/folder
```

## Testing

No formal test framework is configured. To test changes:
1. Create a test directory with sample media files
2. Run with `--dry-run` flag first to verify expected behavior
3. Test both metadata extraction and fallback mechanisms