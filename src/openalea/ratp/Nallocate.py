import numpy as np
import os
import shutil
import sys
import platform

## Parametres a sortir dans un widgets: nb voxels pour intialiser PAR_voxmean, aN et bN, nb de jours pour moyenner

class Nallocate(object):
    """
    """
    def __init__(self, *args, **kwds):
        """

        """
    @staticmethod
    def N_distrib(grid,tabRay,aNa,bNa):
        """ Set the amount of Nitrogen per voxel according to the PAR absorbed ...
        ... input data:
            ... grid: RATP grid variable
            ... taRay: PAR received by each voxel computed from the do_irradiation() method
            ... aNa: slope of the linear relationship between Nitrogen content (g/m2) and PAR absorbed
            ... bNa: intercept of the linear relationship between Nitrogen content (g/m2) and PAR absorbed
        ... output data:
            ... grid: updated RATP grid variable
        """

        path = 'c:/tmpRATP' #if platform.system() == 'Windows' else '/tmp/tmpRATP'
##        if os.path.isdir(path):
##            shutil.rmtree(path)
##        os.mkdir(path)
##        os.mkdir(path+"/Resul_N")

##       print(grid.n_detailed', grid.n_detailed, type(grid.n_detailed), "grid.n_detailed.shape",grid.n_detailed.shape
##       print grid.n_detailed[0]

        nbvox = grid.njx*grid.njy*grid.njz
        nbvox=nbvox.astype(int)

        tabRayTranspose = np.transpose(tabRay)
##         print'TabRayTranspose', tabRayTranspose[0,:]

        k = tabRayTranspose[4] #num de voxel, de 1 a k
        k = k.astype(int)
##        print(k = ',k
# ### indices to modify if tabray outputs are modified
        PARi0 = tabRayTranspose[5]
        PARi1 = tabRayTranspose[6]
        surf0 = tabRayTranspose[7]
        surf1 = tabRayTranspose[8]

        PARi2= (PARi0*surf0 + PARi1*surf1)/(surf0+surf1) #PAR total reconstitue a partir des PAR ombre et lumiere

        PAR_voxmean = np.zeros(nbvox) #tableau contenant la valeur moyenne de PAR cumule journalier par voxel
## Defini a 1300 = nb de voxel pour une grille de 40 x 40 x 40 voxels => changer ce nombre  sichangement de grille!!!

##        print(k', k
        ij=0
        for ik in range(1,max(k)+1): #boucle sur les voxels
            n_celvox = (k == [ik]).nonzero() #sous echantillon correspondant a un meme voxel
            #print n_celvox
            PARvox = PARi2[n_celvox].sum(axis=0)
            PARvox = PARvox/7 # moyenne (sur 7 jours) du PAR cumule journalier
##            print(PARi2', ik, PARi2[n_celvox]
##             print(PARvox, ik', PARvox, ik
            PAR_voxmean[ij]=PARvox #Ajout de la valeur a un vecteur pour le PAR total
            ij=ij+1

        #Calculs azote surfacique par relations empiriques
        #coef juillet 1996 noyer Leroux et al. 1999 TP 181-188
##            aNa = 0.141
##            bNa= 0.46
        #coef septembre 1996 noyer
##            aNa = 0.179
##            bNa= 0.72
        #coef juillet 1996 noyer Leroux et al. 1999 TP 481-492
##            aNa = 0.14
##            bNa = 0.40
##            #coef Pommier Fuji/Braeburn Massonnet et al. 2008 TP
##        aNa = 0.10 # 0.07142857 #0.10
##        bNa = 0.81 # 0.57142857 #0.81

##        print(PAR_voxmean',PAR_voxmean, type(PAR_voxmean),np.size(PAR_voxmean)
        PAR_voxmean = PAR_voxmean*1800*1e-6 #micromol m-2 s-1 en mol m-2 jour-1

        grid.n_detailed[0] = aNa*PAR_voxmean+bNa
        #print "np.size(grid.n_detailed)",np.size(grid.n_detailed),

        final = np.append(grid.n_detailed[0],PAR_voxmean, axis=1)
##        np.savetxt(path+"/Resul_N"+'/n_detailed.txt',grid.n_detailed[0],'%.6e')
        np.savetxt(path+'/final_N.txt',final,'%.6e')
##         print(grid.n_detailed', grid.n_detailed
        print("N ALLOCATION OK")
        return grid





