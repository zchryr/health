# Package Repository Checker API

A FastAPI-based service that provides repository information for both Python packages (PyPI) and NPM packages (npmjs.org). This API helps developers quickly access package metadata, repository information, and version details for multiple packages simultaneously.

## Features

- RESTful API endpoints for both PyPI and NPM packages
- Batch processing support for multiple packages
- Extracts detailed package information including:
  - Package summary/description
  - Repository URL and platform (GitHub/GitLab/Bitbucket)
  - Organization and repository names
  - Latest version
  - Creation date
- Version 1.0.0 API with structured response formats
- Error handling for non-existent packages

## Language Support
- [x] Python (PyPi)
- [x] JavaScript (npmjs.org)
- [ ] Java
- [ ] C#
- [ ] PHP
- [ ] C++
- [ ] Go
- [ ] Ruby
- [ ] Kotlin
- [ ] Swift
- [ ] Rust

## API Endpoints

### PyPI Package Endpoints

- `GET /v1/pypi/{package_name}` - Get information for a single PyPI package
- `POST /v1/pypi/batch` - Get information for multiple PyPI packages

### NPM Package Endpoints

- `GET /v1/npm/{package_name}` - Get information for a single NPM package
- `POST /v1/npm/batch` - Get information for multiple NPM packages

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install fastapi uvicorn requests pydantic
```

## Docker Deployment

The application can be deployed using Docker for a secure, isolated environment. The Dockerfile includes several security hardening measures:

- Uses Python 3.12.10 on Alpine Linux for a minimal attack surface
- Runs as a non-root user for enhanced security
- Implements security best practices for Python and pip
- Regular system package updates
- Proper file permissions and ownership

### Building the Docker Image

```bash
docker build -t package-repo-checker .
```

### Running the Container

```bash
docker run -p 8000:8000 package-repo-checker
```

The API will be available at `http://localhost:8000`

### Docker Security Features

The Dockerfile implements several security measures:

1. **Non-root User**: The application runs as a dedicated non-root user `appuser`
2. **Package Updates**: All system packages are updated during build
3. **Python Security Settings**:
   - Disabled Python bytecode generation
   - Enabled better error handling
   - Randomized Python hash seed
4. **Pip Security Settings**:
   - Disabled pip cache
   - Disabled version checks
   - Set reasonable timeouts
5. **File Permissions**: Proper ownership and permissions for application files

### Production Considerations

For production deployments, consider:
- Using Docker secrets for sensitive data
- Implementing rate limiting
- Using HTTPS
- Regular image updates
- Docker Content Trust for image signing

## Development Setup

For development, install the additional development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Running the Application

Start the server with:
```bash
python app.py
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

Example responses for each endpoint can be found in the Response Format section below.

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

View detailed coverage report with missing lines:
```bash
python3 -m pytest --cov=app --cov-report=term-missing test_app.py
```

Generate HTML coverage report:
```bash
python3 -m pytest --cov=app --cov-report=html test_app.py
```
This will create a `htmlcov` directory with an interactive HTML report. Open `htmlcov/index.html` in your browser to view the detailed coverage report.

### Current Test Coverage

The test suite includes:
- Unit tests for utility functions
- API endpoint tests for both PyPI and NPM routes
- Error handling tests
- Repository URL parsing tests

Current coverage: 81%

### Test Structure

- `test_app.py`: Contains all test cases
  - Utility function tests
  - API endpoint tests
  - Mock fixtures for PyPI and NPM responses

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

## Error Handling

- Returns 404 status code for non-existent packages
- Includes error flag in response for failed package lookups in batch requests
- Gracefully handles missing repository information

## Dependencies

- `fastapi`: Web framework for building APIs
- `uvicorn`: ASGI server for running the application
- `requests`: HTTP client for making API requests
- `pydantic`: Data validation and settings management
- Standard library imports for typing and URL parsing

## Contributing

Feel free to submit issues and enhancement requests!