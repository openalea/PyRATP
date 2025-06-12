import numpy as np
from openalea.ratp.pyratp.skyvault import Skyvault
from openalea.ratp.pyratp.grid import Grid
from openalea.ratp.pyratp.vegetation import Vegetation
from openalea.ratp.pyratp.micrometeo import MicroMeteo
from openalea.ratp.pyratp.runratp import runRATP

import sys

def readveg(file):
    '''    
    read a file of points
    '''
    tab = np.recfromtxt(file,names=True)
    entity = tab['entity']
    x = tab['X']
    y = tab['Y']
    z = tab['Z']
    s = tab['s']
    n = tab['n'] 
    return entity, x, y, z, s, n,

def ratp(date):    
    vegfile='canratp_%s.txt'%(date)
    gridfile='grid_%s.grd'%(date)   
    vfnfile='entities_%s.vfn'%(date)
    skyfile='skyvaultsoc.skv'
    metfile='meteo_diffuseUnitSky1.mto'
    outfile='output_%s.txt'%(date)
    mapfile='mapratp_%s.txt'%(date)
    
    grid = Grid.read(gridfile)  
    entity, x, y, z, s, n = readveg(vegfile)
    grid,map = Grid.fill(entity, x, y, z, s, n, grid)
    vegetation = Vegetation.read(vfnfile)
    sky = Skyvault.read(skyfile)
    met = MicroMeteo.read(metfile)

    t = zip(map.keys(),map.values())
    np.savetxt(mapfile,t)

    res = runRATP.DoIrradiation(grid, vegetation, sky, met)

    np.savetxt(outfile,res)
    
if __name__=="__main__":
    ratp(sys.argv[1])