# Header
#

"""

"""

from openalea.ratp import pyratp
import numpy as np
import math
import os

class MicroMeteo:
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass

    @staticmethod
    def read(filename,truesolartime):
        chemin=str(os.path.dirname(filename))
        micrometeo = pyratp.micrometeo
        listVegeNom = []
        f = open(filename)
        nbli = len(f.readlines())-1
        micrometeo.nbli=nbli
        f.close()
        col = np.int32(13)

        micrometeo.tabmeteo = np.ones(micrometeo.nbli*col).reshape(micrometeo.nbli ,col)   #17/04/2012 NGAO Set to one for HRsol default value ! 

        f = open(filename)
        f.readline()
        li=[]
        for i in range(nbli):
            li=_read(f)
            for ii in range(len(li)):
                micrometeo.tabmeteo[i,ii] = li[ii]
        f.close()
        micrometeo.truesolartime=truesolartime
        print("MICROMETEO OK")
        return micrometeo

    @staticmethod
    def initialise(doy=1, hour=12, Rglob=1, Rdif=1, Ratmos=1, Tsol=1, Tair=1, Eair=1, CO2air=1, Wind=1, HRsol=1,truesolartime=False):
        """ Create a micrometeo object from data given in arguments
        
        Parameters:
        - doy : day of year
        - hour : decimal hour (0-24)
        - Rglob : [list of] global (direct + diffuse) radiation [for successive wavelength bands] (W.m-2)
        - Rdif : [list of] direct/diffuse radiation ratio [for successive wavelength bands] (0-1)
        - Ratmos : atmospheric thermal radiation (W.m-2)
        - Tsol, Tair : soil and air temperature above the canopy (degree celcius)
        - Eair: water vapour pressure in the air (Pa)
        - CO2air: CO2 partial pressure in the air (Pa)
        - Wind: wind speed above the canopy (m.s-1)
        - HRsol: Relative Soil Humidity (0-1)
        - truesolartime: with hour is true solar time or local time
        
        Note that for the first wavelength should be PAR if phothosysnthesis is to be computed, and that all wavelength are summed for Shortwave energy ballance.
        
        All args could be listed to provide data for several dates at a time.
        
        """
        
        micrometeo = pyratp.micrometeo
        micrometeo.nbli = np.array(doy).size # handle both list and scalar args for day
        
        # cast scalar or  flat lists like objects to list of list for glob and dif
        nbh = np.array(hour).size
        if np.array(Rglob).size == 1:# input = one date and one wavelength
            Rglob = [[Rglob]]    
        if np.array(Rglob).size > 1 and nbh == 1:# input = one date and n wavelength
            Rglob = [Rglob]
        if np.array(Rglob).size > 1 and nbh > 1 and np.array(Rglob[0]).size == 1:# input = n date and one wavelength
            Rglob = [[v] for v in Rglob]
        if np.array(Rdif).size == 1:# input = one date and one wavelength
            Rdif = [[Rdif]]    
        if np.array(Rdif).size > 1 and nbh == 1:# input = one date and n wavelength
            Rdif = [Rdif]
        if np.array(Rdif).size > 1 and nbh > 1 and np.array(Rdif[0]).size == 1:# input = n date and one wavelength
            Rdif = [[v] for v in Rdif]

        nblo = len(Rglob[0])
        
        glob_names = ['Rglob' + str(i) for i in range(nblo)]
        dif_names = ['Rdif' + str(i) for i in range(nblo)]
        Rcols = list(sum(zip(glob_names, dif_names),()))
        cols = ['doy', 'hour'] + Rcols + ['Ratmos', 'Tsol', 'Tair', 'Eair', 'CO2air', 'Wind', 'HRsol']
        col = np.int32(len(cols))
        micrometeo.tabmeteo = np.ones(micrometeo.nbli * col).reshape(micrometeo.nbli ,col) 
        args = locals()
        args.update({glob_names[i]: [Rglob[h][i] for h in range(nbh)] for i in range(nblo)})
        args.update({dif_names[i]: [Rdif[h][i] for h in range(nbh)] for i in range(nblo)})
        for i,col in enumerate(cols):
            micrometeo.tabmeteo[:,i] = args[col]
        
        micrometeo.truesolartime=truesolartime
        return micrometeo
        
def _read(f):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l= l.split('\n')[0] # remove chr(13)
    #l = l.split(' ')
    l = l.replace('\t',' ').split(' ') 
    #l = filter(None,l)
    l = [x for x in l if bool(x)==True]
    for j in range(len(l)):
        l[j]=np.float32(l[j])
    return l

