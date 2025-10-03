#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  1 09:27:16 2025

@author: cbozonnet
"""

import pandas as pd
import os
from openalea.ratp.RATP2VTK import PyRATPViewer, RATPVOXELS2PYVISTA, extract_dataframe
from openalea.ratp.grid import Grid

try:
    import pyvista as pv
except ImportError:
    raise ImportError(
    "PyVista is not installed. "
    "Please install it with: pip install pyvista"
    )

# data folder
datafolder = "data_pyratp"

# file names
grid_name = "grid3D-0_5m-vegestar.grd"
vegestar_file = "LOD6juin0.2.vgx"
coeff_allometric = 1
csv_name = "dfvox_20251001_093217.csv"

# read grid file
g = Grid()
g = Grid.read(os.path.join(datafolder, grid_name))

# fill up grid file from digitalisation (Vegestar file)
e, x, y, z, s, n = Grid.readVgx(os.path.join(datafolder, vegestar_file), coeff_allometric)
g, matching = Grid.fill_1(e, x, y, z, s, n, g)

# load data frame
df = pd.read_csv(os.path.join(csv_name ))

# viewer
PyRATPViewer(g, df)

