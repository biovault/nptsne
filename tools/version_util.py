from pathlib import Path
import tempfile
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
    branch = ''
    is_ci = os.environ.get('CI', 'false').lower() == 'true'
    is_travis = os.environ.get('TRAVIS', 'false').lower() == 'true'
    is_appveyor = os.environ.get('APPVEYOR', 'false').lower() == 'true'
    if not is_ci:
        branch=get_branch_via_commit(repo)
    else:
        if is_appveyor:
            branch = os.environ.get('APPVEYOR_REPO_BRANCH')
        if is_travis:
            branch = os.environ.get('TRAVIS_BRANCH')
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
    return len(list(repo.iter_commits(rev='{}^..{}'.format(that_commit, this_commit))))

def get_version(repo_path):
    on_rtd = os.environ.get('READTHEDOCS') == 'True'
    version_file = repo_path / 'src/nptsne/_version.txt'
    # print('version file: ', version_file)
    with open(version_file) as f:
        raw_version = f.read().strip()
    # Readthedocs does a limited clone so the repo commit counting does not work
    if on_rtd:
        return raw_version
    # print('repo dir: ', repo_path)
    repo = Repo(repo_path)
    # commit = list(repo.iter_commits())[0].hexsha
    tag = get_current_tag(repo)

    # If a tag starts with the word release then just use the given version from the file
    if (tag is not None) and tag.tag.tag.startswith('release'):
        return raw_version
    
    #
    build_number = str(get_git_derived_build_number(repo, version_file))

    branch = get_repo_branch(repo)
    if branch.startswith('release'):
        return raw_version + 'rc' + build_number

    return raw_version + '.dev'+ build_number