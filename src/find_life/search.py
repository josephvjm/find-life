from __future__ import annotations

import json as json_mod
import shutil
import textwrap

import click
import httpx

from find_life.init import BASE_URL, ensure_token

_GRAY, _RESET, _BOLD = "\033[37m", "\033[0m", "\033[1m"


def _print_paleo(paleo: dict) -> None:
    first, last = paleo.get("firstAppearance"), paleo.get("lastAppearance")
    if first and last:
        click.echo(f"\n{_BOLD}First appeared:{_RESET} {first} – {last} Ma")


def _print_wikipedia(wikipedia: dict) -> None:
    if wikipedia.get("extract"):
        term_w = shutil.get_terminal_size().columns
        wrapped = textwrap.fill(
            wikipedia["extract"],
            width=term_w,
            initial_indent=f"\n{_BOLD}Wikipedia:{_RESET} ",
            subsequent_indent="           ",
        )
        click.echo(wrapped)
    if wikipedia.get("source"):
        click.echo(f"{_BOLD}Source:{_RESET}    {wikipedia['source']}")


def _print_text(
    taxonomy: dict, wikipedia: dict | None = None, paleo: dict | None = None
) -> None:
    parents = list(reversed(taxonomy.get("parents", [])))
    subject = {"rank": taxonomy["rank"], "name": taxonomy["name"]}
    children = taxonomy.get("children", [])

    click.echo(f"\n{_BOLD}Taxonomy:{_RESET}")

    for i, row in enumerate(parents):
        indent = "  " * i
        branch = "" if i == 0 else "└─ "
        click.echo(f"{_GRAY}{indent}{branch}{row['name']}  ({row['rank']}){_RESET}")

    subject_indent = "  " * len(parents)
    subject_prefix = f"{subject_indent}└─ " if parents else ""
    click.echo(
        f"{_BOLD}{subject_prefix}▶  {subject['name']}  ({subject['rank']}){_RESET}"
    )

    child_indent = "  " * (len(parents) + 1)
    for i, row in enumerate(children):
        branch = "└─" if i == len(children) - 1 else "├─"
        click.echo(f"{child_indent}{branch} {row['name']}  ({row['rank']})")

    if paleo:
        _print_paleo(paleo)
    if wikipedia:
        _print_wikipedia(wikipedia)


def _print_table(
    taxonomy: dict, wikipedia: dict | None = None, paleo: dict | None = None
) -> None:
    rows: list[tuple[str, str, str]] = [
        ("", "Name", taxonomy["name"]),
        ("", "Rank", taxonomy["rank"]),
    ]
    for p in reversed(taxonomy.get("parents", [])):
        rows.append(("Parents", p["rank"], p["name"]))
    for c in taxonomy.get("children", []):
        rows.append(("Children", c["rank"], c["name"]))
    if paleo:
        first, last = paleo.get("firstAppearance"), paleo.get("lastAppearance")
        if first:
            rows.append(("Paleo", "First appearance", f"{first} Ma"))
        if last:
            rows.append(("", "Last appearance", f"{last} Ma"))
    if wikipedia:
        if wikipedia.get("extract"):
            rows.append(("Wikipedia", "Extract", wikipedia["extract"]))
        if wikipedia.get("source"):
            rows.append(("Wikipedia", "Source", wikipedia["source"]))

    sec_w = max(len(r[0]) for r in rows)
    field_w = max(len(r[1]) for r in rows)
    term_w = shutil.get_terminal_size().columns
    value_w = max(term_w - sec_w - field_w - 6, 40)

    click.echo(f"{'Section':<{sec_w}}  {'Field':<{field_w}}  Value")
    click.echo("-" * min(shutil.get_terminal_size().columns, 80))

    prev_section = None
    for section, field, value in rows:
        sec_label = section if section != prev_section else ""
        wrapped = textwrap.wrap(value, width=value_w) or [""]
        click.echo(f"{sec_label:<{sec_w}}  {field:<{field_w}}  {wrapped[0]}")
        indent = " " * (sec_w + field_w + 6)
        for line in wrapped[1:]:
            click.echo(f"{indent}{line}")
        prev_section = section


def run_search(name: str, mode: str | None, output_fmt: str) -> None:
    try:
        token = ensure_token()
    except httpx.RequestError as e:
        click.echo(f"Connection failed: {e}")
        return

    def fetch(action: str) -> dict | None:
        response = httpx.get(
            f"{BASE_URL}/api",
            params={"action": action, "q": name},
            headers={"x-find-life-token": token},
        )
        response.raise_for_status()
        data = response.json()
        return data if data.get("id") else None

    try:
        data = fetch(mode) if mode else (fetch("scientific") or fetch("common"))
        if not data:
            click.echo(f"No results found for {name!r}")
            return
        taxonomy = data.get("taxonomy")
        if not taxonomy:
            click.echo(f"ID: {data['id']}")
            return
        if output_fmt == "json":
            click.echo(
                json_mod.dumps(
                    {
                        "taxonomy": taxonomy,
                        "paleo": data.get("paleo"),
                        "wikipedia": data.get("wikipedia"),
                    },
                    indent=2,
                )
            )
        elif output_fmt == "table":
            _print_table(taxonomy, data.get("wikipedia"), data.get("paleo"))
        else:
            _print_text(taxonomy, data.get("wikipedia"), data.get("paleo"))
    except httpx.HTTPStatusError as e:
        click.echo(f"Request failed: {e.response.status_code} {e.response.text}")
    except httpx.RequestError as e:
        click.echo(f"Connection failed: {e}")
