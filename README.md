# Health

This repository contains tools and services for analyzing and monitoring package health across different programming languages and package managers. The main focus is on providing insights into package repositories, their metadata, and health metrics.

## Repository Structure

- `apis/package-info/`: A FastAPI-based service that provides repository information for both Python packages (PyPI) and NPM packages (npmjs.org)
  - RESTful API endpoints for package metadata
  - Support for batch processing
  - Docker deployment support
  - Comprehensive test coverage

- `apis/repo-health-check/`: A FastAPI-based service for analyzing repository health metrics
  - Support for both GitHub and GitLab repositories
  - Health checks including:
    - Last activity tracking and inactivity warnings
    - Open issues count
    - Stars and forks metrics
    - README and LICENSE file presence
  - Batch processing support for multiple repositories
  - RESTful API endpoints with versioning (v1)
  - Environment-based authentication for GitHub and GitLab APIs

- `example-projects/`: Example projects in different languages for testing and demonstration
  - `node-project/`: Example Node.js project
  - `go-project/`: Example Go project
  - `python-project/`: Example Python project

- `poc/`: Proof of concept implementations and experimental features

## Purpose

This repository aims to provide tools and services for:
1. Analyzing package health across different programming languages
2. Monitoring package repositories and their metadata
3. Providing insights into package dependencies and their relationships
4. Supporting development teams in making informed decisions about package usage
5. Evaluating repository health through activity metrics and documentation presence
6. Identifying potential maintenance issues through inactivity tracking

## Getting Started

For detailed information about specific components, please refer to their respective directories:
- [Package Info API Documentation](apis/package-info/README.md)
- [Repository Health Check API Documentation](apis/repo-health-check/README.md)

## Development

The repository uses Python for the main API services and includes example projects in various languages. Development dependencies and setup instructions can be found in the respective component directories.
