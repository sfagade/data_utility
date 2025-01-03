import json
import logging
import os
import sys
from typing import Any

import click
import pika
from dotenv import load_dotenv
from faker import Faker

from data_util.model.kantin_models import FoodType, Franchise, Menu
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
def queue_create(model: str, count: int, config_file: str, dry_run: bool) -> None:
    logger.info("Command: %s", " ".join(sys.argv))

    if config_file:
        load_dotenv(config_file)
    else:
        load_dotenv()

    faker = Faker()

    if model == "franchises":
        franchise = []
        logger.info("Creating %s Franchises", count)
        for _ in range(count):
            franchise.append({"franchise_name": faker.company(), "description": faker.sentence()})
            publish_message_to_exchange(
                username=os.getenv("RABBITMQ_USERNAME"),
                password=os.getenv("RABBITMQ_PASSWORD"),
                exchange_name=os.getenv("EXCHANGE"),
                message_body=franchise,
                routing_key="franchises",
                exchange_type="direct",
                port=5672,
                host=os.getenv("RABBITMQ_HOST"),
                durable=True,
            )
        logger.info("Created %s Franchises", count)
    elif model == "food-types":
        logger.info("Creating %s Food Types", count)
        fake = FoodTypeProvider()
        food_types = []
        for _ in range(count):
            food_types.append({"type_name": fake.dish_type(), "description": faker.sentence()})
            publish_message_to_exchange(
                username=os.getenv("RABBITMQ_USERNAME"),
                password=os.getenv("RABBITMQ_PASSWORD"),
                exchange_name=os.getenv("EXCHANGE"),
                message_body=food_types,
                routing_key="food-types",
                exchange_type="direct",
                port=5672,
                host=os.getenv("RABBITMQ_HOST"),
                durable=True,
            )
        logger.info("Created %s Food Types", count)
    elif model == "menus":
        logger.info("Creating %s Menus", count)
        menus = []
        for _ in range(count):
            menus.append({"menu_name": faker.company(), "description": faker.sentence()})
            publish_message_to_exchange(
                username=os.getenv("RABBITMQ_USERNAME"),
                password=os.getenv("RABBITMQ_PASSWORD"),
                exchange_name=os.getenv("EXCHANGE"),
                message_body=menus,
                routing_key="menus",
                exchange_type="direct",
                port=5672,
                host=os.getenv("RABBITMQ_HOST"),
                durable=True,
            )
        logger.info("Created %s Menus", count)
    else:
        logger.error("Unknown model: %s", model)


def publish_message_to_exchange(
    username: str,
    password: str,
    exchange_name: str,
    message_body: list[Any],
    routing_key: str,
    **kw: Any,
) -> pika.channel.Channel:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=kw.get("host"),
            port=kw.get("port"),
            credentials=pika.PlainCredentials(username, password),
        )
    )

    # Create a channel
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type=kw.get("exchange_type"), durable=kw.get("durable"))

    channel.basic_publish(exchange=os.getenv("EXCHANGE"), routing_key=routing_key, body=json.dumps(message_body))
    return channel
