"""Doctests for nptsne"""
import doctest
from doctest import REPORT_NDIFF, ELLIPSIS
import numpy as np
import nptsne
import nptsne.libs._nptsne
import os

_skip = object()
SKIP_IN_CI = doctest.register_optionflag('SKIP_IN_CI')
is_ci = os.environ.get('CI', 'false').lower() == 'true'

#  Monkey patch the OutputChecker to handle extra SKIP_IN_CI

def check_output(self, want, got, optionflags):
    if optionflags & SKIP_IN_CI and is_ci:
        return True
    else:
        return self.__base_check_output(want, got, optionflags)
         
doctest.OutputChecker.__base_check_output = doctest.OutputChecker.check_output
doctest.OutputChecker.check_output = check_output


def make_test_globals():
    """Prepare global objects used in the doctests"""
    print("Prepare doctest globals", flush=True)
    # Test using a small data sample of 10000 random integers 0-255
    # with 16 dimensions
    hsne_data = np.random.randint(256, size=(10000, 16))
    tsne_data = np.random.randint(256, size=(2000, 16))
    # Create a sample hsne with 3 levels and
    # save this to a sample file
    hsne = nptsne.HSne(True)
    hsne.create_hsne(hsne_data, 3)
    file_name = "rnd10000x16.hsne"
    hsne.save(file_name)

    print("End prepare doctest globals", flush=True)
    return {
        "sample_hsne": hsne,
        "sample_scale0": hsne.get_scale(0),
        "sample_scale1": hsne.get_scale(1),
        "sample_scale2": hsne.get_scale(2),
        "sample_hsne_file": file_name,
        "sample_hsne_data": hsne_data,
        "sample_tsne_data": tsne_data,
        "sample_texture_tsne": nptsne.TextureTsne()
    }


if __name__ == "__main__":
    print("Starting doctest", flush=True)
    doctest.testmod(nptsne, verbose=True)
    # Doctest will not find the extension library
    doctest.testmod(nptsne.libs._nptsne,
                    verbose=True,
                    optionflags=REPORT_NDIFF | ELLIPSIS,
                    globs=make_test_globals())
