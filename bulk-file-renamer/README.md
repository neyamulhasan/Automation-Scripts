# Bulk File Renamer

Rename many files at once using a prefix, suffix, text replacement, or
sequential numbering.

The tool is safe by default: it shows a preview and does not change files
unless `--apply` is supplied.

## Requirements

- Python 3.10 or newer
- No third-party Python packages

## Usage

Run a preview in a folder:

```bash
python rename_files.py "/path/to/folder" --prefix "holiday-"
```

Apply the same rename after reviewing the preview:

```bash
python rename_files.py "/path/to/folder" --prefix "holiday-" --apply
```

Add a suffix before each extension:

```bash
python rename_files.py "/path/to/photos" --suffix "-edited" --extension jpg
```

Replace text in filenames:

```bash
python rename_files.py "/path/to/files" --replace " " "_" --apply
```

Number files in sorted filename order:

```bash
python rename_files.py "/path/to/files" --number --start 1 --digits 3
```

Include subdirectories with `--recursive`. Options can be combined; for
example, `--prefix "backup-" --number --digits 3`.

## Safety

- Preview mode is the default.
- Existing destination files and duplicate destinations are rejected.
- Files are renamed within their original directories.
- No files are deleted or uploaded.
- Back up important files before using `--apply`.
