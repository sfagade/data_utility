import os

import pika
from dotenv import load_dotenv


def publish_message_to_exchange(config_file: str = None) -> pika.channel.Channel:
    """
    Establish a connection to a RabbitMQ server and declare an exchange.

    Parameters:
    config_file (str): The path to a .env file containing environment variables for the RabbitMQ server.

    Returns:
    pika.channel.Channel: The channel object used for publishing messages to the exchange.
    """
    if config_file:
        load_dotenv(config_file)
    else:
        load_dotenv()

    username = (os.getenv("RABBITMQ_USERNAME"))
    password = (os.getenv("RABBITMQ_PASSWORD"))
    exchange_name = (os.getenv("ACTOR_EXCHANGE"))
    exchange_type = "topic"
    port = 5672
    host = os.getenv("RABBITMQ_HOST")
    durable = True,

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)
    return channel
