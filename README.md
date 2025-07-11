# 🌌 Django NTD Demo - Star Wars Planets API

A comprehensive Django-based microservices application for managing Star Wars planets data with real-time analytics, event streaming, and monitoring capabilities.

## 🚀 Features

- **RESTful API** for CRUD operations on Star Wars planets
- **Event-driven architecture** with Kafka for real-time data streaming
- **Asynchronous task processing** using Celery with Redis
- **Real-time analytics** and event consumption
- **Comprehensive monitoring** with Prometheus, Grafana, and ELK stack
- **Circuit breaker pattern** for resilience
- **OpenAPI documentation** with Swagger UI
- **Comprehensive testing** with pytest and coverage reporting

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django API    │───▶│     Kafka       │───▶│   Analytics     │
│   (Planets)     │    │   (Events)      │    │   Consumer      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Monitoring    │
│   (Database)    │    │ (Cache/Broker)  │    │ (Prometheus)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Django 5.x, Django REST Framework
- **Database**: PostgreSQL 16
- **Message Broker**: Apache Kafka + Zookeeper
- **Cache & Task Queue**: Redis + Celery
- **Monitoring**: Prometheus, Grafana, ELK Stack (Elasticsearch, Logstash, Kibana)
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest, coverage
- **Code Quality**: flake8, pre-commit hooks

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd django-NTD-demo
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Update database credentials, secret keys, etc.
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
```

### 4. Initialize Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

```

## 🌐 Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Django API | http://localhost:8000 | Main API endpoints |
| API Documentation | http://localhost:8000/api/schema/swagger-ui/ | Swagger UI |
| Flower (Celery) | http://localhost:5555 | Task monitoring |
| Prometheus | http://localhost:9090 | Metrics collection |
| Grafana | http://localhost:3000 | Dashboards (admin/grafana123) |
| Kibana | http://localhost:5601 | Log visualization |

## 📚 API Endpoints

### Planets API
- `GET /api/planets/` - List all planets
- `POST /api/planets/` - Create a new planet
- `GET /api/planets/{id}/` - Get planet details
- `PUT /api/planets/{id}/` - Update planet
- `DELETE /api/planets/{id}/` - Delete planet

### Analytics API
- `GET /api/analytics/event-stats/` - Get event statistics

## 🧪 Testing

### Run All Tests
```bash

# Local testing
pip install -r requirements.txt
pip install -r requirements.dev.txt

pytest --cov=app --cov-branch
```

### Run Specific Tests
```bash
# Unit tests only
pytest planets/tests/

# E2E tests
pytest e2e_tests/

# With coverage report
pytest --cov=app --cov-report=html
```

## 📊 Monitoring & Observability

### Metrics
- **Application metrics**: Django-prometheus integration
- **Infrastructure metrics**: Redis, PostgreSQL exporters
- **Custom metrics**: Business logic metrics

### Logging
- **Structured logging**: JSON format with python-json-logger
- **Centralized logs**: ELK stack integration
- **Log shipping**: Logstash TCP handler

### Dashboards
Access Grafana at http://localhost:3000 with:
- Username: `admin`
- Password: `grafana123`

## 🔄 Event Streaming

The application uses Kafka for event-driven architecture:

1. **Planet events** are published when planets are created/updated
2. **Analytics consumer** processes events in real-time
3. **Event statistics** are stored and exposed via API

## 🐳 Docker Services

| Service | Description | Health Check |
|---------|-------------|--------------|
| web | Django application (Gunicorn) | HTTP endpoint |
| postgres | PostgreSQL database | pg_isready |
| redis | Redis cache/broker | redis-cli ping |
| kafka | Kafka message broker | broker-api-versions |
| celery | Celery worker | celery inspect ping |
| analytics_consumer | Kafka consumer | Process monitoring |

## 🔧 Configuration

### Environment Variables
Key environment variables (see `.env.example`):
- `DJANGO_SETTINGS_MODULE`: Django app setting
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `POSTGRES_*`: Database configuration
- `CELERY_*`: Task queue configuration
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka brokers

### Scaling
```bash
# Scale specific services
docker-compose up -d --scale celery=3
docker-compose up -d --scale analytics_consumer=2
```

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker daemon and port conflicts
2. **Database connection errors**: Verify PostgreSQL is healthy
3. **Kafka connection issues**: Ensure Zookeeper is running first
4. **Permission errors**: Check file permissions and Docker user

### Useful Commands
```bash
# View service logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart [service-name]

# Clean up
docker-compose down -v
docker system prune -f
```
