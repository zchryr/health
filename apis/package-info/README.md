# Package Repository Checker API

A FastAPI-based service that provides repository information for both Python packages (PyPI) and NPM packages (npmjs.org). This API helps developers quickly access package metadata, repository information, and version details for multiple packages simultaneously.

## Features

- **Multi-Platform Support**
  - Python packages (PyPI)
  - JavaScript packages (npmjs.org)
  - Planned support for Java, C#, PHP, C++, Go, Ruby, Kotlin, Swift, and Rust

- **Package Information**
  - Package summary/description
  - Repository URL and platform (GitHub/GitLab/Bitbucket)
  - Organization and repository names
  - Latest version
  - Creation date

- **API Features**
  - RESTful API endpoints for both PyPI and NPM packages
  - Batch processing support for multiple packages
  - Version 1.0.0 API with structured response formats
  - Error handling for non-existent packages

## API Endpoints

### PyPI Package Endpoints

- `GET /v1/pypi/{package_name}` - Get information for a single PyPI package
- `POST /v1/pypi/batch` - Get information for multiple PyPI packages

### NPM Package Endpoints

- `GET /v1/npm/{package_name}` - Get information for a single NPM package
- `POST /v1/npm/batch` - Get information for multiple NPM packages

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zchryr/health.git
cd health/package-info-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Examples

### PyPI Package Examples

Get information for a single PyPI package:
```bash
curl http://localhost:8000/v1/pypi/requests
```

Get information for multiple PyPI packages:
```bash
curl -X POST http://localhost:8000/v1/pypi/batch \
  -H "Content-Type: application/json" \
  -d '["requests", "fastapi", "pytest"]'
```

### NPM Package Examples

Get information for a single NPM package:
```bash
curl http://localhost:8000/v1/npm/express
```

Get information for multiple NPM packages:
```bash
curl -X POST http://localhost:8000/v1/npm/batch \
  -H "Content-Type: application/json" \
  -d '["express", "react", "typescript"]'
```

## Response Format

### Single Package Response
```json
{
    "name": "package-name",
    "summary": "Package description",
    "repository_url": "https://github.com/org/repo",
    "repository_platform": "github",
    "repository_org": "org",
    "repository_name": "repo",
    "latest_version": "1.0.0",
    "created_date": "2020-01-01T00:00:00Z",
    "error": false
}
```

### Batch Response
```json
{
    "packages": [
        {
            "name": "package1",
            ...
        },
        {
            "name": "package2",
            ...
        }
    ]
}
```

## Docker Deployment

The application can be deployed using Docker for a secure, isolated environment.

### Building the Docker Image

```bash
docker build -t package-repo-checker .
```

### Running the Container

```bash
docker run -p 8000:8000 package-repo-checker
```

### Docker Security Features

- Uses Python 3.12.10 on Alpine Linux
- Runs as non-root user
- Implements security best practices
- Regular system package updates
- Proper file permissions and ownership

### Production Considerations

- Use Docker secrets for sensitive data
- Implement rate limiting
- Use HTTPS
- Regular image updates
- Docker Content Trust for image signing

## Development Setup

For development, install the additional development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Testing

The project uses pytest for testing and pytest-cov for coverage reporting.

### Running Tests

Run all tests:
```bash
python3 -m pytest test_app.py
```

### Test Coverage

View test coverage report:
```bash
python3 -m pytest --cov=app test_app.py
```

Generate HTML coverage report:
```bash
python3 -m pytest --cov=app --cov-report=html test_app.py
```

Current coverage: 81%

## Error Handling

- Returns 404 status code for non-existent packages
- Includes error flag in response for failed package lookups in batch requests
- Gracefully handles missing repository information

## Dependencies

- `fastapi`: Web framework for building APIs
- `uvicorn`: ASGI server for running the application
- `requests`: HTTP client for making API requests
- `pydantic`: Data validation and settings management

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.