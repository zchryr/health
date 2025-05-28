# dep-extractor GitHub Action

Extract direct dependencies from a manifest file (Python, JS, etc.) using the dep_extractor tool.

## Inputs
- `manifest` (required): Path to the manifest file (e.g., `requirements.txt`, `package.json`).
- `manifest_type` (optional): Type of manifest (e.g., `requirements.txt`, `package.json`, `poetry.lock`). If not provided, inferred from filename.

## Outputs
- `output`: Extracted dependencies as JSON (single-line).

## Example Usage (GitHub Action)
```yaml
- name: Extract dependencies
  uses: ./dep_extractor/action
  with:
    manifest: path/to/manifest
    manifest_type: requirements.txt  # optional

- name: Show dependencies
  run: echo "${{ steps.extract_deps.outputs.output }}"
```

---

## Manual Usage

### Run with Docker

Build the Docker image:
```sh
docker build -t dep-extractor ./dep-extractor
```

Run the image (replace `/path/to/manifest` and optionally set `MANIFEST_TYPE`):
```sh
docker run --rm \
  -e INPUT_MANIFEST=/path/to/manifest \
  -e INPUT_MANIFEST_TYPE=requirements.txt \  # optional
  -v $(pwd):/data \
  dep_extractor
```
- `INPUT_MANIFEST` is required and should be the path inside the container (e.g., `/data/requirements.txt`).
- `INPUT_MANIFEST_TYPE` is optional. If omitted, the type is inferred from the filename.
- The `-v $(pwd):/data` flag mounts your current directory into the container at `/data`.

### Run with Python

Install dependencies:
```sh
cd dep-extractor
pip install -r requirements.txt
```

Run the CLI:
```sh
python -m dep_extractor.cli /path/to/manifest --manifest-type requirements.txt  # --manifest-type is optional
```
- If `--manifest-type` is omitted, the type is inferred from the filename.
- Output is printed as JSON to stdout.