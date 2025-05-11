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