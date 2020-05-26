#!/usr/bin/env python3

# The nptsne package and the hsne_analysis navigation support
from nptsne import hsne_analysis
from ModelController import ModelController
import sys
import matplotlib

matplotlib.use("Qt5Agg")
# Handle running this via Windows Remote Desktop (i.e. no GPU)
def get_default_embedding_type():
    """GPU embedder will not work on remote desktop """
    default_embedder_type = hsne_analysis.EmbedderType.GPU
    if sys.platform == 'win32':
        # pip install pywin32
        try:
            import win32api
            isWindows = True
            SM_REMOTESESSION = 0x1000
            if 1 == win32api.GetSystemMetrics(SM_REMOTESESSION):
               default_embedder_type = hsne_analysis.EmbedderType.CPU 
        except ImportError as exception:
            print(exception, exception.mess)
            print("Assuming GPU")
    return default_embedder_type       

default_embedder_type = get_default_embedding_type()
print("Embedder: ", default_embedder_type)

if __name__ == "__main__":
    modelController = ModelController(default_embedder_type)
    modelController.run()
