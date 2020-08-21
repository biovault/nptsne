from setuptools import setup
from cmake_utils import CMakeExtension, CMakeBuild
import tempfile
import os

def get_current_tag(repo):
    return next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)

def get_repo_branch(repo):
    branch = ''
    is_ci = os.environ.get('CI', 'false').lower() == 'true'
    is_travis = os.environ.get('TRAVIS', 'false').lower() == 'true'
    is_appveyor = os.environ.get('APPVEYOR', 'false').lower() == 'true'
    if not is_ci:
        branch=repo.active_branch.name
    else:
        if is_appveyor:
            branch = os.environ.get('APPVEYOR_REPO_BRANCH')
        if is_travis:
            branch = os.environ.get('TRAVIS_BRANCH')
    return branch

def get_git_derived_build_number(repo, branch):
    print('Derive number for branch: ', branch)
    commits = list(repo.iter_commits(branch, paths='./src/nptsne/_version.txt', max_count=1))
    print('Derive number for commit (of _version.txt): ', commits[0].hexsha)
    return len(list(repo.iter_commits(rev='{}^..{}'.format(commits[0].hexsha, branch))))

def get_version():
    from git import Repo
    from pathlib import Path
    repo = Repo(Path(__file__).resolve().parent)
    tag = get_current_tag(repo)
    with open('./src/nptsne/_version.txt') as f:
        raw_version = f.read().strip()
    
    if tag and tag.startswith('release'):
        return raw_version
    
    branch = get_repo_branch(repo)
    build_number = str(get_git_derived_build_number(repo, branch))

    if branch.startswith('release'):
        return raw_version + 'rc' + build_number
        
    return raw_version + '.dev'+ build_number

templibdir = os.environ.get('LIBSDIR', '/tmp/cibwlibsdir')
print("git derived version = {}".format(get_version()))
 
setup(
    # Always append the build number for tracking purposes - this fits with PEP427
    version=get_version(),
    ext_modules=[CMakeExtension('_nptsne', 'nptsne', templibdir=templibdir)],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
