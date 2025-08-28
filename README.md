# Media Timestamp Renamer

A Python utility for renaming video and image files based on their creation timestamps. Originally created for organizing media files from asphalt anchor testing to streamline video editing workflows.

## Purpose

When testing asphalt anchors, media files from different devices (iPhones, Android phones) often have inconsistent naming schemes that make chronological organization difficult during video editing. This script standardizes filenames using actual creation timestamps and device detection.

## Features

- **Metadata-based timestamps**: Extracts creation time from video/image metadata using ffprobe
- **Device detection**: Identifies iPhone vs Android files using exiftool metadata analysis
- **Consistent naming**: Renames files to `YYYYMMDD-HHMMSS-device.ext` format in Pacific timezone
- **Conflict resolution**: Automatically handles duplicate timestamps by appending `-1`, `-2`, etc.
- **Safe operation**: Includes dry-run mode and skips already-renamed files

## Supported File Types

- **iPhone**: `.mov`, `.heic`
- **Android**: `.mp4`, `.jpg`, `.jpeg`

## Prerequisites

Install the required external tools:

**macOS (with Homebrew):**
```bash
brew install exiftool ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install exiftool ffmpeg
```

## Usage

### Basic usage
```bash
python3 rename_videos.py /path/to/media/folder
```

### Preview changes (recommended first)
```bash
python3 rename_videos.py --dry-run /path/to/media/folder
```

### Custom device prefixes
```bash
python3 rename_videos.py --iphone-prefix "iphone" --android-prefix "android" /path/to/folder
```

## Example

**Before:**
```
IMG_1234.mov
20240820_143022.mp4
PXL_20240820_212345678.jpg
```

**After:**
```
20240820-143022-iphone.mov
20240820-143022-android.mp4
20240820-212345-android.jpg
```

## How It Works

1. **Device Detection**: Uses exiftool to read metadata and identify device manufacturer
2. **Timestamp Extraction**: Attempts to extract creation time from metadata using ffprobe
3. **Fallback**: If metadata is unavailable, uses file modification time and extension-based device detection
4. **Timezone Conversion**: Converts timestamps to Pacific timezone for consistent naming
5. **Safe Renaming**: Checks for existing files and conflicts before renaming

## Notes

- Files already in the correct format are automatically skipped
- Original file extensions are preserved (but normalized to lowercase)
- Pacific timezone is used for all timestamps to match typical testing location
- The script processes files in alphabetical order for predictable behavior