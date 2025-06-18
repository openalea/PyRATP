# Header
#

"""

"""

from . import pyratp
#import pyRATP
import numpy as np
import math
import os
pj = os.path.join



class Vegetation(object):
    """
    """
    
    # default parameters
    default = {'mu': 1,
               'distinc': [0.2] * 5, # uniform dist for 5 classes
               'rf' : [0.1],
               'Aga': (0.01, 0.0071),
               'AgsN': (0, 6.32e-3), 
               'AgsPAR_function': 2,
               'AgsPAR': [1.79467, 131.83, 1. ,  1322.98],
               'AgsCA_function': 1,
               'AgsCA': [2.32e-4, -4.02e-2, 2.07],
               'AgsLT_function' : 5,
               'AgsLT': [0.97498, 1., 25.01445, 11.150015],
               'AgsVPD': (-0.266e-3, 1.3764, 1500.),
               'AVcmaxN': (20.0, 6.),
               'AJmaxN': (52.0, 15.),
               'ARdN':(0.25, 0.05),
               'IsMine': 0,
               'epm' : 1}
               
    
    def __init__(self, *args, **kwds):
        """
        """
        pass

    @staticmethod
    def initialise(entities=[{}], nblomin=1, pervoxel=False, distribvox=[]):
        """  Setup a vegetation object from arguments
        
            Parameters : 
            - entities : a list of entity parameters dict. Each entity dict can contain:
                - 'mu': Parameter of foliage dispersion within voxels (1: random, <1: clumped; >1: regular)
                - 'distinc' : relative proportions of leaf area for angle class i (0 =< i < len(distinc)). Angle class i is for leaf inclination (angle between x-axis and leaf) between i * (90 / nclass) and (i+1) * (90 / nclass)
                - 'rf' : list of reflectance for the different wavelength bands
                - 'Aga' : 2-tuple of parameters for leaf boundary conductance ga: ga = Aga[0] * wind_speed + Aga[1]
                - 'AgsN': 2-tuple of parameters for maximal stomatal conductance gs as a funtion of nitrogen: 
                          gsmax(s.m-1) = AgsN[0] * Na(g.m-2) + AgsN[1]
                - 'AgsPAR_function': integer code that select for a gs_reduction=f(PAR) function (see details below)
                - 'AgsPAR': parameters for the AgsPAR function (see details below)
                - 'AgsCA_function' : integer code that select for a gs reduction function = f(pCO2 (Pa)) (see details)
                - 'AgsCA': parameters for the AgsCA function (see details below)
                - 'AgsLT_function' : integer code that select for a gs reduction function = f(Leaf_Temperature) (see details)
                - 'AgsLT': parameters for the AgsLT function (see details below)
                - 'AgsVPD' : 3-tuple of parameters for the gs_reduction as a function of VPD (Pa):
                            fgs = AgsVPD[0] *  max(AgsVPD[2], VPD) + AgsVPD[1]
                - 'AVcmaxN': 2-tuple of parameters for Vcmax25deg=f(N) function. 
                            Vcmax25(micromol CO2 m-2 s-1) = AVcmaxN[0] * Na (g m-2) + AVcmaxN[1]
                - 'AJmaxN': 2-tuple of parameters for Jmax25deg=f(N) function. 
                            Jmax25(micromol e m-2 s-1) = AJmaxN[0] * Na (g m-2) + AJcmaxN[1]
                - 'ARdN' : 2-tuple of parameters for dark respiration rate at 25deg=f(N) function. 
                            Rd25(micromol CO2 m-2 s-1) = ARdN[0] * Na (g m-2) + ARdN[1]
                - 'IsMine' : enable mine damage (0 = no mine)
                - 'epm' : mine damage : product of leaf thickness * mine damage perimeter

            - nblomin : number of wavelength band given in MicroMeteo
            - pervoxel : if angle distrib is per voxel or global (ajout mwoussen 06/04/22)
            
            Details: 
                - gs = gsmax(Na) * fgsPAR * fgsCA * fgsLT *fgsVPD
                
                - Ags_PAR_function code allows for selecting one of the following function:
                    - 1: 2nd order polynomial function fgs = AgsPAR[0] * PAR**2 + AgsPAR[1] * PAR + AgsPAR[2]
                    - 2: hyperbola  fgs= (AgsPAR[0] * PAR + AgsPAR[1]) / (AgsPAR[2] * PAR + AgsPAR[3])
                    - 3 : fgs= (AgsPAR[0] * PAR**2 + AgsPAR[1] * PAR + AgsPAR[2]) / (AgsPAR[3] * PAR**2 + AgsPAR[4] * PAR + AgsPAR[5])
                    - 4 : fgs = (AgsPAR[0] *  sqrt(PAR) + AgsPAR[1]) / (AgsPAR[2] * PAR + AgsPAR[3] * sqrt(PAR) + AgsPAR[4])
                    - 5 : fgs =  AgsPAR[0] / (  AgsPAR[1] + ( (PAR - AgsPAR[2]) / AgsPAR[3] )**2  )
                    
                - Ags_CA_function code allows for selecting one of the following function:
                    - 1 : 2nd order polynomial function fgs = AgsCA[0] * CA**2 + AgsCA[1] * CA + AgsCA[2]
                    
                - Ags_LT_function code allows for selecting one of the following function:
                    - 1 : 2nd order polynomial function fgs = AgsLT[0] * LT**2 + AgsLT[1] * LT + AgsLT[2]
                    - 2 : deprecated
                    - 3 : fgs= (AgsLT[0] * LT**2 + AgsLT[1] * LT + AgsLT[2]) / (AgsLT[3] * LT**2 + AgsLT[4] * LT + AgsLT[5])
                    - 4 : fgs = (AgsLT[0] *  sqrt(LT) + AgsLT[1]) / (AgsLT[2] * LT + AgsLT[3] * sqrt(LT) + AgsLT[4])
                    - 5 : fgs =  AgsLT[0] / (  AgsLT[1] + ( (LT - AgsLT[2]) / AgsLT[3] )**2  )
                    
        """
        default = Vegetation.default
        
        nent = len(entities)
        
        vegetation = pyratp.vegetation_types
        vegetation.pervoxel = pervoxel
        if not pervoxel : 
            nbincli = [len(entity.get('distinc', default['distinc'])) for entity in entities]
            vegetation.nbincli = np.zeros(nent)
            vegetation.nbincli[:] = nbincli
            vegetation.distinc = np.zeros((nent, max(nbincli)))
            vegetation.distinc[:,:] = [entity.get('distinc', default['distinc']) for entity in entities]
        else : 
            vegetation.nbinclivox = [len(distribvox[0][0])]
            vegetation.distincvox =  np.zeros((len(distribvox),nent, len(distribvox[0][0])))
            for k in range(len(distribvox)):
                for n in range(nent):
                    if len(distribvox[k]) > n :
                        for i in range(len(distribvox[0][0])):
                            vegetation.distincvox[k][n][i] = distribvox[k][n][i]

        vegetation.mu = np.zeros(nent)
        vegetation.nblo = np.zeros(nent)
        vegetation.rf =  np.zeros((nent, nblomin))
        vegetation.aga = np.zeros((nent,2))
        vegetation.agsn = np.zeros((nent,2))
        vegetation.i_gspar = np.zeros(nent)
        vegetation.agspar = np.zeros((nent,10))
        vegetation.i_gsca = np.zeros(nent)
        vegetation.agsca = np.zeros((nent,10))
        vegetation.i_gslt = np.zeros(nent)
        vegetation.agslt = np.zeros((nent,10))
        vegetation.agsvpd = np.zeros((nent,3))
        vegetation.avcmaxn = np.zeros((nent,2))
        vegetation.ajmaxn = np.zeros((nent,2))
        vegetation.ardn = np.zeros((nent,2))
        vegetation.ismine = np.zeros(nent)
        vegetation.epm = np.zeros(nent)
        
        vegetation.mu[:] = [entity.get('mu', default['mu']) for entity in entities]
        vegetation.nblo[:] = [nblomin] * nent
        vegetation.nblomin = nblomin
        vegetation.rf[:,:] =  [entity.get('rf', default['rf'] * nblomin)[0:nblomin] for entity in entities]
        vegetation.aga[:,:] =  [entity.get('Aga', default['Aga']) for entity in entities]
        vegetation.agsn[:,:] =  [entity.get('AgsN', default['AgsN']) for entity in entities]
        vegetation.i_gspar[:] = [entity.get('AgsPAR_function', default['AgsPAR_function']) for entity in entities]
        agspar = [entity.get('AgsPAR', default['AgsPAR']) for entity in entities]
        vegetation.i_gsca[:] = [entity.get('AgsCA_function', default['AgsCA_function']) for entity in entities]
        agsca =  [entity.get('AgsCA', default['AgsCA']) for entity in entities]
        vegetation.i_gslt[:] = [entity.get('AgsLT_function', default['AgsLT_function']) for entity in entities]
        agslt =  [entity.get('AgsLT', default['AgsLT']) for entity in entities]
        vegetation.agsvpd[:,:] =  [entity.get('AgsVPD', default['AgsVPD']) for entity in entities]
        vegetation.avcmaxn[:,:] =  [entity.get('AVcmaxN', default['AVcmaxN']) for entity in entities]
        vegetation.ajmaxn[:,:] =  [entity.get('AJmaxN', default['AJmaxN']) for entity in entities]
        vegetation.ardn[:,:] =  [entity.get('ARdN', default['ARdN']) for entity in entities]
        vegetation.ismine[:] = [entity.get('IsMine', default['IsMine']) for entity in entities]
        vegetation.epm[:] = [entity.get('epm', default['epm']) for entity in entities]
        
        for jent in range(nent):
            vegetation.agspar[jent,:len(agspar[jent])] =  agspar[jent]
            vegetation.agsca[jent,:len(agsca[jent])] =  agsca[jent]
            vegetation.agslt[jent,:len(agslt[jent])] =  agslt[jent]
            
        return vegetation
        
    @staticmethod
    def read(filename):

        chemin=str(os.path.dirname(filename))
        vegetation = pyratp.vegetation_types
        listVegeNom = []
        f = open(filename)
        listVege = f.readlines()
        f.close()
        listParamVege=[]
        nent = len(listVege)
        vegetation.mu = np.zeros(nent)
        vegetation.nbincli = np.zeros(nent)
        vegetation.nblo = np.zeros(nent)
        vegetation.aga = np.zeros(nent*2).reshape(nent,2)
        vegetation.agsn = np.zeros((nent,2))
        vegetation.i_gspar = np.zeros(nent)
        vegetation.agspar = np.zeros((nent,10))
        vegetation.i_gsca = np.zeros(nent)
        vegetation.agsca = np.zeros((nent,10))
        vegetation.i_gslt = np.zeros(nent)
        vegetation.agslt = np.zeros((nent,10))
        vegetation.agsvpd = np.zeros((nent,3))
        vegetation.avcmaxn = np.zeros((nent,2))
        vegetation.ajmaxn = np.zeros((nent,2))
        vegetation.ardn = np.zeros((nent,2))

        vegetation.ismine = np.zeros(nent)
        vegetation.epm = np.zeros(nent)

        varTemp=np.zeros(1)
        varMine=np.zeros(1)
        varEpm=np.zeros(1)

        jent=0
        for i in listVege:
            # second column
            fn = i.split(' ')[1].strip()
            nomfVeg = pj(chemin, fn)
            fVeg = open(nomfVeg)


            _read(fVeg,varTemp)
            vegetation.mu[jent] = varTemp
            _read(fVeg,varTemp)
            vegetation.nbincli[jent]=varTemp
            if jent==0:
                vegetation.distinc =  np.zeros((nent,vegetation.nbincli[jent]))
            _read(fVeg,vegetation.distinc[jent])
            _read(fVeg,varTemp)
            vegetation.nblo[jent]=varTemp

            if jent==0:
                vegetation.nblomin = vegetation.nblo[jent]
                vegetation.rf =  np.zeros((nent,vegetation.nblo[jent]))
            _read(fVeg,vegetation.rf[jent])

            _read(fVeg,vegetation.aga[jent])
            _read(fVeg,vegetation.agsn[jent])

            gsPar=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gspar[jent]=gsPar[0]
            for n in range(len(gsPar[2:])):
                vegetation.agspar[jent][n] = gsPar[2:][n]


            gsCA=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gsca[jent]=gsCA[0]
            for n in range(len(gsCA[2:])):
                vegetation.agsca[jent][n] = gsCA[2:][n]


            gsLT=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gslt[jent]=gsLT[0]
            for n in range(len(gsLT[2:])):
                vegetation.agslt[jent][n] = gsLT[2:][n]

            _read(fVeg,vegetation.agsvpd[jent])


            _read(fVeg,vegetation.avcmaxn[jent])


            _read(fVeg,vegetation.ajmaxn[jent])

            _read(fVeg,vegetation.ardn[jent])
            _read(fVeg,varMine)
            vegetation.ismine[jent]=varMine
            _read(fVeg,varEpm)
            vegetation.epm[jent]=varEpm
            jent +=1
            fVeg.close()

        print('VEGETATION OK')
        return vegetation

def _read(f, *args):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l = l.split('\t')
    l = list(filter(None,l))
    assert len(args) <= len(l)
    args = list(args)

    for i in range(len(args)):
        taille = args[i].size
        args[i].fill(l[i])
        if  taille >1:
            k=0
            for j in l[i:(i+taille)]:
                args[i][k]=np.float32(j)
                k=k+1
    return














