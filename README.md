# TDEI-python-osw-validation

## Introduction 
Service to Validate the OSW files that is uploaded. At the moment, the service does the following:
- Listens to the topic which is mentioned in `.env` file for any new message (that is triggered when a file is uploaded), example  `UPLOAD_TOPIC=osw-upload` 
- Consumes the message and perform following checks - 
  - Download the file locally 
  - File location is in the message `data.meta.file_upload_path`
  - Uses `python-osw-validation` to validate the file
  - Adds the `isValid` and `validationMessage` keys to the original message 
- Publishes the result to the topic mentioned in `.env` file, example `VALIDATION_TOPIC=osw-validation`

## Getting Started
The project is built on Python with FastAPI framework. All the regular nuances for a Python project are valid for this.

### System requirements
| Software   | Version |
|------------|---------|
| Python     | 3.10.x  |


### Connectivity to cloud
- Connecting this to cloud will need the following in the `.env` file

```bash
PROVIDER=Azure
QUEUECONNECTION=xxxx
STORAGECONNECTION=xxxx
VALIDATION_REQ_TOPIC=xxxx
VALIDATION_REQ_SUB=xxxx
VALIDATION_RES_TOPIC=xxxx
CONTAINER_NAME=xxxx
AUTH_PERMISSION_URL=xxx # This is the URL to get the token
MAX_CONCURRENT_MESSAGES=xxx # Optional if not provided defaults to 2
AUTH_SIMULATE=xxx # Optional if not provided defaults to False
```

The application connect with the `STORAGECONNECTION` string provided in `.env` file and validates downloaded zipfile using `python-osw-validation` package.
`QUEUECONNECTION` is used to send out the messages and listen to messages.

`MAX_CONCURRENT_MESSAGES` is the maximum number of concurrent messages that the service can handle. If not provided, defaults to 2

### How to Set up and Build
Follow the steps to install the python packages required for both building and running the application

1. Setup virtual environment
    ```
    python3.10 -m venv .venv
    source .venv/bin/activate
    ```

2. Install the dependencies. Run the following command in terminal on the same directory as `requirements.txt`
    ```
    # Installing requirements
    pip install -r requirements.txt
    ```
### How to Run the Server/APIs   

1. The http server by default starts with `8000` port
2. Run server
    ```
    uvicorn src.main:app --reload
    ```
3. By default `get` call on `localhost:8000/health` gives a sample response
4. Other routes include a `ping` with get and post. Make `get` or `post` request to `http://localhost:8000/health/ping`
5. Once the server starts, it will start to listening the subscriber(`VALIDATION_REQ_SUB` should be in env file)


#### Request Format
  
```json
  {
    "messageId": "tdei_record_id",
    "messageType": "workflow_identifier",
    "data": {
      "file_upload_path": "file_upload_path",
      "user_id": "user_id",
      "tdei_project_group_id": "tdei_project_group_id"
    } 
  }
```

#### Response Format
  
```json
  {
    "messageId": "tdei_record_id",
    "messageType": "workflow_identifier",
    "data": {
      "file_upload_path": "file_upload_path",
      "user_id": "user_id",
      "tdei_project_group_id": "tdei_project_group_id",
      "success": true/false,
      "message": "message" // if false the error string else empty string
    },
    "publishedDate": "published date"
  }
```


### How to Set up and run the Tests

Make sure you have set up the project properly before running the tests, see above for `How to Setup and Build`.

#### How to run test harness
1. Add the new set of test inside `tests/test_harness/tests.json` file like -
    ```
    {
     "Name": "Test Name",
     "Input_file": "test_files/osw_test_case1.json", // Input file path which you want to provide to the test
     "Result": true/false // Defining the test output 
     }
    ```
2. Test Harness would require a valid `.env` file.
3. To run the test harness `python tests/test_harness/run_tests.py` 
#### How to run unit test cases
1. `.env` file is not required for Unit test cases.
2. To run the unit test cases
   1. `python test_report.py`
   2. Above command will run all test cases and generate the html report, in `reports` folder at the root level.
3. To run the coverage
   1. `python -m coverage run --source=src -m unittest discover -s tests/unit_tests`
   2. Above command will run all the unit test cases.
   3. To generate the coverage report in console
      1. `coverage report`
      2. Above command will generate the code coverage report in terminal. 
   4. To generate the coverage report in html.
      1. `coverage html`
      2. Above command will generate the html report, and generated html would be in `htmlcov` directory at the root level.
   5. _NOTE :_ To run the `html` or `report` coverage, 3.i) command is mandatory

#### How to run integration test cases
1. `.env` file is required for Unit test cases.
2. To run the integration test cases, run the below command
   1. `python test_integration.py`
   2. Above command will run all integration test cases and generate the html report, in `reports` folder at the root level.


### Messaging

This microservice deals with two topics/queues. 
- upload queue from osw-upload
- validation queue from osw-validation


#### Incoming
The incoming messages will be from the upload queue `osw-upload`.
The format is mentioned in [osw-upload.json](./src/assets/osw-upload.json)

#### Outgoing
The outgoing messages will be to the `osw-validation` topic.
The format of the message is at [osw-validation.json](./src/assets/osw-validation.json)


