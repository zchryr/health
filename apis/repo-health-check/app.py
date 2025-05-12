from fastapi import FastAPI, HTTPException, APIRouter
from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timezone
import requests
from urllib.parse import urlparse
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get tokens from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')

# Constants
GITHUB_API_BASE = "https://api.github.com"
GITLAB_API_BASE = "https://gitlab.com/api/v4"
README_FILES = ["README.md", "README.rst", "README.txt", "README"]
LICENSE_FILES = ["LICENSE", "LICENSE.md", "COPYING", "COPYING.md"]

def parse_iso8601_timestamp(timestamp: str) -> datetime:
    """
    Parse an ISO 8601 timestamp string into a timezone-aware datetime object.
    Handles both GitHub and GitLab timestamp formats.
    """
    try:
        # Try parsing with microseconds (GitLab format)
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # Try parsing without microseconds (GitHub format)
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 timestamp format: {timestamp}")

    # Make the datetime timezone-aware
    return dt.replace(tzinfo=timezone.utc)

def format_iso8601_timestamp(dt: datetime) -> str:
    """
    Format a datetime object into an ISO 8601 timestamp string.
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

# Create the main FastAPI app
app = FastAPI(
    title="Repository Health Checker",
    description="API to perform health checks on GitHub and GitLab repositories",
    version="1.0.0"
)

# Create a router for v1
v1_router = APIRouter(prefix="/v1")

# Create routers for platform endpoints
github_router = APIRouter(prefix="/github")
gitlab_router = APIRouter(prefix="/gitlab")

class HealthCheckResult(BaseModel):
    repository_url: str
    platform: str
    owner: str
    repo_name: str
    last_activity: Optional[str] = None
    days_since_last_activity: Optional[int] = None
    open_issues_count: Optional[int] = None
    stars_count: Optional[int] = None
    forks_count: Optional[int] = None
    has_readme: bool = False
    has_license: bool = False
    warnings: List[str] = []
    errors: List[str] = []
    is_healthy: bool = True

class HealthCheckResponse(BaseModel):
    results: List[HealthCheckResult]

class RepoCheckRequest(BaseModel):
    repository_url: Optional[str] = None
    repository_path: Optional[str] = None

class RepoBatchCheckRequest(BaseModel):
    repos: List[RepoCheckRequest]

def get_github_headers(token: Optional[str] = None) -> Dict[str, str]:
    """
    Get headers for GitHub API requests.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def get_gitlab_headers(token: Optional[str] = None) -> Dict[str, str]:
    """
    Get headers for GitLab API requests.
    """
    headers = {}
    if token:
        headers["PRIVATE-TOKEN"] = token
    return headers

def check_github_health(owner: str, repo: str, token: Optional[str] = None) -> HealthCheckResult:
    """
    Perform health checks on a GitHub repository.
    """
    headers = get_github_headers(token)
    result = HealthCheckResult(
        repository_url=f"https://github.com/{owner}/{repo}",
        platform="github",
        owner=owner,
        repo_name=repo
    )

    try:
        # Get repository info
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        repo_response = requests.get(repo_url, headers=headers)
        repo_response.raise_for_status()
        repo_data = repo_response.json()

        # Get last activity
        result.last_activity = repo_data.get("pushed_at")
        if result.last_activity:
            # Parse the ISO 8601 timestamp and make it timezone-aware
            last_activity = parse_iso8601_timestamp(result.last_activity)
            now = datetime.now(timezone.utc)
            result.days_since_last_activity = (now - last_activity).days
            if result.days_since_last_activity > 365:
                result.warnings.append("Repository has been inactive for over a year")
                result.is_healthy = False
            elif result.days_since_last_activity > 90:
                result.warnings.append("Repository has been inactive for over 90 days")

        # Get issue count
        issues_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
        issues_response = requests.get(issues_url, headers=headers)
        issues_response.raise_for_status()
        result.open_issues_count = len(issues_response.json())

        # Get stars and forks
        result.stars_count = repo_data.get("stargazers_count", 0)
        result.forks_count = repo_data.get("forks_count", 0)

        # Check for README and LICENSE
        contents_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents"
        contents_response = requests.get(contents_url, headers=headers)
        if contents_response.status_code == 200:
            contents = contents_response.json()
            result.has_readme = any(file["name"] in README_FILES for file in contents)
            result.has_license = any(file["name"] in LICENSE_FILES for file in contents)

            if not result.has_readme:
                result.warnings.append("No README file found")
                result.is_healthy = False
            if not result.has_license:
                result.warnings.append("No LICENSE file found")
                result.is_healthy = False

    except requests.exceptions.RequestException as e:
        result.errors.append(f"Error checking GitHub repository: {str(e)}")
        result.is_healthy = False

    return result

