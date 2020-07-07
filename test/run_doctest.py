"""Doctests for nptsne"""
import doctest
from doctest import REPORT_NDIFF, ELLIPSIS
from doctest import DocTestRunner
import numpy as np
import nptsne
import nptsne.libs._nptsne
import os

_skip = object()
SKIP_IN_CI = doctest.register_optionflag('SKIP_IN_CI')
is_ci = os.environ.get('CI', 'false').lower() == 'true'

if is_ci:
    print("CI detected")
#  Monkey patch the DocTestRunner to handle extra SKIP_IN_CI

doctest_base_run = DocTestRunner.run
def doctest_patch_run(self, test, compileflags=None, out=None, clear_globs=True):
    if is_ci:
        # Filter out any SKIP_IN_CI examples on the CI
        not_skipped_examples = [example for example in test.examples if SKIP_IN_CI not in example.options ]
        if len(test.examples) > len(not_skipped_examples):
            print(f"Skipping {len(test.examples) - len(not_skipped_examples)} test examples in CI")
        test.examples = not_skipped_examples
    doctest_base_run(self, test, compileflags=None, out=None, clear_globs=True)

DocTestRunner.run = doctest_patch_run   

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
