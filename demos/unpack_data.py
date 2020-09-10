import zipfile
from pathlib import Path

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    with zipfile.ZipFile(root / 'data.zip', 'r') as zip_ref:
        zip_ref.extractall(root)
