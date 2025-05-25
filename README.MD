# Lu Estilo API

Backend API for Lu Estilo, a clothing company, to facilitate new sales channels.

## Features

- Authentication with JWT
- Client management
- Product management
- Order management
- WhatsApp integration for customer notifications

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- Alembic for migrations
- SQLAlchemy ORM
- Docker and Docker Compose
- Pytest for testing

## Installation and Setup

### Using Docker

1. Clone the repository
2. Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your-secret-key
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
SENTRY_DSN=your-sentry-dsn
CREATE_DEFAULT_ADMIN=true
```

3. Build and run the application:

```bash
docker-compose up -d
```

4. Run database migrations:

```bash
docker-compose exec api alembic upgrade head
```

### Local Development

1. Clone the repository
2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the required environment variables

5. Run the application:

```bash
uvicorn app.main:app --reload
```

6. Run database migrations:

```bash
alembic upgrade head
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

To run tests:

```bash
pytest
```

## Database Schema

The application uses the following main tables:

- Users: Store user authentication information
- Clients: Store client information
- Products: Store product information
- Orders: Store order information
- OrderItems: Store items within an order

## WhatsApp Integration

The API integrates with WhatsApp Business API to send notifications to customers:

- Order confirmations
- Order status updates
- Promotional messages

To use this feature, you need to:

1. Have a valid WhatsApp Business account
2. Configure the API key and phone number ID in environment variables
3. Ensure client phone numbers are valid and properly formatted

## License

This project is licensed under the MIT License.
