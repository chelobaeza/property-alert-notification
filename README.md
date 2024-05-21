# property-alert-notification

Real estate company challenge.



## Architecture

![Microservice architecture](/docs/alert-notification.drawio.png "Microservice architecture")

This microservice expose a REST API that will use to receive and store user preferences and also schedule user notifications from other microservices. All necessary information will be stored on its own relational database.
Scheduled notifications are stored into a task management queue (RabbitMQ) to decouple the API from the actual notification process with an asynchronous communication, both the API and the notification process can scale independantly.
User specific information should be consumed from the corresponding User microservice API.

## Technology stack

- **FastAPI**. Fast and simple to build REST APIs, has its own dependency injection mechanism and of course is async capable.
- **SQLModel**. ORM for simple, maintainable, and robust communication to the database.
- **SQLite**. Simple relational database for develpment use. Async supported using `aiosqlite` driver.
- **RabbitMQ**. Well-known queue managment system used with `aio_pika` for async support.

## Limitations & Improvements

- Even though we can spawn more workers to scale horizontally, notifications and users can be very dynamic models that could scale tons of times. Building something with autoscaling would be beneficial for optimize resource utilization. Possible solution could be moving to SQS and Lambda functions.
- Alembic or similar package should be used for managing database schema changes with Migrations.
- POST /notifications body is accepting `user_email` and `user_phone_number` for simplicity (and without validation), it should be fetching these data from the corresponding microservice.
- Add more tests.
- There is some duplicated ORM-specific code that can be refactored into a single layer of abstraction
- Dockerize the whole service for development agility

## Quickstart

- Install runtime dependencies and test dependencies in editable mode (-e)
```bash
pip install -e .[test]
```

- Create `.env` file in the root. This will load the needed Env variables.
```bash
cp .env-sample .env
```

- Run docker compose to start RabbitMQ instance
```bash
docker compose up -d
```

- Run the application in development mode
```bash
fastapi dev src/property_alert_notification/main.py
```
The API is now serving in `http://127.0.0.1:8000`
And  the documentation can be accesed at `http://127.0.0.1:8000/docs`

**Note**: a consumer worker will be running on background within the same event loop of the app, only for "local" environment 


- Start consumer workers as needed in different process (Optional).
```bash
python src/property_alert_notification/notification_worker/worker.py
```

## Tests

Run tests with pytest
```bash
pytest
```
append `-vvv` flag to see a more verbose output of the errors.

Pytest will collect tests automatically. To customize the execution check the `[tool.pytest.ini_options]` table in `pyproject.toml`

## Walkthrough

Short guide on how to see the app working.

After the [Quickstart](#quickstart) and having all running, open the API Swagger on the browser http://localhost:8000/docs or just use the curl commands.

1.  Create a user preference for the `user_id=1`.
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/preferences/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email_enabled": true,
  "sms_enabled": true
}'
```

2.  Get preferences for `user_id=1` and verify that the preferences are what you sent.
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/preferences/1' \
  -H 'accept: application/json'
```

3.  Schedule a notification for the `user_id=1`
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/notifications/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "notification title",
  "message": "notification message",
  "user_id": 1,
  "user_email": "user@test.com",
  "user_phone_number": "1231233"
}'
```
At this point you should be seeing the following console output
```
INFO:property_alert_notification.adapters.queue:Message sended.
INFO:     127.0.0.1:44426 - "POST /api/v1/notifications/ HTTP/1.1" 200 OK
INFO:property_alert_notification.adapters.queue:message consumed
Email Hander executed with user@test.com
SMS Hander executed with 1231233
```

4.  Repeat the previous steps using different preferences for a different user. The corresponding handler should notify.

## API Documentation

Openapi docs can be found in [openapi.json](docs/openapi.json).
Swagger is also available in `http://127.0.0.1:8000/docs` after starting the app.


