import subprocess
import sys
from pathlib import Path

def open_notebook():
    notebook = Path(Path(__file__).resolve().parent.parent, "data", "NPTSNE_notebooktests.ipynb")
    subprocess.run([
        sys.executable, "-m", "jupyter", "lab", str(notebook)
    ])