# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# _version.txt contains the base version for a release
#
# _full_version.txt is the _version.txt with the
#   alpha, beta or release-candidate suffix and number
#   appended. This is done in setup.py during a CI build.
#
# Generic release markers:
#   X.Y
#   X.Y.Z   # For bugfix releases
#
# Admissible pre-release markers:
#   X.YaN   # Alpha release
#   X.YbN   # Beta release
#   X.YrcN  # Release Candidate
#   X.Y     # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
#
import pkgutil

__rawversion = pkgutil.get_data("nptsne", "_full_version.txt").strip()
version = __rawversion.decode("utf-8")
__rawbranch = pkgutil.get_data("nptsne", "_branch_name.txt").strip()
branch_name = __rawbranch.decode("utf-8")
