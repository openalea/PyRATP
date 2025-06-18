from openalea.plantgl import *
import numpy as np
from collections import Counter

def PlantGL2VTK(scene, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
    '''    Display a PlantGL Scene in VTK
           Scene is written in VTK Format as an unstructured grid
           Inputs: ... a variable = liste de float
                   ... a scene plant GL composed of triangulated leaves
           Outputs: ... a VTK file
            T = all.Tesselator()
            sce[0].apply(T)
            T.result
    '''

    if len(variable)<len(scene):
      variable=np.zeros(len(scene))


    T = all.Tesselator()
    VertexCoords=[]
    TrianglesVertexIDs=[]
    triangleColor = []

    for k,i in enumerate(scene):
         i.apply(T) #Applique Tesselator
         TS = T.result
         for vertex in TS.pointList:
              VertexCoords.append([vertex[0],vertex[1],vertex[2]])

         ShapeNumTri = len(TS.pointList) #nbr points dans  TriangleSet
         for tri in TS.indexList:
              TrianglesVertexIDs.append([tri[0]+k*ShapeNumTri,tri[1]+k*ShapeNumTri,tri[2]+k*ShapeNumTri])
              triangleColor.append(variable[k])

    numvertex = len(VertexCoords)
    numTriangles = len(TrianglesVertexIDs)
    # write the node code here.
        # Write the output file following VTK file format for 3D view with Paraview
        # Works only with triangles P1 i.e. defined with 3 points
        #... Input:
            #... Triangles - self attribute
            #... Variable to be plotted - var
            #... Corresponding variable name - varname
        #... Output:
            #... a VTK file - filename
##    print nomfich
    f=open(nomfich,'w')
    # Set the header
    f.write('# vtk DataFile Version 3.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET UNSTRUCTURED_GRID\n')
    f.write('POINTS '+str(numvertex)+' float\n')

    # Write vertex coordinates
    for i in VertexCoords:
     f.write(str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
    f.write('\n')

    # Write elements connectivity
    f.write('CELLS '+str(numTriangles)+' '+str(numTriangles*4)+'\n')
    for i in  TrianglesVertexIDs:
     f.write('3 '+str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
    f.write('\n')

    # Write elements type i.e. 5 for triangles
    f.write('CELL_TYPES '+str(numTriangles)+'\n')
    for i in  TrianglesVertexIDs:
        f.write('5\n')
    f.write('\n')

    # Write data for each triangle
    f.write('CELL_DATA '+str(numTriangles)+'\n')

    f.write('FIELD FieldData 1 \n');
    f.write(varname +' 1 '+str(numTriangles)+' float\n')
    for i in triangleColor:
          f.write(str(i).strip('[]')+'\n')

    f.write('\n')

    f.close()

    # return outputs
    return   triangleColor

def RATP2VTK(scene, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
    '''    Display leaves colored by voxel values with Paraview for each entity
           Scene is written in VTK Format as an unstructured grid
           Inputs: ... a RATP variable = liste de float
                   ... a scene plant GL composed of triangulated leaves
           Outputs: ... a VTK file
            T = all.Tesselator()
            sce[0].apply(T)
            T.result
    '''

##    if len(variable)<len(scene):
##      variable=np.zeros(len(scene))


    T = all.Tesselator()
    VertexCoords=[]
    TrianglesVertexIDs=[]
    triangleColor = []

    for k,i in enumerate(scene):
         i.apply(T) #Applique Tesselator
         TS = T.result
         for vertex in TS.pointList:
              VertexCoords.append([vertex[0],vertex[1],vertex[2]])

         ShapeNumTri = len(TS.pointList) #nbr points dans  TriangleSet
         for tri in TS.indexList:
              TrianglesVertexIDs.append([tri[0]+k*ShapeNumTri,tri[1]+k*ShapeNumTri,tri[2]+k*ShapeNumTri])
              varia =variable[0][k] #Get the variable of the leaf number i
              triangleColor.append(varia)


    numvertex = len(VertexCoords)
    numTriangles = len(TrianglesVertexIDs)
    # write the node code here.
        # Write the output file following VTK file format for 3D view with Paraview
        # Works only with triangles P1 i.e. defined with 3 points
        #... Input:
            #... Triangles - self attribute
            #... Variable to be plotted - var
            #... Corresponding variable name - varname
        #... Output:
            #... a VTK file - filename
##    print nomfich
    f=open(nomfich,'w')
    # Set the header
    f.write('# vtk DataFile Version 3.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET UNSTRUCTURED_GRID\n')
    f.write('POINTS '+str(numvertex)+' float\n')

    # Write vertex coordinates
    for i in VertexCoords:
     f.write(str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
    f.write('\n')

    # Write elements connectivity
    f.write('CELLS '+str(numTriangles)+' '+str(numTriangles*4)+'\n')
    for i in  TrianglesVertexIDs:
     f.write('3 '+str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
    f.write('\n')

    # Write elements type i.e. 5 for triangles
    f.write('CELL_TYPES '+str(numTriangles)+'\n')
    for i in  TrianglesVertexIDs:
        f.write('5\n')
    f.write('\n')

    # Write data for each triangle
    f.write('CELL_DATA '+str(numTriangles)+'\n')

    f.write('FIELD FieldData 1 \n');
    f.write(varname +' 1 '+str(numTriangles)+' float\n')
    for i in triangleColor:
          f.write(str(i).strip('[]')+'\n')

    f.write('\n')

    f.close()

    # return outputs
    return   triangleColor

def RATPVOXELS2VTK(grid, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
    '''    Display Voxels colored by variable with Paraview
           RATP Grid is written in VTK Format as a structured grid
           Inputs: ... variable : a list of 3 arrays composed of the a RATP variable to be plotted, corresponding entities, and Voxel ID
                   ... grid : the RATP grid
                   ... varname: name of the variable to be plotted
                   ... nomfich: the VTK filename and path
           Outputs: ... a VTK file
    '''
        # Writes the output file following VTK file format for 3D view with Paraview
        #
        #... Input:
            #... Variable[0] is the value of the variable to be plotted
            #... Variable[1] is the entity corresponding to the variable
            #... Variable[2] is the Voxel id associated to the entity
            #... Corresponding variable name - varname
        #... Output:
            #... a VTK file - filename

##    print nomfich
    f=open(nomfich,'w')
    # Set the header
    f.write('# vtk DataFile Version 3.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET RECTILINEAR_GRID\n')
    f.write('DIMENSIONS '+str(grid.njx+1)+' '+str(grid.njy+1)+' '+str(grid.njz+2)+'\n')
    ## The soil layer is included

    """ f.write('Z_COORDINATES '+str(grid.njz+2)+' float\n')
    for i in range(grid.njz,-1,-1):
       z = -100*grid.dz[i]*(i+1)+100*grid.zorig
       f.write(str(z)+' ')
    f.write(str(100*grid.zorig)+' ')
    f.write('\n')

    f.write('Y_COORDINATES '+str(grid.njy+1)+' float\n')
    for i in range(grid.njy+1):
       y = 100*grid.dy*i -100*grid.yorig
       f.write(str(y)+' ')
    f.write('\n')

    f.write('X_COORDINATES '+str(grid.njx+1)+' float\n')
    for i in  range(grid.njx+1):
       x = 100*grid.dx*i-100*grid.xorig
       f.write(str(x)+' ')
    f.write('\n') """

    f.write('Z_COORDINATES '+str(grid.njz+2)+' float\n')
    # couche du sol (sous l'origine)
    
    # origine du sol
    
    for i in range(grid.njz):
       z = grid.dz[i:grid.njz].sum()-grid.zorig
       f.write(str(z)+' ')

    f.write(str(-grid.zorig)+' ')
    f.write(str(-10*grid.dz[0]-grid.zorig)+' ')
    f.write('\n')

    f.write('Y_COORDINATES '+str(grid.njy+1)+' float\n')
    for i in range(grid.njy, -1, -1):
       y = grid.dy*i+grid.yorig
       f.write(str(y)+' ')
    f.write('\n')

    f.write('X_COORDINATES '+str(grid.njx+1)+' float\n')
    for i in  range(grid.njx+1):
       x = grid.dx*i+grid.xorig
       f.write(str(x)+' ')
    f.write('\n')

    # Write data for each voxels with 1 variable per entity inkcuding soil layer
    numVoxels = (grid.njx)*(grid.njy)*(grid.njz+1)

    # Set the number of entities to write - NbScalars
    ll = Counter(variable[1])
    NbScalars = np.alen(ll.items())


    f.write('CELL_DATA '+str(numVoxels)+'\n')

    #Loop over entities
    iscalar = 0
    for ent in ll.keys(): #Loop over entity values find in the 3D scene
    #for ent in range(1):
        iscalar+=1  #Add one for each entity
        f.write('SCALARS '+varname+'_entity_'+str(int(ent))+' float  1 \n')
        f.write('LOOKUP_TABLE default\n')
        #For a non vegetative voxel set the voxel value to a default value
        #DefaultValue = -9999.0
        #Utiliser grid.kxyz
        for ik in range(grid.njz+1):#range(grid.njz-1,-1,-1):#
            for ij in range(grid.njy):
                for ii in range(grid.njx): #Loop over all voxels
                    k =grid.kxyz[ii,ij,ik] #Get the voxel id number in fortran minus 1 to get the value in Python
                    if (k>0):              #If the voxel k gets some vegetation then
                        #find the index of voxel k in the variable[2]
                        kindexDummy = np.where(np.array(variable[2])==k)
                        kindex = kindexDummy[0]
                        #Get entity numbers which are in this voxel
                        enties = np.array(variable[1])[kindex]
                        #check if  ent is in this voxel
                        EntityOk =np.where(enties==ent)
                        if np.alen(EntityOk[0])<1: #if enties is not in this voxel
                            f.write(str(-9999.0)+'\n')
                        else:                           #if enties is in this voxel
                            if ik == grid.njz:         #Soil layer
                                f.write(str(-9999.0)+'\n')
                            else:
                                value = variable[0][(kindex[np.where(enties==ent)])[0]]
                                f.write(str(value)+'\n')
                    else:
                        f.write(str(-9999.0)+'\n')
        f.write('\n')

        # indice des voxels
        f.write('SCALARS Voxel_ID float  1 \n')
        f.write('LOOKUP_TABLE default\n')
        for ik in range(grid.njz+1):#range(grid.njz-1,-1,-1):#
            for ij in range(grid.njy):
                for ii in range(grid.njx): #Loop over all voxels
                    k =grid.kxyz[ii,ij,ik] # attention affiche k+1
                    f.write(str(k)+'\n')
        f.write('\n')

    f.close()