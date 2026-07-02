#!/bin/sh
set -e

REPO="josephvjm/find-life"
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

# # Resolve latest release download URL via GitHub API
DOWNLOAD_URL=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
  | grep "browser_download_url" \
  | grep "${ASSET}" \
  | sed 's/.*"browser_download_url": "\(.*\)"/\1/')
# DOWNLOAD_URL=file:///$(pwd)/dist/find-life

if [ -z "$DOWNLOAD_URL" ]; then
  echo "No release asset found for ${ASSET}"
  exit 1
fi

echo "Downloading ${ASSET}..."
curl -fsSL "$DOWNLOAD_URL" -o "/tmp/${BIN_NAME}"
chmod +x "/tmp/${BIN_NAME}"

# Install — fall back to ~/.local/bin if /usr/local/bin needs sudo
if [ -w "$BIN_DIR" ]; then
  mv "/tmp/${BIN_NAME}" "${BIN_DIR}/${BIN_NAME}"
else
  echo "Need sudo to install to ${BIN_DIR}"
  sudo mv "/tmp/${BIN_NAME}" "${BIN_DIR}/${BIN_NAME}"
fi

echo "Installed: $(which ${BIN_NAME})"
echo "Run: ${BIN_NAME} --help"
