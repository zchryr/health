# dep-extractor GitHub Action

Extract direct dependencies from a manifest file (Python, JS, etc.) using the dep_extractor tool.

## Inputs
- `manifest` (required): Path to the manifest file (e.g., `requirements.txt`, `package.json`).
- `manifest_type` (optional): Type of manifest (e.g., `requirements.txt`, `package.json`, `poetry.lock`). If not provided, inferred from filename.

## Outputs
- `output`: Extracted dependencies as JSON (single-line).

## Example Usage
```yaml
- name: Extract dependencies
  uses: ./dep_extractor/action
  with:
    manifest: path/to/manifest
    manifest_type: requirements.txt  # optional

- name: Show dependencies
  run: echo "${{ steps.extract_deps.outputs.output }}"
```