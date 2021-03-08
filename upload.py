import argparse
import os
from pathlib import Path
import requests
import hashlib


def get_md5_hash(sourcepath):
    md5 = hashlib.md5()
    with open(sourcepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def upload(user, password, sourcepath, targetpath):
    hash = get_md5_hash(sourcepath)

    with open(sourcepath, "rb") as f:
        requests.put(targetpath, auth=(user, password),
                     headers={"X-Checksum-md5": hash},
                     verify=False, data=f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="File to upload")
    parser.add_argument("targetpath",
                        type=str,
                        help="""Target path - a
                        subdirectory of https://lkeb-artifactory.lumc.nl/artifactory/wheels/nptsne
                        - e.g.: v1.0/file.bin""")
    args = parser.parse_args()
    filepath = Path(args.file)
    if not filepath.exists():
        raise RuntimeError(f"Can find {filepath}")
    targetpath = ("https://lkeb-artifactory.lumc.nl/artifactory/wheels/nptsne/" +
                  args.targetpath + "/" + filepath.name)

    upload(os.environ["CONAN_LOGIN_USERNAME"], os.environ["CONAN_PASSWORD"], filepath, targetpath)
