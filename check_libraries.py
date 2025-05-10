import requests
import json
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from urllib.parse import urlparse

def get_library_info(library_name: str) -> Dict:
    """
    Get information about a Python library from PyPI.

    Args:
        library_name (str): Name of the library to check

    Returns:
        Dict: Library information from PyPI
    """
    url = f"https://pypi.org/pypi/{library_name}/json"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {library_name}: {str(e)}")
        return None

def parse_repo_url(url: str) -> Tuple[str, str, str]:
    """
    Parse a repository URL to extract platform, organization, and repository name.

    Args:
        url (str): Repository URL

    Returns:
        Tuple[str, str, str]: Platform, organization, and repository name
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')

    if len(path_parts) >= 2:
        org = path_parts[0]
        repo = path_parts[1]
        # Remove .git suffix if present
        repo = repo.replace('.git', '')

        if 'github.com' in parsed_url.netloc:
            return 'github', org, repo
        elif 'gitlab.com' in parsed_url.netloc:
            return 'gitlab', org, repo
        elif 'bitbucket.org' in parsed_url.netloc:
            return 'bitbucket', org, repo

    return None, None, None

def analyze_repo_urls(libraries_info: Dict[str, Dict]) -> None:
    """
    Analyze and display statistics about repository URLs across all packages.

    Args:
        libraries_info (Dict[str, Dict]): Dictionary containing library information
    """
    repo_stats = {
        'github': {'count': 0, 'repos': set()},
        'gitlab': {'count': 0, 'repos': set()},
        'bitbucket': {'count': 0, 'repos': set()}
    }

    packages_with_repos = set()
    packages_without_repos = set()
    package_repos = {}  # Store repo info for each package

    for library, info in libraries_info.items():
        has_repo = False
        if info and "project_urls" in info:
            for url_type, url in info["project_urls"].items():
                platform, org, repo = parse_repo_url(url)
                if platform:
                    has_repo = True
                    repo_info = f"{org}/{repo}"
                    repo_stats[platform]['count'] += 1
                    repo_stats[platform]['repos'].add(repo_info)
                    package_repos[library] = (platform, repo_info)

        if has_repo:
            packages_with_repos.add(library)
        else:
            packages_without_repos.add(library)

    print("\nRepository Analysis")
    print("=" * 50)
    print(f"Total packages analyzed: {len(libraries_info)}")
    print(f"Packages with repository URLs: {len(packages_with_repos)}")
    print(f"Packages without repository URLs: {len(packages_without_repos)}")

    print("\nRepository Platform Statistics:")
    print("-" * 50)
    for platform, stats in repo_stats.items():
        print(f"\n{platform.upper()}:")
        print(f"  Packages using {platform}: {stats['count']}")
        if stats['repos']:
            print("  Repositories:")
            for repo in sorted(stats['repos']):
                print(f"    • {repo}")

    print("\nPackage Repository Mapping:")
    print("-" * 50)
    for package, (platform, repo) in sorted(package_repos.items()):
        print(f"  • {package}: {platform} - {repo}")

    if packages_without_repos:
        print("\nPackages without repository URLs:")
        print("-" * 50)
        for package in sorted(packages_without_repos):
            print(f"  • {package}")

def main():
    # List of libraries to check
    libraries = [
        "boto3",
        "urllib3",
        "requests",
        "certifi",
        "charset-normalizer",
        "idna",
        "python-dateutil",
        "aiobotocore",
        "six",
        "s3fs",
        "botocore",
        "setuptools",
        "requests-aws4auth",
        "grpcio-status",
        "opensearch-py",
        "typing-extensions",
        "events",
        "packaging",
        "s3transfer",
        "numpy",
        "pyyaml",
        "fsspec",
        "pydantic"
    ]

    # Dictionary to store all library information
    libraries_info = {}

    for library in libraries:
        print(f"\nChecking {library}...")
        info = get_library_info(library)

        if info:
            # Extract relevant information
            project_urls = info.get("info", {}).get("project_urls", {})
            summary = info.get("info", {}).get("summary", "No summary available")

            print(f"\n{library.upper()}")
            print("=" * len(library.upper()))
            print(f"Summary: {summary}")
            if project_urls and isinstance(project_urls, dict):
                print("\nProject URLs:")
                for url_type, url in project_urls.items():
                    platform, org, repo = parse_repo_url(url)
                    if platform:
                        print(f"  • {url_type} ({platform}): {org}/{repo}")
                    else:
                        print(f"  • {url_type}: {url}")
            print("-" * 50)

            # Store the information for analysis
            libraries_info[library] = info.get("info", {})
        else:
            print(f"Could not fetch information for {library}")

    # Analyze repository URLs across all packages
    analyze_repo_urls(libraries_info)

if __name__ == "__main__":
    main()