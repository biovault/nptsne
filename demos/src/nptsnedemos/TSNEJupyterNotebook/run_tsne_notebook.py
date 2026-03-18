import subprocess
import sys
from pathlib import Path

def open_notebook():
    notebook = Path(__file__).parent / "NPTSNE_notebooktests.ipynb"
    subprocess.run([
        sys.executable, "-m", "jupyter", "lab", str(notebook)
    ])