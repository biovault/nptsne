import os
from git import Repo
from pathlib import Path

def get_branch_name(repo_path="./"):
    """Return the github branch

    Don't use this on ReadTheDocs

    Args:
        repo_path (str): Posix path to the repo defaults to working dir

    Returns:
        str: branch string - e.g. master, feature/xyz, release/nnn
    """
    not_rtd = os.environ.get("READTHEDOCS") != "True"
    assert not_rtd  # don't use this on read the docs
    repo = Repo(repo_path)
    return repo.active_branch.name
