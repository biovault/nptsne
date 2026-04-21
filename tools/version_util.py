import os
from git import Repo
from git.exc import InvalidGitRepositoryError

from pathlib import Path

import os

def _branch_from_env() -> str | None:
    # PR builds
    if os.getenv("GITHUB_HEAD_REF"):
        return os.environ["GITHUB_HEAD_REF"]
    # push/tag builds
    if os.getenv("GITHUB_REF_NAME"):
        return os.environ["GITHUB_REF_NAME"]
    return None

def _git_branch_or_sha(repo_path) -> str:
    try:
        from git import Repo  # GitPython
        repo = Repo(repo_path)

        # Detached HEAD safe: active_branch may raise TypeError
        try:
            return repo.active_branch.name
        except TypeError:
            # detached: use short sha
            return repo.head.commit.hexsha[:12]
    except Exception:
        return "unknown"
    
def get_branch_name(repo_path="./"):
    """Return the github branch

    Don't use this on ReadTheDocs

    Args:
        repo_path (str): Posix path to the repo defaults to working dir

    Returns:
        str: branch string - e.g. master, feature/xyz, release/nnn
    """
    not_rtd = os.environ.get("READTHEDOCS") != "True"
    return _branch_from_env() or _git_branch_or_sha(repo_path)
    
