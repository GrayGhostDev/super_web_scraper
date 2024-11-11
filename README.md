```markdown
# Gray Ghost Data Profile Generator - Setup Guide

## Prerequisites

1. Docker and Docker Compose
2. Python 3.11+
3. Node.js 18+
4. AWS Account (for deployment features)

## Local Development Setup

1. Clone the repository and set up environment:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys and configurations
code .env
```

3. Start required services using Docker Compose:
```bash
docker-compose up -d postgres redis rabbitmq
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the application:
```bash
python -m streamlit run main.py
```

## API Keys Setup

The following API keys are required for full functionality:

- LinkedIn API credentials
- Hunter.io API key
- RocketReach API key
- People Data Labs API key
- LexisNexis API key

Add these to your `.env` file.

## Docker Deployment

To run the entire application stack in Docker:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Accessing the Application

- Main application: http://localhost:8501
- Grafana dashboards: http://localhost:3000
- Prometheus metrics: http://localhost:9090

## Health Check

Verify the application is running correctly:

```bash
curl http://localhost:8501/health
```

## Common Issues

1. Chrome/Selenium Issues:
   - Ensure Chrome is installed
   - Check ChromeDriver compatibility

2. Database Connection Issues:
   - Verify PostgreSQL is running
   - Check database credentials

3. Redis Connection Issues:
   - Verify Redis is running
   - Check Redis connection settings

## Monitoring

1. Access Grafana (default credentials: admin/admin):
   - System metrics
   - API performance
   - Task queue monitoring
   - Error tracking

2. View Prometheus metrics:
   - Application metrics
   - System resources
   - Custom business KPIs

## Development Tools

For development:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black .
isort .
pylint src/
```
```