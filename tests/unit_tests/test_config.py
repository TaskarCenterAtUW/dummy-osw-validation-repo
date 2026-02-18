import os
import unittest
from unittest.mock import patch
from src.config import Settings
import importlib


class TestSettings(unittest.TestCase):

    @patch.dict(os.environ, {
        'AUTH_PERMISSION_URL': 'http://auth-url.com',
        'MAX_CONCURRENT_MESSAGES': '5',
        'AUTH_SIMULATE': 'True'
    }, clear=True)
    def test_settings_with_simulated_auth(self):
        settings = Settings()
        self.assertEqual(settings.app_name, 'python-osw-validation')
        self.assertEqual(settings.auth_permission_url, 'http://auth-url.com')
        self.assertEqual(settings.max_concurrent_messages, 5)
        self.assertEqual(settings.auth_provider, 'Simulated')

    @patch.dict(os.environ, {
        'AUTH_PERMISSION_URL': 'http://auth-url.com',
        'MAX_CONCURRENT_MESSAGES': '10',
        'AUTH_SIMULATE': 'False'
    }, clear=True)
    def test_settings_with_hosted_auth(self):
        settings = Settings()
        self.assertEqual(settings.auth_provider, 'Hosted')

    @patch.dict(os.environ, {
        'AUTH_SIMULATE': 'invalid_value'
    }, clear=True)
    def test_settings_with_invalid_auth_simulate(self):
        settings = Settings()
        self.assertEqual(settings.auth_provider, 'Hosted')

    @patch.dict(os.environ, {'CONTAINER_NAME': 'osw'}, clear=True)
    def test_default_settings(self):
        # Reload config to pick up the patched environment and bypass .env values
        from src import config
        importlib.reload(config)
        settings = config.Settings()
        self.assertEqual(settings.app_name, 'python-osw-validation')
        self.assertEqual(settings.event_bus.container_name, 'osw')
        self.assertIsNone(settings.auth_permission_url)
        self.assertEqual(settings.max_concurrent_messages, 2)


if __name__ == '__main__':
    unittest.main()
