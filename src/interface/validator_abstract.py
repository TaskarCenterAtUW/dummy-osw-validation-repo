from abc import ABC, abstractmethod
from python_ms_core.core.queue.models.queue_message import QueueMessage


class ValidatorAbstract(ABC):

    @abstractmethod
    def validate(self, message: QueueMessage) -> None:
        pass
