from __future__ import annotations

import click

from find_life.init import run_init
from find_life.search import run_search


@click.group()
def cli() -> None:
    """find-life: taxonomic name search."""


@cli.command()
@click.argument("name")
@click.option(
    "--scientific",
    "mode",
    flag_value="scientific",
    help="Search scientific names only.",
)
@click.option(
    "--common", "mode", flag_value="common", help="Search vernacular names only."
)
@click.option(
    "-f",
    "--format",
    "output_fmt",
    type=click.Choice(["text", "table", "json"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
def search(name: str, mode: str | None, output_fmt: str) -> None:
    """Search taxonomic units by scientific or common name."""
    run_search(name, mode, output_fmt)


@cli.command()
def init() -> None:
    """Re-run setup: reset API key, change mode, or reconfigure."""
    run_init()


# TODO coming soon!
# @cli.command()
# def suggest() -> None:
#     """Open a pre-filled issue with query context."""
#     click.echo("suggest")
