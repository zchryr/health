# Repository Health Check API

A FastAPI-based REST API that performs comprehensive health checks on public software repositories. The API supports both GitHub and GitLab repositories, providing detailed insights into repository health metrics.

## Features

- **Multi-Platform Support**
  - GitHub repositories
  - GitLab repositories

- **Authentication**
  - Built-in GitHub Personal Access Token support
  - Built-in GitLab Personal Access Token support
  - Automatic token management via environment variables

- **Health Check Metrics**
  - Last activity tracking with warning thresholds
  - Open issues count
  - Stars and forks count
  - README file presence check
  - LICENSE file presence check
  - Comprehensive warning and error reporting

## API Endpoints

### Universal Check Endpoint
```
POST /v1/check
```
Accepts either a repository URL or path string in the JSON body.

### Batch Check Endpoint
```
POST /v1/check/batch
```
Check the health of multiple repositories in a single request.

### GitHub-Specific Endpoint
```
GET /v1/github/{owner}/{repo}
```
Check a GitHub repository directly by owner and repo name.

### GitLab-Specific Endpoint
```
GET /v1/gitlab/{owner}/{repo}
```
Check a GitLab repository directly by owner/namespace and repo/project name.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zchryr/health.git
cd health/repo-health-check-api
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

Current coverage: 51%

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

### Universal Check Example
```bash
curl -X POST "http://localhost:8000/v1/check" \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/fastapi-users/fastapi-users"}'
```

### Batch Check Example
```bash
curl -X POST "http://localhost:8000/v1/check/batch" \
     -H "Content-Type: application/json" \
     -d '{
           "repos": [
             {"repository_url": "https://github.com/fastapi-users/fastapi-users"},
             {"repository_path": "gnachman/iterm2"},
             {"repository_url": "https://gitlab.com/gitlab-org/gitlab"}
           ]
         }'
```

### GitHub Check Example
```bash
curl "http://localhost:8000/v1/github/fastapi-users/fastapi-users"
```

### GitLab Check Example
```bash
curl "http://localhost:8000/v1/gitlab/gnachman/iterm2"
```

## Docker Deployment

The application can be deployed using Docker for a secure, isolated environment.

### Building the Docker Image

```bash
docker build -t repo-health-checker .
```

### Running the Container

```bash
docker run -p 8000:8000 repo-health-checker
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

## Response Format

Example response:
```json
{
  "results": [
    {
      "repository_url": "https://gitlab.com/gnachman/iterm2",
      "platform": "gitlab",
      "owner": "gnachman",
      "repo_name": "iterm2",
      "last_activity": "2025-05-12T18:33:05.118Z",
      "days_since_last_activity": 0,
      "open_issues_count": 20,
      "stars_count": 1456,
      "forks_count": 187,
      "has_readme": true,
      "has_license": true,
      "warnings": [],
      "errors": [],
      "is_healthy": true
    }
  ]
}
```

## Authentication Setup

### GitHub Authentication

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select the following scopes:
     - `repo` (Full control of private repositories)
     - `read:org` (Read organization data)
   - Copy the generated token

### GitLab Authentication

1. Create a GitLab Personal Access Token:
   - Go to GitLab Settings → Access Tokens
   - Create a new token with the following scopes:
     - `read_api` (Read API access)
     - `read_repository` (Read repository access)
   - Copy the generated token

### Setting Up Environment Variables

1. Create a `.env` file in the project root:
   ```bash
   GITHUB_TOKEN=your_github_token
   GITLAB_TOKEN=your_gitlab_token
   ```

2. The API will automatically load these tokens when started.

Note: Add `.env` to your `.gitignore` file to prevent committing sensitive tokens.

## Health Check Thresholds

The API uses the following thresholds for warnings:
- Repository inactivity > 90 days: Warning
- Repository inactivity > 365 days: Critical warning
- Missing README file: Warning
- Missing LICENSE file: Warning

## Error Handling

The API provides detailed error messages for:
- Invalid repository URLs or paths
- API request failures
- Authentication issues
- Rate limiting (when using tokens)

## Dependencies

- `fastapi`: Web framework for building APIs
- `uvicorn`: ASGI server for running the application
- `requests`: HTTP client for making API requests
- `pydantic`: Data validation and settings management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.