# PyPI Repository Analyzer

A Python tool that analyzes Python packages on PyPI to extract and analyze their repository information. This tool helps developers map Python packages to their source repositories, understand package maintainers, and identify repository platform usage patterns.

## Features

- Fetches package metadata from PyPI's JSON API
- Identifies repository URLs from project metadata
- Parses repository URLs to extract:
  - Platform (GitHub/GitLab/Bitbucket)
  - Organization name
  - Repository name
- Provides detailed statistics about repository usage
- Handles error cases gracefully
- Offers both detailed and summary views of package information

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install requests
```

## Usage

Run the script with:
```bash
python check_libraries.py
```

## Output Format

### Individual Package Information
```
PACKAGE_NAME
============
Summary: Package description

Project URLs:
  • URL_TYPE (platform): organization/repository
```

### Repository Analysis
```
Repository Analysis
==================================================
Total packages analyzed: X
Packages with repository URLs: Y
Packages without repository URLs: Z

Repository Platform Statistics:
--------------------------------------------------
GITHUB:
  Packages using github: X
  Repositories:
    • organization/repository

Package Repository Mapping:
--------------------------------------------------
  • package-name: platform - organization/repository
```

## Supported Libraries

The tool currently analyzes the following Python packages:
```python
libraries = [
    "boto3", "urllib3", "requests", "certifi",
    "charset-normalizer", "idna", "python-dateutil",
    "aiobotocore", "six", "s3fs", "botocore",
    "setuptools", "requests-aws4auth", "grpcio-status",
    "opensearch-py", "typing-extensions", "events",
    "packaging", "s3transfer", "numpy", "pyyaml",
    "fsspec", "pydantic"
]
```

## Key Functions

- `get_library_info(library_name)`: Fetches package info from PyPI
- `parse_repo_url(url)`: Extracts platform, org, and repo from URLs
- `analyze_repo_urls(libraries_info)`: Analyzes and displays repository statistics

## Dependencies

- `requests`: For making HTTP requests to PyPI
- `urllib.parse`: For parsing URLs
- `collections.defaultdict`: For collecting statistics
- Standard library imports for typing and JSON handling

## Use Cases

This tool helps developers:
1. Map Python packages to their source repositories
2. Understand which organizations maintain which packages
3. Identify which repository platforms are most commonly used
4. Find packages that might be missing repository links
5. Get a quick overview of package metadata and documentation

## Contributing

Feel free to submit issues and enhancement requests!