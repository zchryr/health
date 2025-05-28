# dep-extractor

Extract direct dependencies from package manifest files (Python, JS, etc.)

## Supported Manifest Types
- `requirements.txt` (pip)
- `environment.yml` (conda, pip)
- `pyproject.toml` (Poetry)
- `poetry.lock` (Poetry lock file)
- `package.json` (npm)

## Planned Support
- `pom.xml`, `build.gradle` (Java/Maven/Gradle)
- `.csproj`, `packages.config` (C#/.NET)
- `composer.json` (PHP)
- `conanfile.txt`, `CMakeLists.txt` (C++)
- `go.mod` (Go)
- `Gemfile` (Ruby)
- `build.gradle.kts` (Kotlin)
- `Package.swift` (Swift)
- `Cargo.toml` (Rust)


## Installation

**Python 3.8+ is required.**

1. (Recommended) Create and activate a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### CLI

Run the CLI on a manifest file:

```sh
python -m dep_extractor.cli path/to/manifest
# or specify type
python -m dep_extractor.cli path/to/manifest --manifest-type poetry.lock
```

Or, if installed as a package with an entry point:
```sh
dep-extractor path/to/manifest
```

Outputs dependencies as JSON.

#### Example:
```sh
python -m dep_extractor.cli ../example-projects/python-project/poetry.lock
```

### As a Library

```python
from dep_extractor.extractor.requirements_txt import extract_requirements_txt
deps = extract_requirements_txt("requirements.txt")
```

## Troubleshooting
- If you see `ModuleNotFoundError`, ensure you have installed all dependencies with `pip install -r requirements.txt` and are using the correct Python environment.