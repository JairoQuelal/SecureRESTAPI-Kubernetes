# Secure REST API Deployment with Kubernetes

## Overview

This project implements a secure RESTful API with CRUD operations, deployed using Kubernetes. It provides a robust solution for managing courses with advanced security and deployment features.

## Features

- **CRUD Operations:** Perform Create, Read, Update, and Delete actions on a PostgreSQL database
- **Authentication:** Secure JWT-based endpoint protection
- **Rate Limiting:** Prevent excessive API requests using Flask-Limiter
- **Kubernetes Deployment:** Comprehensive deployment configurations with services and volumes
- **Comprehensive Logging:** Detailed tracking of user activities and system errors

## Project Structure

```
FinalProject/
├── app/
│   ├── app.py                 # Flask application core
│   ├── templates/             # HTML templates
│   └── static/                # CSS and JavaScript resources
├── deployment/                # Kubernetes deployment configurations
├── logs/                      # Application log storage
├── .env                       # Environment variable configurations
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependency list
├── README.md                  # Project documentation
└── LICENSE                    # Project licensing information
```

## Local Development Setup

### Prerequisites
- Python 3.8+
- Docker (optional)
- Kubernetes cluster (optional)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/SecureRESTAPI-Kubernetes.git
   cd SecureRESTAPI-Kubernetes
   ```

2. **Configure Environment**
   Create a `.env` file with the following contents:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=admin123
   POSTGRES_DB=courses_db
   SQLALCHEMY_DATABASE_URI=postgresql://postgres:admin123@db:5432/courses_db
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app/app.py
   ```

## Docker Development

1. **Build and Run**
   ```bash
   docker-compose up -d --build
   ```

2. **Access the API**
   Open `http://localhost:5000` in your browser

## Kubernetes Deployment

1. **Apply Configurations**
   ```bash
   kubectl apply -f deployment/
   ```

2. **Verify Deployment**
   ```bash
   kubectl get pods
   kubectl get services
   ```

## API Endpoints

### Authentication
- `POST /login`: User authentication and JWT generation
- `POST /register`: Create a new user account

### Courses
- `POST /courses`: Create a new course (Admin only)
- `GET /courses`: Retrieve all courses

### Health Checks
- `GET /health/liveness`: API liveness probe
- `GET /health/readiness`: API readiness probe

## Example API Requests

### User Login
```bash
curl -X POST http://localhost:5000/login \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "password123"}'
```

### Create a Course
```bash
curl -X POST http://localhost:5000/courses \
-H "Authorization: Bearer <your-jwt-token>" \
-H "Content-Type: application/json" \
-d '{"title": "Python for Beginners", "description": "Learn Python from scratch."}'
```

## Logging and Monitoring

- Request and error logs stored in `logs/api.log`
- Built-in health check endpoints for system monitoring

## Environment Variables

Ensure the following variables are set in your `.env` file:
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `SQLALCHEMY_DATABASE_URI`: Full database connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation

## License

This project is licensed under the MIT License.
