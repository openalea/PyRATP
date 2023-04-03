from alinea.pyratp.micrometeo import MicroMeteo
import numpy

def test_read():
    fn ='mmeteo082050_1h.mto'
    met = MicroMeteo.read(fn)
    expected = numpy.array([[234, 11, 2, 2, 0, 0, 0, 33.1, 33.1, 3288, 54, 1.1, 1],
       [234, 12, 2, 2, 0, 0, 0, 20.1, 20.1, 3288, 54, 1.1, 1]])
    numpy.testing.assert_allclose(met.tabmeteo, expected, atol=0.01)
    return met
    
def test_initialise():
    
    met = MicroMeteo.initialise(doy=1, hour=12, Rglob=1, Rdif=1, Ratmos=1, Tsol=20, Tair=20, Eair=1, CO2air=1, Wind=1, HRsol=1)
    expected = numpy.array([[1, 12, 1, 1, 1, 20, 20, 1, 1, 1, 1]])
    numpy.testing.assert_allclose(met.tabmeteo, expected, atol=0.01)
    
    met = MicroMeteo.initialise(doy=1, hour=12, Rglob=[1,2,3], Rdif=[1,1,0], Ratmos=1, Tsol=20, Tair=20, Eair=1, CO2air=1, Wind=1, HRsol=1)
    expected = numpy.array([[1, 12, 1, 1, 2, 1, 3, 0, 1, 20, 20, 1, 1, 1, 1]])
    numpy.testing.assert_allclose(met.tabmeteo, expected, atol=0.01)
    
    met = MicroMeteo.initialise(doy=[1,2], hour=[12,13], Rglob=[[1,2],[1,3]], Rdif=[[1,1],[1,0]], Ratmos=[10,10], Tsol=[20,20], Tair=[20,20], Eair=[1,1], CO2air=[1,1], Wind=[1,1], HRsol=[1,1])
    expected = numpy.array([[1, 12, 1, 1, 2, 1, 10, 20, 20, 1, 1, 1, 1],
                            [2, 13, 1, 1, 3, 0, 10, 20, 20, 1, 1, 1, 1]])
    numpy.testing.assert_allclose(met.tabmeteo, expected, atol=0.01)
    
    return met
    