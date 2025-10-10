import pika


def publish_message_to_exchange(
    username: str,
    password: str,
    exchange_name: str,
    routing_key: str,
    host: str,
    port: int,
    exchange_type: str,
    durable: bool,
) -> pika.channel.Channel:
    """
    Establish a RabbitMQ connection and declare an exchange.

    Args:
        username: RabbitMQ username
        password: RabbitMQ password
        exchange_name: Name of the exchange to declare
        routing_key: Routing key (reserved for future use)
        host: RabbitMQ host address
        port: RabbitMQ port number
        exchange_type: Type of exchange (e.g., 'topic', 'direct', 'fanout')
        durable: Whether the exchange should survive broker restarts

    Returns:
        Channel object for publishing messages
    """
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
