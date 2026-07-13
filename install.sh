#!/bin/sh
set -e

REPO="josephvjm/find-life"
BIN_DIR="$HOME/.local/bin"
BIN_NAME="find-life"

# Detect OS
case "$(uname -s)" in
  Linux)  OS="linux" ;;
  Darwin) OS="macos" ;;
  *)
    echo "Unsupported OS: $(uname -s)"
    exit 1
    ;;
esac

# Detect arch
case "$(uname -m)" in
  x86_64)          ARCH="x86_64" ;;
  arm64 | aarch64) ARCH="arm64" ;;
  *)
    echo "Unsupported architecture: $(uname -m)"
    exit 1
    ;;
esac

ASSET="${BIN_NAME}-${OS}-${ARCH}"

# Resolve latest release download URL via GitHub API
DOWNLOAD_URL=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
  | grep "browser_download_url" \
  | grep "${ASSET}" \
  | sed 's/.*"browser_download_url": "\(.*\)"/\1/')

if [ -z "$DOWNLOAD_URL" ]; then
  echo "No release asset found for ${ASSET}"
  exit 1
fi

echo "Downloading ${ASSET}..."
curl -fsSL "$DOWNLOAD_URL" -o "/tmp/${BIN_NAME}"
chmod +x "/tmp/${BIN_NAME}"

mkdir -p "$BIN_DIR"
mv "/tmp/${BIN_NAME}" "${BIN_DIR}/${BIN_NAME}"

# Add ~/.local/bin to PATH in shell config if not already there
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    SHELL_RC=""
    if [ -f "$HOME/.zshrc" ]; then
      SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
      SHELL_RC="$HOME/.bashrc"
    fi

    if [ -n "$SHELL_RC" ]; then
      printf '\n# find-life\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$SHELL_RC"
      echo "Added $BIN_DIR to PATH in $SHELL_RC"
      echo "Restart your terminal or run: source $SHELL_RC"
    else
      echo "Note: add $BIN_DIR to your PATH manually: export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    ;;
esac

echo "Installed: ${BIN_DIR}/${BIN_NAME}"
echo "Run: ${BIN_NAME} --help"
