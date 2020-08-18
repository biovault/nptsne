import argparse
import os

parser = argparse.ArgumentParser(description='Get a git derived build number on a branch based on number of changes since a file was changed')

parser.add_argument('branch', type=str, help='Branch used to calculate the build number')
parser.add_argument('file', type=str, help='File used to start the count')

args = parser.parse_args()

from git import Repo
repo = Repo('.')

commits = list(repo.iter_commits('feature/cibuild', paths=args.file, max_count=1))
commits_cibuild = list(repo.iter_commits(rev='{}^..{}'.format(commits[0].hexsha, args.branch)))
print(len(commits_cibuild), end = '')
