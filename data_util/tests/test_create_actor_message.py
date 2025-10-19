import json
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, call, patch

import pika
from click.testing import CliRunner
from faker import Faker

from data_util.create_actor_messages import (
    _create_person_message,
    _publish_messages_for_model,
    queue_person_create,
)


class TestPublishMessagesForModel(unittest.TestCase):
    def setUp(self):
        self.channel = MagicMock()
        self.faker = Faker()
        self.exchange = "test_exchange"
        self.count = 5
        self.model = "people"

    @patch("data_util.create_actor_messages.logger.info")
    def test_publish_messages_for_person_model(self, mock_logger_info):
        _publish_messages_for_model(self.channel, self.model, self.count, self.faker, self.exchange)
        self.channel.basic_publish.assert_called()
        self.assertEqual(self.channel.basic_publish.call_count, self.count)
        self.assertEqual(mock_logger_info.call_count, 2)

        self.assertEqual(
            mock_logger_info.call_args_list,
            [
                call("Creating %s People", self.count),
                call("Created %s People", self.count),
            ],
        )

    @patch("data_util.create_actor_messages.logger")
    def test_unknown_model(self, mock_logger):
        _publish_messages_for_model(self.channel, "unknown_model", self.count, self.faker, self.exchange)
        mock_logger.error.assert_called_with("Unknown model: %s", "unknown_model")

    @patch("data_util.create_actor_messages.publish_message_to_exchange")
    @patch("data_util.create_actor_messages._publish_messages_for_model")
    def test_queue_person_periodic_create(
        self,
        mock_publish_messages_for_model,
        mock_publish_message_to_exchange,
    ):
        # Test case 1: Test that the function publishes messages for the specified model
        mock_publish_message_to_exchange.return_value = MagicMock()
        mock_publish_messages_for_model.return_value = None

        runner = CliRunner()
        result = runner.invoke(queue_person_create, ["people", "10", "--periodic-run"])
        mock_publish_message_to_exchange.assert_called_once_with(config_file=None)
        mock_publish_messages_for_model.assert_called()

    @patch("data_util.create_actor_messages.publish_message_to_exchange")
    @patch("data_util.create_actor_messages._publish_messages_for_model")
    def test_queue_person_once_create(
        self,
        mock_publish_messages_for_model,
        mock_publish_message_to_exchange,
    ):
        # Test case 2: Test that the function publishes messages once when --periodic-run is False
        mock_publish_messages_for_model.return_value = None

        runner = CliRunner()
        result = runner.invoke(queue_person_create, ["people", "5"])
        mock_publish_message_to_exchange.assert_called_once_with(config_file=None)
        mock_publish_messages_for_model.assert_called()

    @patch("data_util.create_actor_messages.logger.info")
    @patch("data_util.create_actor_messages.load_dotenv")
    @patch("data_util.create_actor_messages.publish_message_to_exchange")
    @patch("data_util.create_actor_messages._publish_messages_for_model")
    def test_queue_person_env_create(
        self,
        mock_publish_messages_for_model,
        mock_publish_message_to_exchange,
        mock_load_dotenv,
        mock_logger_info,
    ):
        # Test case 3: Test that the function loads environment variables from a config file
        mock_publish_message_to_exchange.reset_mock()
        mock_publish_messages_for_model.reset_mock()
        mock_load_dotenv.return_value = None
        mock_load_dotenv.side_effect = Exception("Test exception")

        runner = CliRunner()
        result = runner.invoke(queue_person_create, ["people", "15", "-c", "test_config.env"])
        mock_load_dotenv.assert_called_once_with("test_config.env")

        mock_publish_messages_for_model.assert_not_called()
        # Test case 4: Test that the function logs the command
        mock_publish_message_to_exchange.reset_mock()
        mock_publish_messages_for_model.reset_mock()
        mock_logger_info.reset_mock()

        runner = CliRunner()
        result = runner.invoke(queue_person_create, ["people", "10"])
        mock_logger_info.assert_called_once_with("Command: %s", " ".join(sys.argv))


if __name__ == "__main__":
    unittest.main()
