import unittest
from abc import ABC
from unittest.mock import MagicMock
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.interface.validator_abstract import ValidatorAbstract


# A concrete implementation of ValidatorAbstract for testing
class ConcreteValidator(ValidatorAbstract):
    def validate(self, message: QueueMessage) -> None:
        # Example implementation: Simply pass for testing purposes
        pass


class TestValidatorAbstract(unittest.TestCase):

    def test_abstract_method_enforcement(self):
        # Ensure that ValidatorAbstract cannot be instantiated directly
        with self.assertRaises(TypeError):
            ValidatorAbstract()

    def test_concrete_validator_instance(self):
        # Ensure a concrete class can be instantiated and implements `validate`
        validator = ConcreteValidator()
        self.assertIsInstance(validator, ValidatorAbstract)

    def test_validate_method_called(self):
        # Mock a QueueMessage object
        message = MagicMock(spec=QueueMessage)

        # Create an instance of the concrete validator
        validator = ConcreteValidator()

        # Call the validate method and ensure it executes without error
        validator.validate(message)

        # Assert that the mocked message object is a valid argument
        self.assertTrue(hasattr(message, '__class__'))


if __name__ == '__main__':
    unittest.main()
