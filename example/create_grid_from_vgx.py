#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 11:54:17 2025

@author: cbozonnet
"""
import os
from openalea.ratp.grid import Grid
import numpy as np

######################## inputs ###################

datafolder = "data_pyratp"
vegestar_file = "LOD6juin0.2.vgx"
coeff_allometric = 1

grid_file_name = os.path.join(datafolder,"gridfromVGX_0_5m.grd")

dx= dy= dz = 0.5 # in m

# grid parameters
lat = 44.00    # latitude
long = 0.0     # longitude
timezone = 0.0 # timezone
angle = 0.0    # angle between x+ axis and North
offset = int(0.0)   # offset between canopy unit along Y-axis
nveg = int(1)       # number of vegetation entities
nwave = int(2)     # number of wavebands
reflect = [0.075, 0.2]  # soil reflectance for each waveband

####################### code #######################

# read vgx file (obtained either from digit or plantGL viewer)
e, x, y, z, s, n = Grid.readVgx(os.path.join(datafolder, vegestar_file), coeff_allometric)

# compute bounding box dimensions
deltaX = max(x)-min(x)
deltaY = max(y)-min(y)
deltaZ = max(z)-min(z)

# grid dimensions
nx = int(np.ceil(deltaX/dx)) # round to higer value and turn to integer
ny = int(np.ceil(deltaY/dy))
nz = int(np.ceil(deltaZ/dz))

vec_dz = [dz] * int(nz+1) # z sizes vector

# account for extra space along x
extrax = dx*nx - deltaX
xo = min(x)- (extrax / 2.)

# account for extra space along y
extray = dy*ny - deltaY
yo = min(y)- (extray / 2.)

# account for extra space along z
extraz = dz*nz - deltaZ
zo = min(z)- (extraz / 2.)

####################### gather values and save ##########

# Gather all data
lines = [
    f"{nx} {ny} {nz+1}",  # x, ny, nz
    f"{dx} {dy} {' '.join(map(str, vec_dz))}",  # voxels size in x y z
    f"{xo} {yo} {-zo}",  # min box corner
    f"{lat} {long} {timezone}",  # lat, long, timezone
    str(angle),  # angle
    str(offset),  # offset
    str(nveg),  # nveg
    f"{nwave} {' '.join(map(str, reflect))}"  # number of waveband and band reflection values
]

# Write to file
with open(grid_file_name, 'w') as f:
    f.write('\n'.join(lines))

########################## verification (optional) #########

fn = os.path.join(grid_file_name)
g = Grid()
g = Grid.read(fn)

g, matching = Grid.fill_1(e, x, y, z, s, n, g)