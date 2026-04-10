# David Völgyes. (2020, February 20). Zenodo_get: a downloader for Zenodo records (Version 3.0.0).
# Zenodo. https://doi.org/10.5281/zenodo.1261812

# Bibtex format:
# @misc{david_volgyes_2020_10.5281/zenodo.1261812,
#   author  = {David Völgyes},
#   title   = {Zenodo_get: a downloader for Zenodo records.},
#   month   = {2},
#   year    = {2020},
#   doi     = {10.5281/zenodo.1261812},
#   url     = {https://doi.org/10.5281/zenodo.1261812}
# }

from zenodo_get import download
import zipfile
from pathlib import Path


def main():
    # Download all files from the nptsne zenodo record
    download("10.5281/zenodo.19470311", output_dir="./zenodo")

    p = sorted(Path("./zenodo").rglob("nptsne*.zip"))

    print(p)
    with zipfile.ZipFile(p[0], "r") as zip_ref:
        zip_ref.extractall("./data")


if __name__ == "__main__":
    main()
