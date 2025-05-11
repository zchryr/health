import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app, parse_repo_url, extract_repo_info, extract_npm_repo_info

client = TestClient(app)

# Test utility functions
def test_parse_repo_url():
    # Test GitHub URL
    platform, org, repo = parse_repo_url("https://github.com/org/repo")
    assert platform == "github"
    assert org == "org"
    assert repo == "repo"

    # Test GitLab URL
    platform, org, repo = parse_repo_url("https://gitlab.com/org/repo.git")
    assert platform == "gitlab"
    assert org == "org"
    assert repo == "repo"

    # Test Bitbucket URL
    platform, org, repo = parse_repo_url("https://bitbucket.org/org/repo")
    assert platform == "bitbucket"
    assert org == "org"
    assert repo == "repo"

    # Test invalid URL
    platform, org, repo = parse_repo_url("https://invalid.com/url")
    assert platform is None
    assert org is None
    assert repo is None

def test_extract_repo_info():
    # Test with source URL
    info = {
        "project_urls": {
            "Source": "https://github.com/org/repo",
            "Homepage": "https://example.com"
        }
    }
    url, platform, org, repo = extract_repo_info(info)
    assert url == "https://github.com/org/repo"
    assert platform == "github"
    assert org == "org"
    assert repo == "repo"

    # Test with no repository info
    info = {"project_urls": {"Homepage": "https://example.com"}}
    url, platform, org, repo = extract_repo_info(info)
    assert url is None
    assert platform is None
    assert org is None
    assert repo is None

def test_extract_npm_repo_info():
    # Test with valid repository info
    info = {
        "repository": {
            "url": "https://github.com/org/repo"
        }
    }
    url, platform, org, repo = extract_npm_repo_info(info)
    assert url == "https://github.com/org/repo"
    assert platform == "github"
    assert org == "org"
    assert repo == "repo"

    # Test with no repository info
    info = {"name": "package"}
    url, platform, org, repo = extract_npm_repo_info(info)
    assert url is None
    assert platform is None
    assert org is None
    assert repo is None

# Mock responses for PyPI and NPM
@pytest.fixture
def mock_pypi_response():
    return {
        "info": {
            "name": "test-package",
            "summary": "Test package",
            "version": "1.0.0",
            "project_urls": {
                "Source": "https://github.com/org/repo"
            }
        },
        "releases": {
            "1.0.0": [{"upload_time_iso_8601": "2023-01-01T00:00:00Z"}]
        }
    }

@pytest.fixture
def mock_npm_response():
    return {
        "name": "test-package",
        "description": "Test package",
        "dist-tags": {"latest": "1.0.0"},
        "time": {"created": "2023-01-01T00:00:00Z"},
        "repository": {
            "url": "https://github.com/org/repo"
        }
    }

# Test API endpoints
@patch('app.get_library_info')
def test_get_pypi_package_info(mock_get_library_info, mock_pypi_response):
    mock_get_library_info.return_value = mock_pypi_response

    response = client.get("/v1/pypi/test-package")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-package"
    assert data["repository_platform"] == "github"
    assert data["repository_org"] == "org"
    assert data["repository_name"] == "repo"
    assert data["latest_version"] == "1.0.0"
    assert data["created_date"] == "2023-01-01T00:00:00Z"

@patch('app.get_npm_info')
def test_get_npm_package_info(mock_get_npm_info, mock_npm_response):
    mock_get_npm_info.return_value = mock_npm_response

    response = client.get("/v1/npm/test-package")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-package"
    assert data["repository_platform"] == "github"
    assert data["repository_org"] == "org"
    assert data["repository_name"] == "repo"
    assert data["latest_version"] == "1.0.0"
    assert data["created_date"] == "2023-01-01T00:00:00Z"

@patch('app.get_library_info')
def test_get_pypi_package_not_found(mock_get_library_info):
    mock_get_library_info.return_value = None

    response = client.get("/v1/pypi/nonexistent-package")
    assert response.status_code == 404
    assert response.json()["detail"] == "Package nonexistent-package not found on PyPI"

@patch('app.get_npm_info')
def test_get_npm_package_not_found(mock_get_npm_info):
    mock_get_npm_info.return_value = None

    response = client.get("/v1/npm/nonexistent-package")
    assert response.status_code == 404
    assert response.json()["detail"] == "Package nonexistent-package not found on npmjs.org"

@patch('app.get_library_info')
def test_get_multiple_pypi_packages(mock_get_library_info, mock_pypi_response):
    mock_get_library_info.return_value = mock_pypi_response

    response = client.post("/v1/pypi/batch", json=["test-package"])
    assert response.status_code == 200
    data = response.json()
    assert len(data["packages"]) == 1
    assert data["packages"][0]["name"] == "test-package"
    assert data["packages"][0]["repository_platform"] == "github"

@patch('app.get_npm_info')
def test_get_multiple_npm_packages(mock_get_npm_info, mock_npm_response):
    mock_get_npm_info.return_value = mock_npm_response

    response = client.post("/v1/npm/batch", json=["test-package"])
    assert response.status_code == 200
    data = response.json()
    assert len(data["packages"]) == 1
    assert data["packages"][0]["name"] == "test-package"
    assert data["packages"][0]["repository_platform"] == "github"