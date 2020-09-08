from setuptools import setup
from cmake_utils import CMakeExtension, CMakeBuild
from pathlib import Path
import tempfile
import os

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

def get_version():
    from git import Repo
    parent = Path(__file__).resolve().parent
    # print('repo dir: ', parent)
    repo = Repo(parent)
    # commit = list(repo.iter_commits())[0].hexsha
    tag = get_current_tag(repo)
    version_file = Path(parent, './', 'src/nptsne/_version.txt')
    # print('version file: ', version_file)
    with open(version_file) as f:
        raw_version = f.read().strip()
    
    if tag and tag.startswith('release'):
        return raw_version
    
    #
    build_number = str(get_git_derived_build_number(repo, version_file))

    branch = get_repo_branch(repo)
    if branch.startswith('release'):
        return raw_version + 'rc' + build_number

    return raw_version + '.dev'+ build_number

#  This temporary directory is used to collect libs
#  for inclusion in the wheel 
templibdir = Path(Path(tempfile.gettempdir()), 'cibwlibsdir')
print('Creating cibwlibsdir at: ', templibdir)
templibdir.mkdir(exist_ok=True)
 
setup(
    # Always append the build number for tracking purposes - this fits with PEP427
    version=get_version(),
    ext_modules=[CMakeExtension('_nptsne', 'nptsne', templibdir=str(templibdir))],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
