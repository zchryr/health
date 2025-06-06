import typer
import json
from pathlib import Path
from dep_extractor.extractor.requirements_txt import extract_requirements_txt
from dep_extractor.extractor.environment_yml import extract_environment_yml
from dep_extractor.extractor.pyproject_toml import extract_pyproject_toml
from dep_extractor.extractor.package_json import extract_package_json
from dep_extractor.extractor.poetry_lock import extract_poetry_lock

def main(
    file: Path = typer.Argument(..., help="Path to the manifest file"),
    manifest_type: str = typer.Option(None, help="Type of manifest: requirements.txt, environment.yml, pyproject.toml, package.json, poetry.lock")
):
    if not file.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(1)
    if not manifest_type:
        # Infer from file name
        name = file.name.lower()
        if name == 'requirements.txt':
            manifest_type = 'requirements.txt'
        elif name == 'environment.yml':
            manifest_type = 'environment.yml'
        elif name == 'pyproject.toml':
            manifest_type = 'pyproject.toml'
        elif name == 'package.json':
            manifest_type = 'package.json'
        elif name == 'poetry.lock':
            manifest_type = 'poetry.lock'
        else:
            typer.echo("Could not infer manifest type. Please specify --manifest-type.", err=True)
            raise typer.Exit(1)
    if manifest_type == 'requirements.txt':
        deps = extract_requirements_txt(str(file))
    elif manifest_type == 'environment.yml':
        deps = extract_environment_yml(str(file))
    elif manifest_type == 'pyproject.toml':
        deps = extract_pyproject_toml(str(file))
    elif manifest_type == 'package.json':
        deps = extract_package_json(str(file))
    elif manifest_type == 'poetry.lock':
        deps = extract_poetry_lock(str(file))
    else:
        typer.echo(f"Unsupported manifest type: {manifest_type}", err=True)
        raise typer.Exit(1)
    typer.echo(json.dumps([dep.__dict__ for dep in deps], indent=2))

if __name__ == "__main__":
    typer.run(main)