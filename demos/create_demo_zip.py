import zipfile
import sys
from pathlib import Path
from zenodo_get import download

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def]

# Configure your includes here (or load from pyproject.toml / a YAML file)

def get_demo_data(demobase: Path):
      # Download all files from the nptsne zenodo record
  zen_doi = "10.5281/zenodo.19470311"
  print(f"fetch data from Zenodo DOI {zen_doi}")
  download(zen_doi, output_dir=Path(demobase, "download"))

  p = sorted(Path(demobase, "download").rglob("data.zip"))
  
  print(p)
  with zipfile.ZipFile(p[0], 'r') as zip_ref:
      zip_ref.extractall(Path(demobase, './data'))

def load_include_list(pyproject_path: Path = Path("./demos/pyproject.toml")) -> list[str]:
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data.get("tool", {}).get("create_demo_zip", {}).get("include", [])


def add_to_zip(zf: zipfile.ZipFile, source: Path, base: Path) -> None:
    if source.is_file():
        zf.write(source, source.relative_to(base))
    elif source.is_dir():
        for file in source.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(base))


def main(output: Path, base: Path = Path(".")) -> None:
    demobase = Path(Path(__file__).resolve().parent)
    get_demo_data(demobase)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zip_includes = load_include_list(Path(demobase, "pyproject.toml"))
        for entry in zip_includes:
            source = demobase / entry
            if not source.exists():
                print(f"Warning: {source} does not exist, skipping")
                continue
            add_to_zip(zf, source, demobase)
    print(f"Created {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("demos.zip")
    main(output)
