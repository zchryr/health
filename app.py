from fastapi import FastAPI, HTTPException, APIRouter
from typing import List, Dict, Optional
from pydantic import BaseModel
import requests
from urllib.parse import urlparse

# Create the main FastAPI app
app = FastAPI(
    title="Package Repository Checker",
    description="API to check repository information for Python packages on PyPI and NPM packages on npmjs.org",
    version="1.0.0"
)

# Create a router for v1
v1_router = APIRouter(prefix="/v1")

# Create routers for package endpoints
pypi_router = APIRouter(prefix="/pypi")
npm_router = APIRouter(prefix="/npm")

class PackageInfo(BaseModel):
    name: str
    summary: Optional[str] = None
    repository_url: Optional[str] = None
    repository_platform: Optional[str] = None
    repository_org: Optional[str] = None
    repository_name: Optional[str] = None
    error: Optional[str] = None

class PackageResponse(BaseModel):
    packages: List[PackageInfo]

def get_library_info(library_name: str) -> Dict:
    """
    Get information about a Python library from PyPI.
    """
    url = f"https://pypi.org/pypi/{library_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def get_npm_info(package_name: str) -> Dict:
    """
    Get information about an NPM package from npmjs.org.
    """
    url = f"https://registry.npmjs.org/{package_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def parse_repo_url(url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse a repository URL to extract platform, organization, and repository name.
    """
    # Handle git+https:// URLs
    if url.startswith('git+'):
        url = url[4:]

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')

    if len(path_parts) >= 2:
        org = path_parts[0]
        repo = path_parts[1]
        repo = repo.replace('.git', '')

        if 'github.com' in parsed_url.netloc:
            return 'github', org, repo
        elif 'gitlab.com' in parsed_url.netloc:
            return 'gitlab', org, repo
        elif 'bitbucket.org' in parsed_url.netloc:
            return 'bitbucket', org, repo

    return None, None, None

def extract_repo_info(info: Dict) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Extract repository information from package info.
    Prioritizes source code repository URLs over other GitHub URLs.
    """
    if not info or "project_urls" not in info:
        return None, None, None, None

    # Priority order for repository URL types
    primary_repo_types = ["Source", "Homepage"]
    secondary_repo_types = ["Repository", "Code"]

    # First try primary repository URL types
    for url_type, url in info["project_urls"].items():
        if url_type in primary_repo_types:
            platform, org, repo = parse_repo_url(url)
            if platform:
                return url, platform, org, repo

    # Then try secondary repository URL types
    for url_type, url in info["project_urls"].items():
        if url_type in secondary_repo_types:
            platform, org, repo = parse_repo_url(url)
            if platform:
                return url, platform, org, repo

    # If no specific repository URL found, look for any GitHub/GitLab/Bitbucket URL
    # but exclude known non-repository types
    excluded_types = ["Funding", "Sponsor", "Donate", "Bug Tracker", "Issue Tracker", "Documentation"]
    for url_type, url in info["project_urls"].items():
        if url_type not in excluded_types:
            platform, org, repo = parse_repo_url(url)
            if platform:
                return url, platform, org, repo

    return None, None, None, None

def extract_npm_repo_info(info: Dict) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Extract repository information from NPM package info.
    """
    if not info or "repository" not in info:
        return None, None, None, None

    repo_url = info["repository"].get("url")
    if not repo_url:
        return None, None, None, None

    platform, org, repo = parse_repo_url(repo_url)
    return repo_url, platform, org, repo

@pypi_router.get("/{package_name}", response_model=PackageInfo)
async def get_package_info(package_name: str):
    """
    Get repository information for a single PyPI package.
    """
    info = get_library_info(package_name)

    if not info:
        raise HTTPException(status_code=404, detail=f"Package {package_name} not found on PyPI")

    package_info = info.get("info", {})
    repo_url, platform, org, repo = extract_repo_info(package_info)

    return PackageInfo(
        name=package_name,
        summary=package_info.get("summary"),
        repository_url=repo_url,
        repository_platform=platform,
        repository_org=org,
        repository_name=repo
    )

@npm_router.get("/{package_name}", response_model=PackageInfo)
async def get_npm_package_info(package_name: str):
    """
    Get repository information for a single NPM package.
    """
    info = get_npm_info(package_name)

    if not info:
        raise HTTPException(status_code=404, detail=f"Package {package_name} not found on npmjs.org")

    repo_url, platform, org, repo = extract_npm_repo_info(info)

    return PackageInfo(
        name=package_name,
        summary=info.get("description"),
        repository_url=repo_url,
        repository_platform=platform,
        repository_org=org,
        repository_name=repo
    )

@pypi_router.post("/batch", response_model=PackageResponse)
async def get_multiple_packages(package_names: List[str]):
    """
    Get repository information for multiple PyPI packages.
    """
    results = []

    for package_name in package_names:
        info = get_library_info(package_name)

        if not info:
            results.append(PackageInfo(
                name=package_name,
                error=f"Package {package_name} not found on PyPI"
            ))
            continue

        package_info = info.get("info", {})
        repo_url, platform, org, repo = extract_repo_info(package_info)

        results.append(PackageInfo(
            name=package_name,
            summary=package_info.get("summary"),
            repository_url=repo_url,
            repository_platform=platform,
            repository_org=org,
            repository_name=repo
        ))

    return PackageResponse(packages=results)

@npm_router.post("/batch", response_model=PackageResponse)
async def get_multiple_npm_packages(package_names: List[str]):
    """
    Get repository information for multiple NPM packages.
    """
    results = []

    for package_name in package_names:
        info = get_npm_info(package_name)

        if not info:
            results.append(PackageInfo(
                name=package_name,
                error=f"Package {package_name} not found on npmjs.org"
            ))
            continue

        repo_url, platform, org, repo = extract_npm_repo_info(info)

        results.append(PackageInfo(
            name=package_name,
            summary=info.get("description"),
            repository_url=repo_url,
            repository_platform=platform,
            repository_org=org,
            repository_name=repo
        ))

    return PackageResponse(packages=results)

# Include the routers
v1_router.include_router(pypi_router)
v1_router.include_router(npm_router)
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)