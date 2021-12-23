import os
from git import Repo


def get_current_tag(repo):
    return next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)


def get_branch_via_commit(repo):
    #  Should handle detached head
    c = list(repo.iter_commits())[0]
    branch_name = None
    for r in repo.refs:
        if r.object.hexsha == c.hexsha:
            branch_name = str(r)
    return branch_name


def get_repo_branch(repo):
    branch = ""
    is_ci = os.environ.get("CI", "false").lower() == "true"
    is_travis = os.environ.get("TRAVIS", "false").lower() == "true"
    is_appveyor = os.environ.get("APPVEYOR", "false").lower() == "true"
    if not is_ci:
        branch = get_branch_via_commit(repo)
    else:
        if is_appveyor:
            branch = os.environ.get("APPVEYOR_REPO_BRANCH")
        if is_travis:
            branch = os.environ.get("TRAVIS_BRANCH")
        else:
            # use nelonoel/branch-name on GitHub actions
            branch = os.environ.get("BRANCH_NAME")
    return branch


def get_git_derived_build_number(repo, commit_path):
    """
    Get a build number counting from the last commit of a specified file.
    If that file is the version stamp then this counts the number of commits
    the last version change - a good enough approximation to a CI independent
    build number.
    """
    that_commit = list(repo.iter_commits(None, paths=commit_path, max_count=1))[0].hexsha
    this_commit = list(repo.iter_commits())[0].hexsha
    # print('Derive number for commit (of _version.txt): ', that_commit)
    return len(list(repo.iter_commits(rev="{}^..{}".format(that_commit, this_commit))))


def get_version(repo_path="./"):
    """Create the version string by concatenating:
        - contents of the version file, src/nptsne/_version.txt
        - the PEP440TYPE (may be blank)
        - the build number derived from the commit
          counting since the last
          change to the version file

        If running on ReadTheDocs the repo tag is used.
        If PEP440TYPE is blank then the raw version is returned
        If PEP440TYPE is "rcNN" then it is appended to the raw version

    Args:
        repo_path (str): Posix path to the repo defaults to working dir

    Returns:
        str: derived version string
    """
    on_rtd = os.environ.get("READTHEDOCS") == "True"
    pep440type = os.environ.get("PEP440TYPE", "")
    version_file = repo_path / "src/nptsne/_version.txt"
    repo = Repo(repo_path)

    # Readthedocs must use the tag
    # The convention is that the tag is prefixed with v
    if on_rtd:
        # commit = list(repo.iter_commits())[0].hexsha
        tag = get_current_tag(repo)
        assert tag is not None
        return tag

    raw_version = "X.Y.Z"
    with open(version_file) as f:
        raw_version = f.read().strip()

    if pep440type == "" or pep440type[0:2] == "rc":
        return f"{raw_version}{pep440type}"
    else:
        build_number = str(get_git_derived_build_number(repo, version_file))
        # print('version file: ', version_file)

        return f"{raw_version}{pep440type}{build_number}"


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
