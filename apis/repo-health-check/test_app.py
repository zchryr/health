import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app import (
    app,
    parse_repo_url,
    parse_repo_path,
    parse_iso8601_timestamp,
    format_iso8601_timestamp,
    check_github_health,
    check_gitlab_health
)

client = TestClient(app)

# Test utility functions
def test_parse_repo_url():
    # Test GitHub URL
    platform, owner, repo = parse_repo_url("https://github.com/org/repo")
    assert platform == "github"
    assert owner == "org"
    assert repo == "repo"

    # Test GitLab URL
    platform, owner, repo = parse_repo_url("https://gitlab.com/org/repo.git")
    assert platform == "gitlab"
    assert owner == "org"
    assert repo == "repo"

    # Test invalid URL
    platform, owner, repo = parse_repo_url("https://invalid.com/url")
    assert platform is None
    assert owner is None
    assert repo is None

def test_parse_repo_path():
    # Test GitHub path
    platform, owner, repo = parse_repo_path("github.com/org/repo")
    assert platform == "github"
    assert owner == "org"
    assert repo == "repo"

    # Test GitLab path
    platform, owner, repo = parse_repo_path("gitlab.com/org/repo")
    assert platform == "gitlab"
    assert owner == "org"
    assert repo == "repo"

    # Test invalid path
    platform, owner, repo = parse_repo_path("invalid/path")
    assert platform is None
    assert owner is None
    assert repo is None

def test_parse_iso8601_timestamp():
    # Test GitHub format (without microseconds)
    timestamp = "2023-01-01T00:00:00Z"
    dt = parse_iso8601_timestamp(timestamp)
    assert isinstance(dt, datetime)
    assert dt.tzinfo == timezone.utc
    assert dt.year == 2023
    assert dt.month == 1
    assert dt.day == 1

    # Test GitLab format (with microseconds)
    timestamp = "2023-01-01T00:00:00.000Z"
    dt = parse_iso8601_timestamp(timestamp)
    assert isinstance(dt, datetime)
    assert dt.tzinfo == timezone.utc
    assert dt.year == 2023
    assert dt.month == 1
    assert dt.day == 1

    # Test invalid format
    with pytest.raises(ValueError):
        parse_iso8601_timestamp("invalid-timestamp")

def test_format_iso8601_timestamp():
    # Test with timezone-aware datetime
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    formatted = format_iso8601_timestamp(dt)
    assert formatted == "2023-01-01T00:00:00+00:00"

    # Test with naive datetime
    dt = datetime(2023, 1, 1)
    formatted = format_iso8601_timestamp(dt)
    assert formatted == "2023-01-01T00:00:00+00:00"

# Mock responses for GitHub and GitLab
@pytest.fixture
def mock_github_response():
    return {
        "pushed_at": "2023-01-01T00:00:00Z",
        "stargazers_count": 100,
        "forks_count": 50,
        "default_branch": "main"
    }

@pytest.fixture
def mock_gitlab_response():
    return {
        "last_activity_at": "2023-01-01T00:00:00.000Z",
        "star_count": 100,
        "forks_count": 50,
        "default_branch": "main"
    }

# Test API endpoints
@patch('app.check_github_health')
def test_check_github_repo(mock_check_github_health):
    mock_result = {
        "repository_url": "https://github.com/org/repo",
        "platform": "github",
        "owner": "org",
        "repo_name": "repo",
        "last_activity": "2023-01-01T00:00:00Z",
        "days_since_last_activity": 30,
        "open_issues_count": 5,
        "stars_count": 100,
        "forks_count": 50,
        "has_readme": True,
        "has_license": True,
        "warnings": [],
        "errors": [],
        "is_healthy": True
    }
    mock_check_github_health.return_value = mock_result

    response = client.get("/v1/github/org/repo")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "github"
    assert data["owner"] == "org"
    assert data["repo_name"] == "repo"
    assert data["is_healthy"] is True

@patch('app.check_gitlab_health')
def test_check_gitlab_repo(mock_check_gitlab_health):
    mock_result = {
        "repository_url": "https://gitlab.com/org/repo",
        "platform": "gitlab",
        "owner": "org",
        "repo_name": "repo",
        "last_activity": "2023-01-01T00:00:00Z",
        "days_since_last_activity": 30,
        "open_issues_count": 5,
        "stars_count": 100,
        "forks_count": 50,
        "has_readme": True,
        "has_license": True,
        "warnings": [],
        "errors": [],
        "is_healthy": True
    }
    mock_check_gitlab_health.return_value = mock_result

    response = client.get("/v1/gitlab/org/repo")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "gitlab"
    assert data["owner"] == "org"
    assert data["repo_name"] == "repo"
    assert data["is_healthy"] is True

@patch('app.check_github_health')
def test_check_repository_with_url(mock_check_github_health):
    mock_result = {
        "repository_url": "https://github.com/org/repo",
        "platform": "github",
        "owner": "org",
        "repo_name": "repo",
        "last_activity": "2023-01-01T00:00:00Z",
        "days_since_last_activity": 30,
        "open_issues_count": 5,
        "stars_count": 100,
        "forks_count": 50,
        "has_readme": True,
        "has_license": True,
        "warnings": [],
        "errors": [],
        "is_healthy": True
    }
    mock_check_github_health.return_value = mock_result

    response = client.post("/v1/check", json={"repository_url": "https://github.com/org/repo"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["platform"] == "github"
    assert data["results"][0]["is_healthy"] is True

@patch('app.check_github_health')
@patch('app.check_gitlab_health')
def test_check_repositories_batch(mock_check_gitlab_health, mock_check_github_health):
    mock_github_result = {
        "repository_url": "https://github.com/org1/repo1",
        "platform": "github",
        "owner": "org1",
        "repo_name": "repo1",
        "is_healthy": True
    }
    mock_gitlab_result = {
        "repository_url": "https://gitlab.com/org2/repo2",
        "platform": "gitlab",
        "owner": "org2",
        "repo_name": "repo2",
        "is_healthy": True
    }
    mock_check_github_health.return_value = mock_github_result
    mock_check_gitlab_health.return_value = mock_gitlab_result

    response = client.post("/v1/check/batch", json={
        "repos": [
            {"repository_url": "https://github.com/org1/repo1"},
            {"repository_url": "https://gitlab.com/org2/repo2"}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["platform"] == "github"
    assert data["results"][1]["platform"] == "gitlab"
    assert all(result["is_healthy"] for result in data["results"])

def test_check_repository_invalid_url():
    response = client.post("/v1/check", json={"repository_url": "invalid-url"})
    assert response.status_code == 400
    assert "Invalid repository URL" in response.json()["detail"]

def test_check_repository_missing_params():
    response = client.post("/v1/check", json={})
    assert response.status_code == 400
    assert "Either repository_url or repository_path must be provided" in response.json()["detail"]