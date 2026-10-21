# Automation-Scripts

Small, practical automation tools for everyday computer tasks.

## Why this repository exists

This repository is my personal toolkit for turning repetitive computer work
into simple, reusable scripts. The goal is to save time, reduce manual effort,
and make common file-management tasks more organized and reliable.

Each tool is intended to solve one focused problem clearly rather than become
part of a large, complicated application. The collection can grow over time as
new everyday problems appear.

## What I care about

These scripts are built to be:

| Principle | What it means |
| --- | --- |
| **Useful** | Save time by handling repetitive tasks. |
| **Simple** | Do one job and stay easy to understand. |
| **Reusable** | Work with different files, folders, and situations. |
| **Safe** | Avoid personal paths, passwords, and private information. |
| **Preview-first** | Show what will happen before changing files. |
| **Well-documented** | Explain setup, usage, and important warnings. |
| **Clear** | Never make important changes silently. |

## Available tools

### 1. [`meta-data-fixer`](./meta-data-fixer/)

See the [`meta-data-fixer` README](./meta-data-fixer/README.md) for details.

### 2. [`bulk-file-renamer`](./bulk-file-renamer/)

See the [`bulk-file-renamer` README](./bulk-file-renamer/README.md) for details.

### 3. [`github-setup`](./github-setup/)

See the [`github-setup` README](./github-setup/README.md) for details.

## General usage and safety

Before using a script:

1. Read its tool-specific README.
2. Check its requirements and review the command you plan to run.
3. Use its preview or dry-run mode when available.
4. Back up important files before applying changes.
5. Review the results after the script completes.

Scripts in this repository are designed for local use. They should not upload
files or expose private information unless a tool explicitly documents that
behavior.

## Adding a new tool

New scripts should:

- Live in their own clearly named directory.
- Have a focused purpose and straightforward command-line usage.
- Use configurable paths instead of personal absolute paths.
- Provide a dry-run or preview mode when they modify files.
- Include a README with requirements, examples, and safety notes.
- Avoid committing credentials, private data, generated output, or personal
  file paths.
