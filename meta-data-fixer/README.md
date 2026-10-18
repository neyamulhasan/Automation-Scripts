# Google Takeout Metadata Fixer

Restore capture dates in Google Takeout photos and videos using the
`*.json` sidecar files exported with the media.

The script is safe by default: it performs a dry run and does not change
files unless `--apply` is supplied.

## Requirements

- Python 3.10 or newer
- ExifTool

Install ExifTool on Ubuntu or Debian:

```bash
sudo apt install libimage-exiftool-perl
```

On macOS:

```bash
brew install exiftool
```

On Windows:

```powershell
winget install OliverBetz.ExifTool
```

No third-party Python packages are required, so this project does not need
`pip install` or a Python `requirements.txt` file.

## Usage

Run a dry run first:

```bash
python restore_takeout_dates.py "/path/to/Google Takeout"
```

Review the preview, then apply the metadata and filesystem timestamp changes:

```bash
python restore_takeout_dates.py "/path/to/Google Takeout" --apply
```

The default conflict behavior is to skip media with conflicting timestamps.
Other options are available when needed:

```bash
python restore_takeout_dates.py "/path/to/Google Takeout" \
  --resolve-conflicts earliest \
  --preview-limit 50
```

Supported conflict rules are `skip`, `unnumbered`, `earliest`, and `latest`.

## Safety

Make a backup of your media before using `--apply`. The script writes
metadata in place and updates filesystem timestamps. It does not upload files
or send data anywhere.

Do not commit Google Takeout photos, videos, JSON sidecars, or command output
to the repository. The included `.gitignore` helps prevent accidental
uploads, but always review staged files before pushing.