def check_gitlab_health(owner: str, repo: str, token: Optional[str] = None) -> HealthCheckResult:
    """
    Perform health checks on a GitLab repository.
    """
    headers = get_gitlab_headers(token)
    result = HealthCheckResult(
        repository_url=f"https://gitlab.com/{owner}/{repo}",
        platform="gitlab",
        owner=owner,
        repo_name=repo
    )

    try:
        # Get project info
        project_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}"
        project_response = requests.get(project_url, headers=headers)
        project_response.raise_for_status()
        project_data = project_response.json()

        # Get last activity
        result.last_activity = project_data.get("last_activity_at")
        if result.last_activity:
            # Parse the ISO 8601 timestamp and make it timezone-aware
            last_activity = parse_iso8601_timestamp(result.last_activity)
            now = datetime.now(timezone.utc)
            result.days_since_last_activity = (now - last_activity).days
            if result.days_since_last_activity > 365:
                result.warnings.append("Repository has been inactive for over a year")
                result.is_healthy = False
            elif result.days_since_last_activity > 90:
                result.warnings.append("Repository has been inactive for over 90 days")

        # Get issue count
        issues_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}/issues"
        issues_response = requests.get(issues_url, headers=headers)
        issues_response.raise_for_status()
        result.open_issues_count = len(issues_response.json())

        # Get stars and forks
        result.stars_count = project_data.get("star_count", 0)
        result.forks_count = project_data.get("forks_count", 0)

        # Check for README and LICENSE using /repository/files/:file_path endpoint on default branch
        default_branch = project_data.get("default_branch", "master")
        # Check README
        result.has_readme = False
        for readme_name in README_FILES:
            file_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}/repository/files/{requests.utils.quote(readme_name, safe='')}"
            params = {"ref": default_branch}
            file_response = requests.get(file_url, headers=headers, params=params)
            if file_response.status_code == 200:
                result.has_readme = True
                break
        if not result.has_readme:
            result.warnings.append("No README file found")
            result.is_healthy = False
        # Check LICENSE
        result.has_license = False
        for license_name in LICENSE_FILES:
            file_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}/repository/files/{requests.utils.quote(license_name, safe='')}"
            params = {"ref": default_branch}
            file_response = requests.get(file_url, headers=headers, params=params)
            if file_response.status_code == 200:
                result.has_license = True
                break
        if not result.has_license:
            result.warnings.append("No LICENSE file found")
            result.is_healthy = False

    except requests.exceptions.RequestException as e:
        result.errors.append(f"Error checking GitLab repository: {str(e)}")
        result.is_healthy = False

    return result

def parse_repo_url(url: str):
    """
    Parse a repository URL to extract platform, owner, and repository name.
    """
    if url.startswith('git@'):
        parts = url.split(':')
        if len(parts) != 2:
            return None, None, None
        path = parts[1]
        if 'github.com' in url:
            platform = 'github'
        elif 'gitlab.com' in url:
            platform = 'gitlab'
        else:
            return None, None, None
    else:
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        if 'github.com' in parsed_url.netloc:
            platform = 'github'
        elif 'gitlab.com' in parsed_url.netloc:
            platform = 'gitlab'
        else:
            return None, None, None

    parts = path.split('/')
    if len(parts) >= 2:
        owner = parts[0]
        repo = parts[1].replace('.git', '')
        return platform, owner, repo

    return None, None, None

