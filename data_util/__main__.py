"""A tool to copy tasks from passes in CS:MOC."""

import click

from data_util.create_people_messages import queue_person_create
from data_util.create_queue_records import queue_create

from .create_db_records import db_create


@click.group()
def utility() -> None:
    """Command group"""


@click.group()
def cli() -> None:
    """Command group"""


utility.add_command(db_create)
utility.add_command(queue_create)
utility.add_command(queue_person_create)

cli.add_command(utility)


if __name__ == "__main__":
    cli()
