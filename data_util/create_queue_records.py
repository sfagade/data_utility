import json
import logging
import os
import sys
import time
from typing import Any

import click
import pika
from dotenv import load_dotenv
from faker import Faker

from data_util.providers.FoodTypeProvider import FoodTypeProvider

logger = logging.getLogger(__name__)

# Model type constants
MODEL_FRANCHISES = "franchises"
MODEL_FOOD_TYPES = "food-types"
MODEL_MENUS = "menus"


def _create_person_message(faker: Faker) -> dict[str, str]:
    """Create a person message body."""
    return {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "date_of_birth": faker.date_of_birth().isoformat(),
        "gender": faker.passport_gender(),
    }


def _create_franchise_message(faker: Faker) -> dict[str, str]:
    """Create a franchise message body."""
    return {"franchise_name": faker.company(), "description": faker.sentence()}


def _create_food_type_message(food_type_provider: FoodTypeProvider, faker: Faker) -> dict[str, str]:
    """Create a food type message body."""
    return {"type_name": food_type_provider.dish_type(), "description": faker.sentence()}


def _create_menu_message(faker: Faker) -> dict[str, str]:
    """Create a menu message body."""
    return {"menu_name": faker.company(), "description": faker.sentence()}


def _publish_messages_for_model(
    channel: pika.channel.Channel,
    model: str,
    count: int,
    faker: Faker,
    exchange: str,
) -> None:
    """Publish messages for a specific model type."""
    if model == MODEL_FRANCHISES:
        logger.info("Creating %s Franchises", count)
        for _ in range(count):
            message = _create_franchise_message(faker)
            channel.basic_publish(
                exchange=exchange,
                routing_key=model,
                body=json.dumps(message),
            )
        logger.info("Created %s Franchises", count)
    elif model == MODEL_FOOD_TYPES:
        logger.info("Creating %s Food Types", count)
        food_type_provider = FoodTypeProvider()
        for _ in range(count):
            message = _create_food_type_message(food_type_provider, faker)
            channel.basic_publish(
                exchange=exchange,
                routing_key=model,
                body=json.dumps(message),
            )
        logger.info("Created %s Food Types", count)
    elif model == MODEL_MENUS:
        logger.info("Creating %s Menus", count)
        for _ in range(count):
            message = _create_menu_message(faker)
            channel.basic_publish(
                exchange=exchange,
                routing_key=model,
                body=json.dumps(message),
            )
        logger.info("Created %s Menus", count)
    else:
        logger.error("Unknown model: %s", model)


@click.command()
@click.argument("model", type=str, required=True)
@click.argument("count", type=int, required=True)
@click.option(
    "--config-file",
    "-c",
    default=None,
    help="Choose a config file to load environment variables from.",
)
@click.option(
    "--periodic-run/--real-run",
    "-p",
    default=False,
    help="When true messages are sent periodically for the number of count.",
)
def queue_create(model: str, count: int, config_file: str, periodic_run: bool) -> None:
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

        exchange = os.getenv("EXCHANGE")

        if periodic_run:
            for _ in range(count):
                _publish_messages_for_model(channel, model, 10, faker, exchange)
                time.sleep(5)
        else:
            _publish_messages_for_model(channel, model, count, faker, exchange)
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
    if len(message_body) > 0:
        channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(message_body))
    return channel
