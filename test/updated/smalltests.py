""" Test python tutorial for use of Ratp
"""

import pandas
import os

from alinea.pyratp.skyvault import Skyvault
from alinea.pyratp.grid import Grid
from alinea.pyratp.vegetation import Vegetation
from alinea.pyratp.micrometeo import MicroMeteo
from alinea.pyratp.runratp import runRATP

def test_pommier_veg(datafolder):
    # lecture du fichier grille
    fn = os.path.join(datafolder, 'grid3Da_2004.grd')
    g = Grid()
    g = Grid.read(fn)

    # remplissage de la grille à partir d'un fichier VGX
    e, x, y, z, s, n = Grid.readVgx(os.path.join(datafolder, "aa2004petit.vgx"), 1)
    g, matching = Grid.fill_1(e, x, y, z, s, n, g)

    # lecture du fichier météo
    fn = os.path.join(datafolder, 'mmeteo082050_1h.mto')
    truesolartime = True # choix entre heure solaire ou heure locale
    met = MicroMeteo.read(fn, truesolartime)

    # lecture du fichier ciel
    fn = os.path.join(datafolder, 'skyvaultsoc.skv')
    sky = Skyvault.read(fn)

    # lecture du fichier vegetation
    fn = os.path.join(datafolder, 'vegetationa_2004.vfn')
    veg = Vegetation.read(fn)

    # Appel de RATP, simulation radiation
    res = runRATP.DoIrradiation(g, veg, sky, met)
        
    VegetationType,Iteration,day,hour,VoxelId,ShadedPAR,SunlitPAR,ShadedArea,SunlitArea, Pintercepted, Ptransmitted = res.T
    # 'PAR' is expected in  Watt.m-2 in RATP input, whereas output is in micromol => convert back to W.m2 (cf shortwavebalance, line 306)
    dfvox =  pandas.DataFrame({'VegetationType':VegetationType,
                        'Iteration':Iteration,
                        'day':day,
                        'hour':hour,
                        'VoxelId':VoxelId,
                        'ShadedPAR':ShadedPAR / 4.6,
                        'SunlitPAR':SunlitPAR / 4.6,
                        'ShadedArea':ShadedArea,
                        'SunlitArea': SunlitArea,
                        'Area': ShadedArea + SunlitArea,
                        'PAR': (ShadedPAR * ShadedArea + SunlitPAR * SunlitArea) / (ShadedArea + SunlitArea) / 4.6, 
                        'intercepté' : Pintercepted,
                        'transmis' : Ptransmitted,
                        })
    return dfvox

if __name__ == "__main__":
    # dossier contenant les données
    datafolder = os.path.join("test", "updated", "data")
    print(test_pommier_veg(datafolder))
    
    print('--- END ---')