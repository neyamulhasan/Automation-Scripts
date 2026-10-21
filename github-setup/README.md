# GitHub HTTPS Setup

Set up Git and the GitHub CLI on Linux with automated package installation,
global configuration, and HTTPS authentication.

## Requirements

- Linux operating system
- Supported package manager: APT, DNF, YUM, Pacman, or Zypper
- `sudo` access to install packages

## Usage

Make the script executable:

```bash
chmod +x setup_github.sh
```

Run the script:

```bash
./setup_github.sh
```

Follow the prompts during execution:

1. Enter your Git username and GitHub email when asked.
2. The script installs Git, curl, ca-certificates, and the GitHub CLI (`gh`).
3. If not already authenticated, complete the interactive login via `gh auth login`.

The script automatically configures:

- `user.name` and `user.email` for your Git commits
- Default initial branch name set to `main`
- Default text editor (`nano` or `vi`)
- Automatic URL rewriting of SSH GitHub URLs to HTTPS
- Git credential authentication through the GitHub CLI (`gh auth setup-git`)

## Safety

- Does not store personal passwords or tokens in files or scripts.
- Authentication credentials are managed securely by the official GitHub CLI.
- Only modifies your local global Git configuration (`~/.gitconfig`) and installs required system packages.
