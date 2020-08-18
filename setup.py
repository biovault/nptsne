from setuptools import setup
from cmake_utils import CMakeExtension, CMakeBuild
import tempfile
import os


def get_git_derived_build_number():
    from git import Repo
    repo = Repo('.')
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
    print('Derive number for branch: ', branch)
    commits = list(repo.iter_commits(branch, paths='./src/nptsne/_version.txt', max_count=1))
    return len(list(repo.iter_commits(rev='{}^..{}'.format(commits[0].hexsha, branch))))

templibdir = os.environ.get('LIBSDIR', '/tmp/cibwlibsdir')
print("GIT_DERIVED_BUILD_NUMBER = {}".format(get_git_derived_build_number()))
 
setup(
    ext_modules=[CMakeExtension('_nptsne', 'nptsne', templibdir=templibdir)],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