def parse_repo_path(path: str):
    """
    Parse a repository path string to extract platform, owner, and repository name.
    """
    parts = path.split('/')
    if len(parts) >= 2:
        if len(parts) == 2:
            return 'github', parts[0], parts[1]
        elif len(parts) >= 3:
            return 'gitlab', parts[0], parts[-1]
    return None, None, None

@github_router.get("/{owner}/{repo}", response_model=HealthCheckResult)
async def check_github_repo(
    owner: str,
    repo: str
):
    """
    Check health of a GitHub repository.
    """
    return check_github_health(owner, repo, GITHUB_TOKEN)

@gitlab_router.get("/{owner}/{repo}", response_model=HealthCheckResult)
async def check_gitlab_repo(
    owner: str,
    repo: str
):
    """
    Check health of a GitLab repository.
    """
    return check_gitlab_health(owner, repo, GITLAB_TOKEN)

@v1_router.post("/check", response_model=HealthCheckResponse)
async def check_repository(
    body: RepoCheckRequest
):
    """
    Check health of a repository using either URL or path.
    """
    repository_url = body.repository_url
    repository_path = body.repository_path
    if not repository_url and not repository_path:
        raise HTTPException(status_code=400, detail="Either repository_url or repository_path must be provided")

    platform = None
    owner = None
    repo = None

    if repository_url:
        platform, owner, repo = parse_repo_url(repository_url)
    elif repository_path:
        platform, owner, repo = parse_repo_path(repository_path)

    if not all([platform, owner, repo]):
        raise HTTPException(status_code=400, detail="Invalid repository URL or path")

    if platform == "github":
        result = check_github_health(owner, repo, GITHUB_TOKEN)
    elif platform == "gitlab":
        result = check_gitlab_health(owner, repo, GITLAB_TOKEN)
    else:
        raise HTTPException(status_code=400, detail="Unsupported repository platform")

    return HealthCheckResponse(results=[result])

@v1_router.post("/check/batch", response_model=HealthCheckResponse)
async def check_repositories_batch(
    body: RepoBatchCheckRequest
):
    """
    Check health of multiple repositories using either URL or path for each.
    """
    results = []
    for repo_req in body.repos:
        repository_url = repo_req.repository_url
        repository_path = repo_req.repository_path
        if not repository_url and not repository_path:
            results.append(HealthCheckResult(
                repository_url=repository_url or repository_path or "",
                platform="",
                owner="",
                repo_name="",
                errors=["Either repository_url or repository_path must be provided"],
                is_healthy=False
            ))
            continue
        platform = None
        owner = None
        repo = None
        if repository_url:
            platform, owner, repo = parse_repo_url(repository_url)
        elif repository_path:
            platform, owner, repo = parse_repo_path(repository_path)
        if not all([platform, owner, repo]):
            results.append(HealthCheckResult(
                repository_url=repository_url or repository_path or "",
                platform=platform or "",
                owner=owner or "",
                repo_name=repo or "",
                errors=["Invalid repository URL or path"],
                is_healthy=False
            ))
            continue
        if platform == "github":
            result = check_github_health(owner, repo, GITHUB_TOKEN)
        elif platform == "gitlab":
            result = check_gitlab_health(owner, repo, GITLAB_TOKEN)
        else:
            result = HealthCheckResult(
                repository_url=repository_url or repository_path or "",
                platform=platform or "",
                owner=owner or "",
                repo_name=repo or "",
                errors=["Unsupported repository platform"],
                is_healthy=False
            )
        results.append(result)
    return HealthCheckResponse(results=results)

# Include the routers
v1_router.include_router(github_router)
v1_router.include_router(gitlab_router)
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)