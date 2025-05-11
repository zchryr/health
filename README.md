# Health

This repository contains tools and services for analyzing and monitoring package health across different programming languages and package managers. The main focus is on providing insights into package repositories, their metadata, and health metrics.

## Repository Structure

- `package-info-api/`: A FastAPI-based service that provides repository information for both Python packages (PyPI) and NPM packages (npmjs.org)
  - RESTful API endpoints for package metadata
  - Support for batch processing
  - Docker deployment support
  - Comprehensive test coverage

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

## Getting Started

For detailed information about specific components, please refer to their respective directories:
- [Package Info API Documentation](package-info-api/README.md)

## Development

The repository uses Python for the main API service and includes example projects in various languages. Development dependencies and setup instructions can be found in the respective component directories.
