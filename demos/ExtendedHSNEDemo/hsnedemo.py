#!/usr/bin/env python3

"""A demo of HSNE analysis in python using the hsne_analysis from the nptsne package
"""
import sys

# The nptsne package and the hsne_analysis navigation support
from nptsne import hsne_analysis
import matplotlib
from ModelController import ModelController

matplotlib.use("Qt5Agg")
# Handle running this via Windows Remote Desktop (i.e. no GPU)
def get_default_embedding_type():
    """GPU embedder will not work on remote desktop, try to catch that on windows at least"""
    embedder_type = hsne_analysis.EmbedderType.GPU
    if sys.platform == "win32":
        # pip install pywin32
        try:
            import win32api  # pylint: disable=import-outside-toplevel

            SM_REMOTESESSION = 0x1000  # pylint: disable=invalid-name
            if (
                win32api.GetSystemMetrics(SM_REMOTESESSION) == 1
            ):  # pylint: disable=c-extension-no-member
                embedder_type = hsne_analysis.EmbedderType.CPU
        except ImportError as exception:
            print(str(exception))
            print("Assuming GPU")
    return embedder_type


default_embedder_type = get_default_embedding_type()
print("Embedder: ", default_embedder_type)

if __name__ == "__main__":
    modelController = ModelController(default_embedder_type)
    modelController.run()
