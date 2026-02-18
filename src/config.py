import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class EventBusSettings:
    connection_string: str = os.environ.get('QUEUECONNECTION', None)
    upload_topic: str = os.environ.get('VALIDATION_REQ_TOPIC', None)
    upload_subscription: str = os.environ.get('VALIDATION_REQ_SUB', None)
    validation_topic: str = os.environ.get('VALIDATION_RES_TOPIC', None)
    container_name: str = os.environ.get('CONTAINER_NAME', 'osw')


class Settings(BaseSettings):
    app_name: str = 'python-osw-validation'
    event_bus = EventBusSettings()
    auth_permission_url: str = os.environ.get('AUTH_PERMISSION_URL', None)
    max_concurrent_messages: int = os.environ.get('MAX_CONCURRENT_MESSAGES', 2)

    @property
    def auth_provider(self) -> str:
        is_simulated: str = os.environ.get('AUTH_SIMULATE', 'False')
        if is_simulated.lower() in ('true', 'yes', '1'):
            return 'Simulated'
        elif is_simulated.lower() in ('false', 'no', '0'):
            return 'Hosted'
        else:
            return 'Hosted'
