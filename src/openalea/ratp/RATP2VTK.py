##from openalea.plantgl import *
import numpy as np
from collections import Counter
import pandas

##def PlantGL2VTK(scene, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
##    '''    Display a PlantGL Scene in VTK
##           Scene is written in VTK Format as an unstructured grid
##           Inputs: ... a variable = liste de float
##                   ... a scene plant GL composed of triangulated leaves
##           Outputs: ... a VTK file
##            T = all.Tesselator()
##            sce[0].apply(T)
##            T.result
##    '''
##
##    if len(variable)<len(scene):
##      variable=np.zeros(len(scene))
##
##
##    T = all.Tesselator()
##    VertexCoords=[]
##    TrianglesVertexIDs=[]
##    triangleColor = []
##
##    for k,i in enumerate(scene):
##         i.apply(T) #Applique Tesselator
##         TS = T.result
##         for vertex in TS.pointList:
##              VertexCoords.append([vertex[0],vertex[1],vertex[2]])
##
##         ShapeNumTri = len(TS.pointList) #nbr points dans  TriangleSet
##         for tri in TS.indexList:
##              TrianglesVertexIDs.append([tri[0]+k*ShapeNumTri,tri[1]+k*ShapeNumTri,tri[2]+k*ShapeNumTri])
##              triangleColor.append(variable[k])
##
##    numvertex = len(VertexCoords)
##    numTriangles = len(TrianglesVertexIDs)
##    # write the node code here.
##        # Write the output file following VTK file format for 3D view with Paraview
##        # Works only with triangles P1 i.e. defined with 3 points
##        #... Input:
##            #... Triangles - self attribute
##            #... Variable to be plotted - var
##            #... Corresponding variable name - varname
##        #... Output:
##            #... a VTK file - filename
####    print nomfich
##    f=open(nomfich,'w')
##    # Set the header
##    f.write('# vtk DataFile Version 3.0\n')
##    f.write('vtk output\n')
##    f.write('ASCII\n')
##    f.write('DATASET UNSTRUCTURED_GRID\n')
##    f.write('POINTS '+str(numvertex)+' float\n')
##
##    # Write vertex coordinates
##    for i in VertexCoords:
##     f.write(str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
##    f.write('\n')
##
##    # Write elements connectivity
##    f.write('CELLS '+str(numTriangles)+' '+str(numTriangles*4)+'\n')
##    for i in  TrianglesVertexIDs:
##     f.write('3 '+str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
##    f.write('\n')
##
##    # Write elements type i.e. 5 for triangles
##    f.write('CELL_TYPES '+str(numTriangles)+'\n')
##    for i in  TrianglesVertexIDs:
##        f.write('5\n')
##    f.write('\n')
##
##    # Write data for each triangle
##    f.write('CELL_DATA '+str(numTriangles)+'\n')
##
##    f.write('FIELD FieldData 1 \n');
##    f.write(varname +' 1 '+str(numTriangles)+' float\n')
##    for i in triangleColor:
##          f.write(str(i).strip('[]')+'\n')
##
##    f.write('\n')
##
##    f.close()
##
##    # return outputs
##    return   triangleColor

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
    f.write(str(-grid.dz[0]-grid.zorig)+' ')
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
                        if len(EntityOk[0])<1: #if enties is not in this voxel
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
    
