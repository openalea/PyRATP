from alinea.pyratp.vegetation import Vegetation
import numpy

def test_read():
    fn ='vegetationa_2004.vfn'
    veg = Vegetation.read(fn)
    

    assert veg.nbincli[1] == 9
    assert veg.nblo[1] == 2
    
    return veg
    
def test_initialise():

    veg = Vegetation.initialise()
    assert veg.nbincli[0] == 5
    assert veg.nblo[0] == 1
    assert veg.agspar[0,2] == 1
    
    veg = Vegetation.initialise(nblomin=2)
    assert veg.nblo[0] == 2
    
    return veg