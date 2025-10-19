import json
import logging
import os
import time
from unittest import TestCase, mock
from unittest.mock import MagicMock, call, patch

import pika
from click.testing import CliRunner
from faker import Faker

from data_util.create_reference_message import (
    _create_food_type_message,
    _create_franchise_message,
    _create_menu_message,
    _publish_messages_for_model,
    queue_create,
)
from data_util.providers.FoodTypeProvider import FoodTypeProvider

MODEL_FRANCHISES = "franchises"
MODEL_FOOD_TYPES = "food-types"
MODEL_MENUS = "menus"


class TestCreateReferenceMessage(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.exchange = "test_exchange"
        self.count = 5
        self.channel = mock.Mock()
        self.channel.basic_publish.return_value = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    @patch("data_util.create_reference_message.logger.info")
    def test_publish_messages_for_model_franchises(self, mock_logger_info):
        _publish_messages_for_model(self.channel, MODEL_FRANCHISES, self.count, self.faker, self.exchange)

        self.channel.basic_publish.assert_called()
        self.assertEqual(mock_logger_info.call_count, 2)
        self.assertEqual(
            mock_logger_info.call_args_list,
            [
                call("Creating %s Franchises", self.count),
                call("Created %s Franchises", self.count),
            ],
        )

    @patch("data_util.create_reference_message.logger.info")
    def test_publish_messages_for_model_food_types(self, mock_logger_info):
        food_type_provider = FoodTypeProvider()
        message_body = _create_food_type_message(food_type_provider, self.faker)
        _publish_messages_for_model(
            self.channel,
            MODEL_FOOD_TYPES,
            self.count,
            self.faker,
            self.exchange,
        )

        self.channel.basic_publish.assert_called()
        self.assertEqual(mock_logger_info.call_count, 2)
        self.assertEqual(
            mock_logger_info.call_args_list,
            [
                call("Creating %s Food Types", self.count),
                call("Created %s Food Types", self.count),
            ],
        )

    @patch("data_util.create_reference_message.logger.info")
    def test_publish_messages_for_model_menus(self, mock_logger_info):
        _publish_messages_for_model(self.channel, MODEL_MENUS, self.count, self.faker, self.exchange)

        self.channel.basic_publish.assert_called()
        self.assertEqual(mock_logger_info.call_count, 2)
        self.assertEqual(
            mock_logger_info.call_args_list,
            [call("Creating %s Menus", self.count), call("Created %s Menus", self.count)],
        )

    @patch("data_util.create_reference_message.logger.error")
    def test_publish_messages_for_model_unknown_model(self, mock_logger_info):
        _publish_messages_for_model(self.channel, "unknown_model", self.count, self.faker, self.exchange)

        self.channel.basic_publish.assert_not_called()
        self.assertEqual(
            mock_logger_info.call_args_list,
            [call("Unknown model: %s", "unknown_model")],
        )

    @patch("data_util.create_reference_message.publish_message_to_exchange")
    @patch("data_util.providers.FoodTypeProvider.FoodTypeProvider")
    @patch("data_util.create_reference_message._publish_messages_for_model")
    def test_queue_create_periodic_run(
        self,
        mock_publish_messages_for_model,
        mock_food_type_provider,
        mock_publish_message_to_exchange,
    ):
        # Test case 1: Test that the function publishes messages for the specified model
        mock_publish_message_to_exchange.return_value = MagicMock()
        mock_food_type_provider.return_value = MagicMock()
        mock_publish_messages_for_model.return_value = None

        runner = CliRunner()
        result = runner.invoke(queue_create, ["franchises", "10", "--periodic-run"])
        mock_publish_message_to_exchange.assert_called_once_with(config_file=None)
        mock_publish_messages_for_model.assert_called()
        self.assertEqual(mock_publish_messages_for_model.call_count, 10)

        # time.sleep(1)

    @patch("data_util.create_reference_message.logger.info")
    @patch("data_util.create_reference_message.load_dotenv")
    @patch("data_util.create_reference_message.publish_message_to_exchange")
    @patch("data_util.providers.FoodTypeProvider.FoodTypeProvider")
    @patch("data_util.create_reference_message._publish_messages_for_model")
    def test_queue_create_once(
        self,
        mock_publish_messages_for_model,
        mock_food_type_provider,
        mock_publish_message_to_exchange,
        mock_load_dotenv,
        mock_logger_info,
    ):
        runner = CliRunner()
        result = runner.invoke(queue_create, ["menus", "10"])
        mock_publish_message_to_exchange.assert_called_once_with(config_file=None)
        mock_publish_messages_for_model.assert_called()
        self.assertEqual(mock_publish_messages_for_model.call_count, 1)

        # Test case 3: Test that the function loads environment variables from a config file
        mock_publish_message_to_exchange.reset_mock()
        mock_food_type_provider.reset_mock()
        mock_publish_messages_for_model.reset_mock()
        mock_load_dotenv.return_value = None
        mock_load_dotenv.side_effect = Exception("Test exception")

        result = runner.invoke(queue_create, ["food-type", "15", "-c", "data_util/tests/test_config.env"])
        mock_load_dotenv.assert_called_with("data_util/tests/test_config.env")
        mock_publish_messages_for_model.assert_not_called()