def RATPVOXELS2PYVISTA(grid, variable, varname):
    '''
    A function to create a visualisation of a voxel file using PyVista.
    It creates a vtk grid structure and fill it with the variable to plot,
    or to default values for empty voxels. This mesh is then thresholded 
    to remove empty voxels before display.
    
    Parameters
    ----------
    grid: RATP grid
        RATP grid object.
    variable: Numpy array
        Numpy array containing the variable to be viewed.
    varname: string
        name of the variable to be displayed

    Returns
    -------
    pvgrid : PyVista Rectilinear grid

    '''
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError(
        "PyVista is not installed. "
        "Please install it with: pip install pyvista"
        )
        
    # --- Extract coordinates ---
    # Z_COORDINATES
    z_coords = np.zeros(grid.njz + 2) # +2 as it is the number of edges
    for i in range(grid.njz):
        z_coords[i] = grid.dz[i:grid.njz].sum() - grid.zorig
    z_coords[-2] = -grid.zorig
    z_coords[-1] = -grid.dz[0] - grid.zorig

    # Y_COORDINATES 
    y_coords = np.zeros(grid.njy + 1) # +1 as it is the number of edges
    for i in range(grid.njy, -1, -1):
        y_coords[grid.njy - i] = grid.dy * i + grid.yorig

    # X_COORDINATES
    x_coords = np.zeros(grid.njx + 1) # +1 as it is the number of edges
    for i in range(grid.njx + 1):
        x_coords[i] = grid.dx * i + grid.xorig

    # --- Create the PyVista RectilinearGrid ---
    pvgrid = pv.RectilinearGrid(x_coords, y_coords, z_coords)
    
    # --- add the scalar fields ---
    num_voxels = grid.njx * grid.njy * (grid.njz + 1)
    ll = Counter(variable[1]) # number of vegetation entities in the scene
    
    # Initialize scalar arrays
    scalar_arrays = {}
    for ent in ll.keys(): # 1 scalar array per vegetation entity
        scalar_arrays[f"{varname}_entity_{int(ent)}"] = np.full(num_voxels, -9999.0)
        
    # Loop over each unique entity in the dataset
    for ent in ll.keys():
        # Get the scalar field array for the current entity
        scalar_field = scalar_arrays[f"{varname}_entity_{int(ent)}"]
    
        # Loop over all voxels in the grid (z, y, x directions)
        for ik in range(grid.njz + 1):  # Loop over z-coordinates (including soil layer)
            for ij in range(grid.njy):   # Loop over y-coordinates
                for ii in range(grid.njx):  # Loop over x-coordinates
                    # Get the voxel ID at position (ii, ij, ik)
                    k = grid.kxyz[ii, ij, ik]
    
                    # Check if the voxel exists (k > 0)
                    if k > 0:
                        # Find all indices in `variable[2]` (voxelID) where the voxel ID matches `k`
                        kindex_dummy = np.where(np.array(variable[2]) == k)
    
                        # Extract the indices as a 1D array
                        kindex = kindex_dummy[0]
    
                        # Get the entity values for this voxel
                        entities = np.array(variable[1])[kindex]
    
                        # Check if the current entity `ent` exists in this voxel
                        entity_ok = np.where(entities == ent)[0]
    
                        # If the entity exists in this voxel
                        if len(entity_ok) > 0:
                            # Skip the soil layer (ik == grid.njz)
                            if ik != grid.njz:
                                # Get the scalar value for this entity in this voxel
                                # `kindex[entity_ok][0]` gets the index of the first matching entity
                                value = variable[0][kindex[entity_ok][0]]
    
                                # Calculate the linear index for the scalar field array
                                # This converts 3D indices (ik, ij, ii) to a 1D index
                                idx = ik * grid.njx * grid.njy + ij * grid.njx + ii
    
                                # Assign the scalar value to the corresponding position in the array
                                scalar_field[idx] = value

        # Add the scalar field to the grid (one per entity)
        pvgrid[f"{varname}_entity_{int(ent)}"] = scalar_field

    # threshold scalar fields to remove non-existing voxels 
    thresholded = pvgrid.threshold(value=-9998, all_scalars=True)
    
    return thresholded

def extract_dataframe(df, ColName, Day, Hour):
    '''
    A function to extract a day+hour +variable of interest from a pandas data frame.
    It is formatted to then be exported as vtk, or plotted using PyVista.
    
    Parameters
    ----------
    df: pandas data frame
        
    ColName: string
        Name of the variable to be extracted
    Day: integer
        Value of the day to be extracted
    Hour: integer
        Value of the hour to be extracted

    Returns
    -------
    extratcted_array: Numpy array
        contains the variable of interest at the specified day and hour

    '''
    
    # Filter the DataFrame for the specified day and hour
    filtered_df = df[(df['day'] == Day) & (df['hour'] == Hour)]

    # format data to be written
    extracted_df = filtered_df[[ColName, 'VegetationType', 'VoxelId',]]

    # Convert the DataFrame to a NumPy array
    extracted_array = extracted_df.to_numpy()

    # Transpose the array to orient it along the rows
    return extracted_array.T

# Function to detect if running in a notebook
def is_notebook():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' in get_ipython().config:
            return True
        else:
            return False
    except:
        return False

