#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 14:23:22 2025

@author: cbozonnet
"""

##### a program to view VTK files from python using PyVista ######

## INSTALL PYVISTA BEFORE RUNNING THIS CODE
## USING in a terminal :  pip install pyvista
## within you pyratp environment

import pyvista as pv

# Read the VTK file 
grid = pv.read('data_PAR_day192hour12.vtk')

# Print available arrays (scalars/vectors)
print(grid.array_names)

# threshold scalar field to remove non-existing voxels 
thresholded = grid.threshold(value=-100, scalars='PAR_entity_1')

# Plot with scalars colored
plotter = pv.Plotter()
plotter.add_mesh(thresholded, cmap='viridis')
plotter.show()
