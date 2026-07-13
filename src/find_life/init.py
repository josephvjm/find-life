from __future__ import annotations

import json
import secrets
import socket
from datetime import datetime
from pathlib import Path

import click
import httpx

BASE_URL = "https://find-life.org"
CONFIG_DIR = Path.home() / ".find-life"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    CONFIG_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save_config(token: str) -> None:
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"find-life-token": token}, indent=2))


def make_token_name() -> str:
    host = socket.gethostname().split(".")[0]
    date = datetime.now().strftime("%Y%m%d")
    suffix = secrets.token_hex(4)
    return f"{host}-{date}-{suffix}"


def provision_token(token: str) -> str:
    response = httpx.post(f"{BASE_URL}/api", json={"token": token}, timeout=10)
    response.raise_for_status()
    result = response.json()["token"]
    click.echo(f"New token created, saved to {CONFIG_FILE}")
    return result


def ensure_token() -> str:
    config = load_config()
    token = config.get("find-life-token", "")
    today = datetime.now().strftime("%Y%m%d")
    if token and today in token:
        return token
    token = provision_token(make_token_name())
    save_config(token)
    return token


def run_init() -> None:
    try:
        token = provision_token(make_token_name())
        save_config(token)
    except httpx.HTTPStatusError as e:
        click.echo(f"Request failed: {e.response.status_code} {e.response.text}")
    except httpx.RequestError as e:
        click.echo(f"Connection failed: {e}")
