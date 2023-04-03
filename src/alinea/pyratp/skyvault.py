# Header(
#

"""

"""

from alinea.pyratp import pyratp

#import pyRATP
import numpy as np
import math

elevations46 = [9.23] * 10 + [10.81] * 5 + [26.57] * 5 + [31.08] * 10 + [47.41] * 5 + [52.62] * 5 + [69.16] * 5 +  [90]
azimuths46 = [12.23, 59.77, 84.23, 131.77, 156.23, 203.77, 228.23, 275.77, 300.23, 347.77, 36, 108, 180, 252, 324, 0, 72, 144, 216, 288, 23.27, 48.73, 95.27, 120.73,167.27, 192.73, 239.27, 264.73, 311.27, 336.73, 0, 72, 144, 216, 288, 36, 108, 180, 252, 324, 0, 72, 144, 216, 288, 180]
omegas_46 = [0.1355] * 10 + [0.1476] * 5 + [0.1207] * 5 + [0.1375] * 10 + [0.1364] * 5 + [0.1442] * 5 + [0.1378] * 5 + [0.1196]
weights_soc_46 = [0.0043] * 10 + [0.0055] * 5 + [0.014] * 5 + [0.0197] * 10 + [0.0336] * 5 + [0.0399] * 5 + [0.0495] * 5 + [0.0481]
weights_uoc_46 = [0.007] * 10 + [0.0086] * 5 + [0.017] * 5 + [0.0224] * 10 + [0.0317] * 5 + [0.036] * 5 + [0.0405] * 5 + [0.0377]


class Skyvault(object):
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass

    @staticmethod
    def read(filename):
        skyvault = pyratp.skyvault
        listGene = []
        f = open(filename)
        skyvault.ndir=int(f.readline().strip().split('\t')[0])
        skyvault.hmoy=np.zeros(skyvault.ndir)
        skyvault.azmoy=np.zeros(skyvault.ndir)
        skyvault.omega=np.zeros(skyvault.ndir)
        skyvault.pc=np.zeros(skyvault.ndir)
        for n in range(skyvault.ndir):
            listGene.append(f.readline().strip().split('\t'))
        tabGene=np.array(listGene)
        tabGene = np.cast['float64'](tabGene)
        skyvault.hmoy=np.transpose(tabGene)[0]*math.pi / 180
        skyvault.azmoy=np.transpose(tabGene)[1]*math.pi / 180
        skyvault.omega=np.transpose(tabGene)[2]
        skyvault.pc=np.transpose(tabGene)[3]
        print("SKYVAULT OK")
        f.close()
        return skyvault

    @staticmethod
    def initialise(hmoy=elevations46, azmoy=azimuths46, omega=omegas_46, pc=weights_soc_46):
        """ Create a skyvault object from arguments. One value per direction of incidence
        
        Parameters:
            - hmoy: Elevation angle (degrees) pointing to the center of a sky fraction
            - azmoy: Azimuth angle (degrees) pointing to the center of a sky fraction
            - omega: Solid angle associated to the direction of incidence
            - pc: Relative contribution of the sky fraction to the sky illumination
            
        """
        skyvault = pyratp.skyvault
        skyvault.ndir = int(np.array(hmoy).size) # handle both list and scalar args for day
        skyvault.hmoy=np.zeros(skyvault.ndir)
        skyvault.azmoy=np.zeros(skyvault.ndir)
        skyvault.omega=np.zeros(skyvault.ndir)
        skyvault.pc=np.zeros(skyvault.ndir)
        skyvault.hmoy[:] = np.radians(np.array(hmoy))
        skyvault.azmoy[:] = np.radians(np.array(azmoy))
        skyvault.omega[:] = np.array(omega)
        skyvault.pc[:] = np.array(pc)
        
        return skyvault