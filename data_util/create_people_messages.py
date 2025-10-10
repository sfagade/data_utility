import json
import logging
import os
import sys
import time

import click
import pika
from dotenv import load_dotenv
from faker import Faker

from data_util.connections.rabbit_connection import publish_message_to_exchange
from data_util.providers.FoodTypeProvider import FoodTypeProvider

logger = logging.getLogger(__name__)

# Model type constants
MODEL_PERSON = "people"


def _create_person_message(faker: Faker) -> dict[str, str]:
    """Create a person message body."""
    return {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "date_of_birth": faker.date_of_birth().isoformat(),
        "gender": faker.passport_gender(),
    }


def _publish_messages_for_model(
    channel: pika.channel.Channel,
    model: str,
    count: int,
    faker: Faker,
    exchange: str,
) -> None:
    """Publish messages for a specific model type."""
    if model == MODEL_PERSON:
        logger.info("Creating %s People", count)
        for _ in range(count):
            message = _create_person_message(faker)
            channel.basic_publish(
                exchange=exchange,
                routing_key=model,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent  # Mark message as persistent (delivery_mode=2)
                ),
            )
        logger.info("Created %s People", count)
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
def queue_person_create(model: str, count: int, config_file: str, periodic_run: bool) -> None:
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
            exchange_name=os.getenv("PERSON_EXCHANGE"),
            routing_key=model,
            exchange_type="topic",
            port=5672,
            host=os.getenv("RABBITMQ_HOST"),
            durable=True,
        )

        exchange = os.getenv("PERSON_EXCHANGE")

        if periodic_run:
            for _ in range(count):
                _publish_messages_for_model(channel, model, 10, faker, exchange)
                time.sleep(5)
        else:
            _publish_messages_for_model(channel, model, count, faker, exchange)
    finally:
        if channel is not None:
            channel.close()