class PyRATPViewer:
    def __init__(self, grid, df):
        try:
            import pyvista as pv
        except ImportError:
            raise ImportError(
            "PyVista is not installed. "
            "Please install it with: pip install pyvista"
            )
            
        # Set the Jupyter backend if running in a notebook
        if is_notebook():
            pv.set_jupyter_backend("static")  
        
        self.data = df # data frame of interest
        self.g = grid # RATP grid
        
        # Get all column names except the first 4 (veg type, Iteration, day, hour)
        self.list_names = df.columns[4:].tolist()
        
        # slider ranges
        self.min_day = self.data["day"].min()
        self.max_day = self.data["day"].max()
        self.min_hour = self.data["hour"].min()  
        self.max_hour = self.data["hour"].max()  
        self.nent = self.g.nent #number of entities
        
        # intial view parameters
        self.day = int((self.min_day+self.max_day)/2) # initial day
        self.hour = self.min_hour+12 # initial hour
        self.variable = "SunlitTemp" # default variable to plot
        self.entity = 1 # default entity
        
        # create initial view
        self.plotter = pv.Plotter() # initiate plotter
        array = extract_dataframe(self.data, self.variable, self.day, self.hour) #  get data
        self.mesh = RATPVOXELS2PYVISTA(self.g, array, self.variable) # create pyvista object

        self.plotter.add_mesh(self.mesh,cmap="viridis", 
                              scalars=f"{self.variable}_entity_{self.entity}") # add to plotter
        
        # Add a slider widget to control the day
        self.plotter.add_slider_widget(
            callback=self.update_day, # what to do when the slider moved
            rng=[self.min_day,self.max_day], # slider range
            value=int((self.min_day+self.max_day)/2), # initial value
            style="modern",
            title="day",
            pointa=(0.35, 0.9),
            pointb=(0.64, 0.9),
            interaction_event = 'always',
        )
        
        # Add a slider widget to control the hour
        self.plotter.add_slider_widget(
            callback=self.update_hour,
            rng=[self.min_hour,self.max_hour],
            value=self.min_hour+12,
            style="modern",  # or "document"
            title="hour",
            pointa=(0.67, 0.9),
            pointb=(0.98, 0.9),
            interaction_event = 'always',
        )
        
        # Add a slider widget to control the entity
        self.plotter.add_slider_widget(
            callback=self.update_entity,
            rng=[1,self.nent],
            value=self.entity,
            style="modern",  # or "document"
            title="entity",
            pointa=(0.02, 0.7),
            pointb=(0.33, 0.7),
            interaction_event = 'always',
        )
        
        # Add a TEXT slider widget to control the variable to plot
        self.plotter.add_text_slider_widget(
            callback=self.update_variable,
            data=self.list_names,
            value=self.list_names.index(self.variable),
            style="modern",
            pointa=(0.02, 0.9),
            pointb=(0.33, 0.9),
            interaction_event='always',
        )
        
        self.plotter.show_axes()
        self.plotter.show(title="PyRATP Viewer")

    def update_day(self,val):
        self.day = int(val) # round slider value
        self.update_plot()
        
    def update_entity(self,val):
        self.entity = max(1,np.ceil(val)) # actual entity is at least 1
        self.update_plot()
        
    def update_hour(self,val):
        self.hour = int(val) # round slider value
        self.update_plot()
        
    def update_variable(self, val):
        self.variable = val # get slider value
        self.update_plot()
        
    def update_plot(self):
        """Update the plot with the current day, hour, variable and entity."""
        # Extract data for the selected day, hour, and variable
        array = extract_dataframe(self.data, self.variable, self.day, self.hour)
        if array is not None and np.size(array,1) > 0: # if the data exists!
            self.plotter.remove_scalar_bar()
            self.mesh = RATPVOXELS2PYVISTA(self.g, array, self.variable)
            self.plotter.add_mesh(self.mesh, cmap="viridis",
                                  scalars=f"{self.variable}_entity_{self.entity}")
    
            # Update the scalar bar title and range
            self.plotter.update_scalar_bar_range(self.mesh.get_data_range())
        else:
            print(f"No data available for variable: {self.variable}, day: {self.day}, hour: {self.hour}")