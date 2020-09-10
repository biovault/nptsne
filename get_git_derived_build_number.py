import argparse
import os

parser = argparse.ArgumentParser(description='Get a git derived build number on a branch based on number of changes since a file was changed')


parser.add_argument('file', type=str, help='File used to start the count')

args = parser.parse_args()

from git import Repo
repo = Repo('.')
branch=repo.active_branch.name
commits = list(repo.iter_commits('feature/cibuild', paths='./src/nptsne/_version.txt', max_count=1))
commits_cibuild = list(repo.iter_commits(rev='{}^..{}'.format(commits[0].hexsha, branch)))
print(len(commits_cibuild), end = '')
