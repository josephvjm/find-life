#!/bin/sh
set -e

REPO="your-github-username/find-life"
BIN_DIR="/usr/local/bin"
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

# Prefer /usr/local/bin; fall back to ~/.local/bin to avoid sudo in piped scripts
if [ -w "$BIN_DIR" ]; then
  mv "/tmp/${BIN_NAME}" "${BIN_DIR}/${BIN_NAME}"
else
  BIN_DIR="$HOME/.local/bin"
  mkdir -p "$BIN_DIR"
  mv "/tmp/${BIN_NAME}" "${BIN_DIR}/${BIN_NAME}"
  # Warn if ~/.local/bin isn't on PATH
  case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "Note: add $BIN_DIR to your PATH: export PATH=\"$BIN_DIR:\$PATH\"" ;;
  esac
fi

echo "Installed: $(which ${BIN_NAME})"
echo "Run: ${BIN_NAME} --help"
