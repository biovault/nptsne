import os
from git import Repo
from git.exc import InvalidGitRepositoryError

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
    repo = None
    try:
      repo = Repo(repo_path)

    except InvalidGitRepositoryError:
        return "0+unknown"

    try:
        # works only when on a branch
        return repo.active_branch.name
    except TypeError:
        # detached HEAD
        # If HEAD is detached, do NOT use repo.head.reference / active_branch
        sha = repo.head.commit.hexsha[:8]
        return f"0+g{sha}"
    
