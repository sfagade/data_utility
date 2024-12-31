import logging
import os
import sys

import click
from dotenv import load_dotenv
from faker import Faker

from data_util.model.kantin_models import FoodType, Franchise
from data_util.providers.FoodTypeProvider import FoodTypeProvider

logger = logging.getLogger(__name__)


@click.command()
@click.argument("model", type=str, required=True)
@click.argument("count", type=int, required=True)
@click.option(
    "--config-file",
    "-c",
    default=None,
    help="Choose a config file for database connection.",
)
@click.option(
    "--dry-run/--real-run",
    "-d",
    default=False,
    help="Dry run (Will not persist changes).",
)
def create(model: str, count: int, config_file: str, dry_run: bool) -> None:
    logger.info("Command: %s", " ".join(sys.argv))

    if config_file:
        load_dotenv(config_file)
    else:
        load_dotenv()

    faker = Faker()
    connection_string = os.getenv("DATABASE_URI")
    if model == "food-types":
        logger.info("Creating %s Food Types", count)
        fake = FoodTypeProvider()
        for i in range(count):
            food_type = FoodType(connection_string, type_name=fake.dish_type(), description=faker.sentence())
            food_type.create()

    elif model == "franchises":
        logger.info("Creating %s Franchises", count)
        for i in range(count):
            franchise = Franchise(connection_string, franchise_name=faker.company(), description=faker.sentence())
            franchise.create()

    else:
        logger.info("Unknown model %s", model)
