"""Doctests for nptsne"""
import doctest
from doctest import REPORT_NDIFF, ELLIPSIS
from doctest import DocTestRunner
import numpy as np
import nptsne
import nptsne.hsne_analysis
import nptsne.libs._nptsne
import os

_skip = object()
SKIP_IN_CI = doctest.register_optionflag('SKIP_IN_CI')
is_ci = os.environ.get('CI', 'false').lower() == 'true'
glob_total_skipped = 0

if is_ci:
    print("CI detected")
    
#  Monkey patch the DocTestRunner to filter SKIP_IN_CI examples
doctest_base_run = DocTestRunner.run
def doctest_patch_run(self, test, compileflags=None, out=None, clear_globs=True):
    global glob_total_skipped
    if is_ci:
        # Filter out any SKIP_IN_CI examples on the CI
        not_skipped_examples = [example for example in test.examples if SKIP_IN_CI not in example.options ]
        tot_skipped = len(test.examples) - len(not_skipped_examples)
        glob_total_skipped += tot_skipped
        if tot_skipped:
            print(f"Skipping {tot_skipped} test examples in CI")
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
        "sample_texture_tsne": nptsne.TextureTsne(),
        "sample_texture_tsne_extended": nptsne.TextureTsneExtended()
    }


if __name__ == "__main__":
    print("Starting doctest", flush=True)
    #failures_nptsne, tests_nptsne = doctest.testmod(nptsne, verbose=True)
    #failures_hsne_analysis, tests_hsne_analysis = doctest.testmod(nptsne.hsne_analysis, verbose=True)
    # Must explicitly test the extension library
    failures_nptsne_ex, tests_nptsne_ex = doctest.testmod(nptsne,
                    verbose=True,
                    optionflags=REPORT_NDIFF | ELLIPSIS,
                    globs=make_test_globals())
    total_failures =  failures_nptsne   # + failures_hsne_analysis + failures_nptsne_ex 
    if glob_total_skipped:
        print(f"{glob_total_skipped} tests were skipped in the CI environment.")
    if total_failures:
        exit(1)
    exit(0)