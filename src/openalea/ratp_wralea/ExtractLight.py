import numpy as np

def ExtractLight(d_e2v, data, day, hour,col):
    '''    Extract a variable from RATP output for a given date (day and hour)
    and attached this extracted variable to leaves for 3D visualization.
        Input::Parameters:
            - d_e2v: connectivity table Leaf -> Voxel (list)
            - data: a 2D array(real)
            - day, hour: time to extract data
            - col: column corresponding to data to be extracted.

        Output:Parameters:
            - extractedvar: extracted data. One data per leaf
    '''
    ls_id = [1,2]
    ls_vals = [day, hour]
    dat = extract_list(data, ls_id, ls_vals)
    dat = t_list(dat)


    extractedvar = []

    nmax = np.alen(d_e2v)

    for i in range(nmax): #Enleve nmax+1 MARC 10 12 2014
        try :
            extractedvar.append(dat[col][int(d_e2v[str(i)])])
        except:
            extractedvar.append(0)#!!! Recupere pas toutes les entites dans d_e2v!!? : A cause de triangles en z negatif!

    return extractedvar


def ExtractLightNew(d_e2v, data, day, hour,col):
    '''    Extract a variable from RATP output for a given date (day and hour)
    and attached this extracted variable to leaves for 3D visualization.
        Input::Parameters:
            - d_e2v: connectivity table Leaf number -> Voxel number (list)
            - data: a 2D array(real)
            - day, hour: time to extract data
            - col: column corresponding to data to be extracted.

        Output:Parameters:
            - extractedvar: extracted data. One data per leaf
    '''
    # Works fine for 1 entity only. When we have several entities the column contains more than nb Voxels
#    ls_id = [1,2] for one entity
    ls_id = [2,3]               #Column number for day and hour in the output file - ANY CHANGE IN THE OUTPUT FILE SHOULD BE ALSO DONE THERE
    ls_vals = [day, hour]
    dat = extract_list(data, ls_id, ls_vals)
    dat = t_list(dat)
    colVoxel = 5;           #VOXEL_ID SHOULD BE STORED IN THIS COLUMN IN THE OUTPUT FILE i.e. voxel_id = dat[:][colVoxel]
    colEntity = 0;          #ENTITY ID SHOULD BE STORED IN THIS COLUMN IN THE OUTPUT FILE i.e. Entity = dat[:][colEntity]

    extractedvar = []
    entity=[]
    voxelId=[]
    nmax = np.alen(d_e2v)   #number of leaves in the initial 3D plant scene to be colored

    for i in range(nmax): #Enleve nmax+1 MARC 10 12 2014
##        try :
            extractedvar.append(dat[col][int(d_e2v[str(i)])])
            entity.append(dat[colEntity][int(d_e2v[str(i)])])
            voxelId.append(dat[colVoxel][int(d_e2v[str(i)])]) #Not sure yet if i need this information for the 3D output ! At this time keep it to have the same outputt format as the ExtractVoxels method
##        except:
##            extractedvar.append(0)#!!! Recupere pas toutes les entites dans d_e2v!!? : A cause de triangles en z negatif!

    return extractedvar,entity,voxelId

def ExtractVoxels(data, day, hour,col):
    '''    Extract a variable from RATP output for a given date (day and hour)
    and attached this extracted variable to voxels for 3D visualization.
        Input:
            - data: a 2D array(real)
            - day, hour: time to extract data
            - col: column corresponding to data to be extracted.

        Output:
            - extractedvar: extracted data. One data per Voxel
    '''
    # Works fine for 1 entity only. When we have several entities the column contains more than nb Voxels
#    ls_id = [1,2] for one entity
    ls_id = [2,3]               #Column number for day and hour in the output file - ANY CHANGE IN THE OUTPUT FILE SHOULD BE ALSO DONE THERE
    ls_vals = [day, hour]
    dat = extract_list(data, ls_id, ls_vals) # dat contains only data for the targeted day and hour
    dat = t_list(dat)
    nmax = len(dat[col])
    colVoxel = 5;           #VOXEL_ID SHOULD BE STORED IN THIS COLUMN IN THE OUTPU FILE
    colEntity = 0;          #ENTITY ID SHOULD BE STORED IN THIS COLUMN IN THE OUTPU FILE
    extractedvar = []
    entity=[]
    voxelId=[]
    for i in range(nmax):
#        try :
        extractedvar.append(dat[col][i])
        entity.append(dat[colEntity][i])
        voxelId.append(dat[colVoxel][i])
#        except:
#        extractedvar.append(0)


    return extractedvar,entity,voxelId



#!!! Recupere pas toutes les entites dans d_e2v!!?
def extract_list(dat, ls_id, ls_vals):
    """ extrait avec un ET les lignes pour les quelles les colonnes numerotees ls_id prennent les valeurs ls_vals"""

    res = []
    for i in range(0, len(dat)):   #ATTENTION CHANGEMENT ON PART A 0. UN VOXEL ETAIT MANQUANT SINON !! 20/12/2011 MARC SAUDREAU
        bol = 1
        for j in range(len(ls_id)):
            if dat[i][ls_id[j]] == ls_vals[j]:
                bol = bol*1
            else :
                bol = bol*0

        if bol == 1:
            res.append(dat[i])

    return res

def t_list(tab):
    """transpose tab"""
    res = []
    if tab:
        for j in range(len(tab[0])):
            v = []
            for i in range(len(tab)):
                v.append(tab[i][j])

            res.append(v)

    return res
