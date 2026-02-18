import json


class ValidationResult:
    is_valid: bool
    validation_message: str


class Upload:

    def __init__(self, data: dict):
        upload_data = data.get('data', None)
        self._message = data.get('message', None)
        self._message_type = data.get('messageType', None)
        self._message_id = data.get('messageId', '')
        self.data = UploadData(data=upload_data) if upload_data else {}

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, value):
        self._message_type = value

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, value):
        self._message_id = value

    def to_json(self):
        self.data = self.data.to_json()
        return to_json(self.__dict__)

    def data_from(self):
        message = self
        if isinstance(message, str):
            message = json.loads(self)
        if message:
            try:
                return Upload(data=message)
            except Exception as e:
                error = str(e).replace('Upload', 'Invalid parameter,')
                raise TypeError(error)


class UploadData:
    def __init__(self, data: dict):
        self._file_upload_path = data.get('file_upload_path', '')
        self._tdei_project_group_id = data.get('tdei_project_group_id', '')
        self._user_id = data.get('user_id', '')
        self._success = data.get('success', False)
        self._message = data.get('message', '')

    @property
    def file_upload_path(self): return self._file_upload_path

    @file_upload_path.setter
    def file_upload_path(self, value): self._file_upload_path = value

    @property
    def tdei_project_group_id(self): return self._tdei_project_group_id

    @tdei_project_group_id.setter
    def tdei_project_group_id(self, value): self._tdei_project_group_id = value

    @property
    def user_id(self): return self._user_id

    @user_id.setter
    def user_id(self, value): self._user_id = value

    @property
    def success(self): return self._success

    @success.setter
    def success(self, value): self._success = value

    @property
    def message(self): return self._message

    @message.setter
    def message(self, value): self._message = value

    def to_json(self):
        return to_json(self.__dict__)


def remove_underscore(string: str):
    return string if not string.startswith('_') else string[1:]


def to_json(data: object):
    result = {}
    for key in data:
        value = data[key]
        key = remove_underscore(key)
        result[key] = value

    return result
