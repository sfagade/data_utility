import json
import logging
import os
import sys
from typing import Any

import click
import pika
from dotenv import load_dotenv
from faker import Faker

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

    channel = None
    try:
        channel = publish_message_to_exchange(
            username=os.getenv("RABBITMQ_USERNAME"),
            password=os.getenv("RABBITMQ_PASSWORD"),
            exchange_name=os.getenv("EXCHANGE"),
            message_body=[],
            routing_key=model,
            exchange_type="topic",
            port=5672,
            host=os.getenv("RABBITMQ_HOST"),
            durable=True,
        )

        if model == "franchises":
            logger.info("Creating %s Franchises", count)
            for _ in range(count):
                channel.basic_publish(
                    exchange=os.getenv("EXCHANGE"),
                    routing_key=model,
                    body=json.dumps({"franchise_name": faker.company(), "description": faker.sentence()}),
                )
            logger.info("Created %s Franchises", count)
        elif model == "food-types":
            logger.info("Creating %s Food Types", count)
            fake = FoodTypeProvider()
            for _ in range(count):
                channel.basic_publish(
                    exchange=os.getenv("EXCHANGE"),
                    routing_key=model,
                    body=json.dumps({"type_name": fake.dish_type(), "description": faker.sentence()}),
                )
            logger.info("Created %s Food Types", count)
        elif model == "menus":
            logger.info("Creating %s Menus", count)
            for _ in range(count):
                channel.basic_publish(
                    exchange=os.getenv("EXCHANGE"),
                    routing_key=model,
                    body=json.dumps({"menu_name": faker.company(), "description": faker.sentence()}),
                )
            logger.info("Created %s Menus", count)
        else:
            logger.error("Unknown model: %s", model)
    finally:
        if channel is not None:
            channel.close()


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
