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
Accepts either a repository URL or path string.

**Request Body:**
```json
{
    "repository_url": "https://github.com/owner/repo"  // or
    "repository_path": "owner/repo"
}
```

### GitHub-Specific Endpoint
```
GET /v1/github/{owner}/{repo}
```

### GitLab-Specific Endpoint
```
GET /v1/gitlab/{owner}/{repo}
```

## Example Requests

### Using Repository URL
```bash
# Check a GitHub repository using URL
curl -X POST "http://localhost:8000/v1/check" \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/fastapi-users/fastapi-users"}'

# Check a GitLab repository using URL
curl -X POST "http://localhost:8000/v1/check" \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://gitlab.com/gitlab-org/gitlab"}'
```

### Using Repository Path
```bash
# Check a GitHub repository using path
curl -X POST "http://localhost:8000/v1/check" \
     -H "Content-Type: application/json" \
     -d '{"repository_path": "fastapi-users/fastapi-users"}'

# Check a GitLab repository using path
curl -X POST "http://localhost:8000/v1/check" \
     -H "Content-Type: application/json" \
     -d '{"repository_path": "gitlab-org/gitlab"}'
```

### Direct Platform Endpoints
```bash
# Check GitHub repository directly
curl "http://localhost:8000/v1/github/fastapi-users/fastapi-users"

# Check GitLab repository directly
curl "http://localhost:8000/v1/gitlab/gitlab-org/gitlab"
```

## Response Format

```json
{
    "results": [
        {
            "repository_url": "string",
            "platform": "string",
            "owner": "string",
            "repo_name": "string",
            "last_activity": "string",
            "days_since_last_activity": "integer",
            "open_issues_count": "integer",
            "stars_count": "integer",
            "forks_count": "integer",
            "has_readme": "boolean",
            "has_license": "boolean",
            "warnings": ["string"],
            "errors": ["string"],
            "is_healthy": "boolean"
        }
    ]
}
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd repo-health-check-api
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

## Running the API

Start the server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.