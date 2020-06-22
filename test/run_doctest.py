import nptsne
import numpy as np

def make_test_globals():

    # Test using a small data sample of 10000 random integers 0-255
    # with 16 dimensions    
    data = np.random.randint(256, size=(10000,16))
    # Create a sample hsne with 3 levels and
    # save this to a sample file    
    hsne = nptsne.HSne(True)
    hsne.create_hsne(data, 3)
    file_name = "rnd10000x16.hsne"
    hsne.save(file_name)
    
    return {
        "sample_hsne": hsne,
        "sample_scale0": hsne.get_scale(0),      
        "sample_scale1": hsne.get_scale(1), 
        "sample_scale2": hsne.get_scale(2),         
        "sample_hsne_file": file_name,
        "sample_data": data
        
    }

if __name__ == "__main__":
    import doctest
    from doctest import REPORT_NDIFF,ELLIPSIS
    doctest.testmod(nptsne, verbose=True)
    # Doctest will not find the extension library
    import nptsne.libs._nptsne
    doctest.testmod(nptsne.libs._nptsne, 
        verbose=True, 
        optionflags=REPORT_NDIFF|ELLIPSIS, 
        globs = make_test_globals())