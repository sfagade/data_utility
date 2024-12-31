"""A tool to copy tasks from passes in CS:MOC."""

import click

from .create_records import create


@click.group()
def utility() -> None:
    """Command group"""


@click.group()
def cli() -> None:
    """Command group"""


utility.add_command(create)

cli.add_command(utility)


if __name__ == "__main__":
    cli()
