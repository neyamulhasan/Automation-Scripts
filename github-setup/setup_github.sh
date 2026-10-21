#!/usr/bin/env bash

set -Eeuo pipefail

# ==========================================================
# GitHub HTTPS Setup for Linux
# Supports APT, DNF, YUM, Pacman, and Zypper
# ==========================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

trap 'error "Setup failed at line $LINENO."' ERR

# ----------------------------------------------------------
# 1. Detect package manager
# ----------------------------------------------------------

echo
echo "================================================"
echo "          GitHub HTTPS Setup for Linux"
echo "================================================"
echo

if command -v apt-get >/dev/null 2>&1; then
    PKG_MANAGER="apt"
elif command -v dnf >/dev/null 2>&1; then
    PKG_MANAGER="dnf"
elif command -v yum >/dev/null 2>&1; then
    PKG_MANAGER="yum"
elif command -v pacman >/dev/null 2>&1; then
    PKG_MANAGER="pacman"
elif command -v zypper >/dev/null 2>&1; then
    PKG_MANAGER="zypper"
else
    error "Unsupported package manager."
    echo "Supported: APT, DNF, YUM, Pacman, Zypper."
    exit 1
fi

info "Detected package manager: $PKG_MANAGER"

# ----------------------------------------------------------
# 2. Get Git identity
# ----------------------------------------------------------

echo

read -r -p "Enter your Git username: " GIT_NAME
read -r -p "Enter your GitHub email: " GIT_EMAIL

if [[ -z "$GIT_NAME" || -z "$GIT_EMAIL" ]]; then
    error "Git username and email cannot be empty."
    exit 1
fi

# ----------------------------------------------------------
# 3. Install Git and dependencies
# ----------------------------------------------------------

echo
info "[1/5] Installing Git and dependencies..."

case "$PKG_MANAGER" in
    apt)
        sudo apt-get update
        sudo apt-get install -y git curl ca-certificates
        ;;
    dnf)
        sudo dnf install -y git curl ca-certificates
        ;;
    yum)
        sudo yum install -y git curl ca-certificates
        ;;
    pacman)
        sudo pacman -Syu --needed git curl ca-certificates
        ;;
    zypper)
        sudo zypper --non-interactive refresh
        sudo zypper --non-interactive install \
            git curl ca-certificates
        ;;
esac

# ----------------------------------------------------------
# 4. Install GitHub CLI from configured repositories
# ----------------------------------------------------------

echo
info "[2/5] Installing GitHub CLI..."

if command -v gh >/dev/null 2>&1; then
    info "GitHub CLI is already installed."
else
    case "$PKG_MANAGER" in
        apt)
            sudo apt-get install -y gh
            ;;
        dnf)
            sudo dnf install -y gh
            ;;
        yum)
            sudo yum install -y gh
            ;;
        pacman)
            sudo pacman -S --needed github-cli
            ;;
        zypper)
            sudo zypper --non-interactive install gh
            ;;
    esac
fi

# Verify GitHub CLI installation
if ! command -v gh >/dev/null 2>&1; then
    error "GitHub CLI installation failed."
    echo
    echo "The package may not be available in your configured repositories."
    echo "Check your distribution's package sources."
    echo "Official installation guide:"
    echo "https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    exit 1
fi

info "GitHub CLI installed successfully."

# ----------------------------------------------------------
# 5. Configure Git
# ----------------------------------------------------------

echo
info "[3/5] Configuring Git..."

git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
git config --global init.defaultBranch main

if command -v nano >/dev/null 2>&1; then
    git config --global core.editor nano
elif command -v vi >/dev/null 2>&1; then
    git config --global core.editor vi
fi

# Rewrite SCP-style GitHub SSH URLs to HTTPS.
git config --global \
    url."https://github.com/".insteadOf \
    git@github.com:

# Rewrite ssh:// GitHub URLs to HTTPS.
git config --global \
    url."https://github.com/".insteadOf \
    ssh://git@github.com/

info "Git configuration completed."

# ----------------------------------------------------------
# 6. GitHub authentication
# ----------------------------------------------------------

echo
info "[4/5] GitHub authentication..."

if gh auth status; then
    info "Already authenticated with GitHub."
else
    echo
    info "Starting GitHub CLI authentication..."
    echo "Follow the prompts provided by GitHub CLI."
    echo

    gh auth login
fi

# Configure Git to use GitHub CLI for HTTPS authentication.
gh auth setup-git

info "GitHub authentication configured."

# ----------------------------------------------------------
# 7. Verify installation and configuration
# ----------------------------------------------------------

echo
info "[5/5] Verifying installation..."

echo
echo "Git version:"
git --version

echo
echo "GitHub CLI version:"
gh --version

echo
echo "Git username:"
git config --global user.name

echo
echo "Git email:"
git config --global user.email

echo
echo "GitHub authentication:"
gh auth status

# ----------------------------------------------------------
# 8. Display useful commands
# ----------------------------------------------------------

echo
echo "================================================"
echo "          SETUP COMPLETED SUCCESSFULLY"
echo "================================================"

echo
echo "Clone a repository:"
echo "git clone https://github.com/OWNER/REPOSITORY.git"

echo
echo "Check repository status:"
echo "git status"

echo
echo "Stage changes:"
echo "git add ."

echo
echo "Commit changes:"
echo 'git commit -m "Your commit message"'

echo
echo "Push changes:"
echo "git push"

echo
echo "Create a public GitHub repository:"
echo "gh repo create my-project --public"

echo
echo "Create a private GitHub repository:"
echo "gh repo create my-project --private"

echo
info "Git and GitHub CLI are ready to use."