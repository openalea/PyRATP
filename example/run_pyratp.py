""" 
Test python tutorial for use of Ratp

This programs showcases several uses:
    1) create and fill RATP grid either from full digitalisation (Vegestar file),
        or from a list of voxel coordinates and leaf area values
    2) read meteo, skyvault and vegetation files
    3) run either the full RATP program, or only the Irradation part
    4) export a vtk file at given time and variable
    5) plot some global variable at tree scales
    
"""

import pandas
import os
import numpy as np
from openalea.ratp.skyvault import Skyvault
from openalea.ratp.grid import Grid
from openalea.ratp.vegetation import Vegetation
from openalea.ratp.micrometeo import MicroMeteo
from openalea.ratp.runratp import runRATP
from openalea.ratp.RATP2VTK import RATPVOXELS2VTK
import matplotlib.pyplot as plt

######################## set up inputs #############################

# data folder
datafolder = "data_pyratp"

# file names
grid_vegestar = "grid3D-0_5m-vegestar.grd"
vegestar_file = "LOD6juin0.2.vgx"
coeff_allometric = 1

grid_voxel = 'grid3D-0_5m.grd'
voxel_file = 'leafarea-0_5m.txt'

meteo_file = 'Forcage_sansTROU1_PARdirPOSITIF.mto'
skyvault_file = 'skyvaultsoc.skv'
vegetation_file = 'vegetationa_2004.vfn'

# options
do_all = True # True if you want to run the full code - False for Irradaition only
run_from_vegestar = True # True to run based on vegestar file - False from voxels

# data extraction to VTK
DayToExtract = 192
HourToExtract = 12
ColToExtract = 'PAR'

# variable to plot
var2plot = 'TreePhotosynthesis'
y_label = 'TreePhotosynthesis [mol CO2 / s / m2]'

#############################################################

############ 1) create and fill grids ################

if run_from_vegestar:
    # read grid file
    fn = os.path.join(datafolder, grid_vegestar)
    g = Grid()
    g = Grid.read(fn)
    
    # fill up grid file from digitalisation (Vegestar file)
    e, x, y, z, s, n = Grid.readVgx(os.path.join(datafolder, vegestar_file), coeff_allometric)
    g, matching = Grid.fill_1(e, x, y, z, s, n, g)
    
else:
    # read grid file
    fn = os.path.join(datafolder, grid_voxel)
    g = Grid()
    g = Grid.read(fn)
    
    # Fill up the grid
    txtpath = os.path.join(datafolder, voxel_file)
    data = np.loadtxt(txtpath, delimiter='\t', skiprows=1)  # Adjust delimiter as needed
    # Extracting the different variables
    e, x, y, z, s, n = data[:, 0], data[:, 1], data[:, 2], data[:, 3], data[:, 4], data[:, 5]
    # fill the grid
    g, matching = Grid.fill_1(e, x, y, z, s, n, g)

############ 2) read meteo, skyvault and vegetation files ################

# lecture du fichier météo
#fn = os.path.join(datafolder, 'mmeteo082050_1h.mto')
fn = os.path.join(datafolder, meteo_file)
truesolartime = True # choix entre heure solaire ou heure locale
met = MicroMeteo.read(fn, truesolartime)

# lecture du fichier ciel
fn = os.path.join(datafolder, skyvault_file )
sky = Skyvault.read(fn)

# lecture du fichier vegetation
## vegetationa_2004.vfn pommierFct-utf8.vfn
fn = os.path.join(datafolder, vegetation_file)
veg = Vegetation.read(fn)

############ 3) run code ################

if not do_all:
    # Radiation only
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
else:       
    # RATP: doALL 
    res_spatial, res_tree = runRATP.DoAll(g, veg, sky, met)
    
    dfvox =  pandas.DataFrame({'VegetationType':res_spatial[:,0],
                        'Iteration':res_spatial[:,1],
                        'day':res_spatial[:,2],
                        'hour':res_spatial[:,3],
                        'AirTemperature':res_spatial[:,4],
                        'VoxelId':res_spatial[:,5],
                        'ShadedTemp':res_spatial[:,6],
                        'SunlitTemp':res_spatial[:,7],
                        'STARDirect':res_spatial[:,8],
                        'STARSky':res_spatial[:,9],
                        'ShadedPhoto':res_spatial[:,10],
                        'SunlitPhoto':res_spatial[:,11],
                        'ShadedTranspi':res_spatial[:,12],
                        'SunlitTranspi':res_spatial[:,13],
                        'ShadedArea':res_spatial[:,14],
                        'SunlitArea':res_spatial[:,15],
                        'ShadedGs':res_spatial[:,16],
                        'SunlitGs':res_spatial[:,17],
                        'ShadedAbsordbedPAR':res_spatial[:,18] / 4.6,
                        'SunlitAbsordbedPAR':res_spatial[:,19]/ 4.6,
                        'ShadedAbsordbedNIR':res_spatial[:,20] / 4.6,
                        'SunlitAbsordbedNIR':res_spatial[:,21] / 4.6,
                        'Area': res_spatial[:,14] + res_spatial[:,15],
                        'PAR': (res_spatial[:,18] * res_spatial[:,14] + res_spatial[:,19] * res_spatial[:,15]) / (res_spatial[:,14] + res_spatial[:,15])/4.6, 
                        })
    
    dftree = pandas.DataFrame({'Iteration':res_tree[:,0],
                           'day':res_tree[:,1],
                           'hour':res_tree[:,2],
                           'VegetationType':res_tree[:,3],
                           'TotalIrradiation':res_tree[:,4],
                           'AirTemperature':res_tree[:,5],
                           'TreePhotosynthesis':res_tree[:,6],
                           'TreeTranspiration': res_tree[:,7],
                           'LeafSurfaceArea': res_tree[:,8],
                           })
    
############ 4) export a vtk file at given time and variable ################

outputname = 'data_'+ColToExtract+'_day'+str(DayToExtract)+'hour'+str(HourToExtract)+'.vtk'

# Filter the DataFrame for the specified day and hour
filtered_df = dfvox[(dfvox['day'] == DayToExtract) & (dfvox['hour'] == HourToExtract)]

# format data to be written
extracted_df = filtered_df[[ColToExtract, 'VegetationType', 'VoxelId',]]

# Convert the DataFrame to a NumPy array
extracted_array = extracted_df.to_numpy()

# Transpose the array to orient it along the rows
extracted_array_transposed = extracted_array.T

# write VTK file
RATPVOXELS2VTK(g, extracted_array_transposed,ColToExtract,outputname)

##################  5) plot some global variable at tree scales  #############

plt.figure(1)
plt.plot(dftree['Iteration'],dftree[var2plot])
plt.xlabel('Iteration')
plt.ylabel(y_label)
