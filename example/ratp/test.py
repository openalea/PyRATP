###################
# TEST RATP module
###################
import os
from openalea.ratp.pyratp import ratp
from numpy import *

njx = 2
njy = 3
njz = 4
size_box_x = 4.   
size_box_y = 5.   
size_box_z = 3.75

nentmax = pyratp.grid3d.nentmax = 1
pyratp.grid3d.nveg=24
pyratp.grid3d.g3d_create(njx,njy,njz,size_box_x,size_box_y,size_box_z)

xlad = array ([[ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1., 1.,1.,1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.]])
for i in range(size(xlad[0])):
    pyratp.grid3d.leafareadensity[0][i]=xlad[0][i]

kxyz = array([[[1, 2, 3, 4, 1],[5, 6, 7, 8, 2],[9, 10, 11, 12, 3]],[[13, 14, 15, 16, 4],[17, 18, 19, 20, 5],[21, 22, 23, 24, 6]]])
numx = array([1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2])
numy = array([1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3])
numz = array([1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4])


for i in range(size(kxyz[:,0,0])):
    for j in range(size(kxyz[0,:,0])):
        for k in range(size(kxyz[0,0,:])):
            pyratp.grid3d.kxyz[i,j,k]=kxyz[i,j,k]

for i in range(size(numx)):
    pyratp.grid3d.numx[i]= numx[i]
    pyratp.grid3d.numy[i]= numy[i]
    pyratp.grid3d.numz[i]= numz[i]



SPEC="PP1"                   
pyratp.skyvault.sv_read('skyvault.PP1')   
#pyratp.vegetation_types.vt_read(pyratp.grid3d.nent,'.','SpeciesPlano.spc')   
#pyratp.diffscatt_interception.do_all()   
