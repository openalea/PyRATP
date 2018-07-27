
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>


""" A high level class interface to RATP
"""

import numpy
import pandas

from alinea.pyratp.grid import Grid, voxel_map
from alinea.pyratp.skyvault import Skyvault
from alinea.pyratp.vegetation import Vegetation
from alinea.pyratp.micrometeo import MicroMeteo
from alinea.pyratp.runratp import runRATP

from alinea.pyratp.interface.clumping_index import clark_evans

from openalea.plantgl import all as pgl

# to be moved to grid.py: function voxel_boxes that return center + x,y,z sizes of filled voxel boxes
def voxel_relative_coordinates(x, y, z, mapping, grid, normalise = True):
    """ return coordinates of points relative to voxel origin
        If normalise = true, coordinates are normalised by voxel dimensions
    """
    # scene dimensions
    delta_x = grid.njx * grid.dx
    delta_y = grid.njy * grid.dy
    delta_z = grid.dz.sum()
    #
    kvox = [int(mapping[str(i)]) for i in range(len(x))]
    xv = (numpy.array(x) - grid.xorig) % delta_x - numpy.array([int((grid.numx[k] - 1) * grid.dx) for k in kvox])
    yv = (numpy.array(y) - grid.yorig) % delta_y - numpy.array([int((grid.njy - grid.numy[k]) * grid.dy) for k in kvox])
    zv = (numpy.array(z) + grid.zorig) % delta_z - numpy.array([int(grid.dz.sum() - grid.dz[:grid.numz[k]].sum()) for k in kvox])
    # normalising voxel dimensions
    if normalise:
        xv /= grid.dx
        yv /= grid.dy
        zv /= numpy.array([grid.dz[int(grid.numz[k] - 1)] for k in kvox])
    
    return xv, yv, zv 
 

def estimate_clumping(entity, x, y, z, s, mapping, grid, normalise = True):
    # compute clumping : compute 3D dispersion index of all voxels with at least two points
    # (a valider avec marc)
    # coordinates of points within voxels
    xv, yv, zv = voxel_relative_coordinates(x, y, z, mapping, grid, normalise = normalise)
    kvox = [mapping[str(i)] for i in range(len(x))]
    data = pandas.DataFrame({'entity':entity, 'x':xv, 'y':yv, 'z':zv, 's':s, 'kvox':kvox})        
    mu = []
    grouped = data.groupby('entity')
    for e in range(grid.nent):
        dfe = grouped.get_group(e)
        gvox = dfe.groupby('kvox')
        clumps=[]
        for k, df in gvox: 
            if len(df) > 0:
                if df['s'].sum() > 0:
                    min_mu = df['s'].mean() / df['s'].sum() # minimal mu in the case of perfect clumping
                    if len(df) > 1:
                        clumping = clark_evans(zip(df['x'], df['y'], df['z']), ((0,0,0),(1,1,1)))
                        clumps.append(max(min_mu, clumping))
                    else:
                        clumps.append(min_mu)
        mu.append(numpy.mean(clumps))
    return mu

class ColorMap(object):
    """A RGB color map, between 2 colors defined in HSV code

    :Examples: 

    >>> minh,maxh = minandmax([height(i) for i in s2])
    >>> colormap = ColorMap(minh,maxh)
    >>> s3 = [ Shape(i.geometry, Material
    >>>    (Color3(colormap(height(i))), 1), i.id)
    >>>    for i in s2]

    """

    def __init__(self, minval=0., maxval=1.):
        self.minval = float(minval)
        self.maxval = float(maxval)

    def color(self, normedU):
        """
        
        :param normedU: todo
        
        """
        inter = 1/5.
        winter = int(normedU/inter)
        a = (normedU % inter)/inter
        b = 1 - a
        
        if winter < 0:
            col = (self.coul2, self.coul2, self.coul1)
        elif winter == 0:
            col = (self.coul2, self.coul2*b+self.coul1*a, self.coul1)
        elif winter == 1:
            col = (self.coul2, self.coul1, self.coul1*b+self.coul2*a)
        elif winter == 2:
            col = (self.coul2*b+self.coul1*a, self.coul1, self.coul2)
        elif winter == 3:
            col = (self.coul1, self.coul1*b+self.coul2*a, self.coul2)
        elif winter > 3:
            col = (self.coul1, self.coul2, self.coul2)
        return (int(col[0]), int(col[1]), int(col[2]))

    def greycolor(self, normedU):
        """
        
        :param normedU: todo
        :returns: todo
        """
        return (int(255*normedU), int(255*normedU), int(255*normedU))

    def grey(self, u):
        """
        :param u: 
        :returns: todo
        """
        return self.greycolor(self.normU(u))

    def normU(self, u):
        """
        :param u:
        :returns: todo
        """
        if self.minval == self.maxval:
            return 0.5
        return (u - self.minval) / (self.maxval - self.minval)

    def __call__(self, u, minval=0, maxval=1, coul1=80, coul2=20):
        self.coul1 = coul1
        self.coul2 = coul2
        self.minval = float(minval)
        self.maxval = float(maxval)
        return self.color(self.normU(u))



def sample_database():
    """ to test if th creative commons database of french city fits
    """
    return {'Montpellier': {'city': 'Montpellier', 'latitude':43.61, 'longitude':3.87}}

class RatpScene(object):
    """ High level class interface for RATP
    """
    
    localisation_db = sample_database()
    default_grid = {'shape':[10, 10, 10], 'resolution':[0.1, 0.1, 0.1], 'z_soil':0}
    units = {'mm':0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10, 'hm': 100, 'km':1000}
    timezone = 0 # consider UTC/GMT time for date inputs
    idecaly = 0 
    
    def __init__(self, scene=None, scene_unit = 'm', toric=False, domain=None, entity=None, nitrogen=None, area=None, z_soil=None, localisation='Montpellier', grid_shape=None, grid_resolution=None, grid_orientation=0, z_resolution=None, nbincli=9):
        """
        Initialise a RatpScene.
        
        Arguments:
        scene: a PlantGL Scene (list of shapes with ids)
        scene_unit (string): scene length unit ('m', 'cm', ...)
        toric (bool): False (default) if the scene is an isolated canopy, True if the scene is toric, ie simulated as if repeated indefinitvely 
        domain: a ((xmin, ymin), (xmax, ymax)) tuple of coordinates (in scene units) describing the spatial extent of the toric scene pattern domain.
                If None (default) the scene bounding box will be taken as the domain
        entity: a {scene_id:entity_key} dict that associate a scene object to an RATP entity. If None (default), all shapes points to entity_code 1.
        nitrogen: a {scene_id:nitrogen_content} dict that associate a scene object to a nitrogen content. If None (default), all got a value of 2
        area: a {scene_id:area} dict that associate a scene object to its 'radiative' (one sided) area (in scene unit). If None (default), object area is used.
        z_soil : z coordinate (scene units) of the soil in the scene. If None (default), soil will be positioned at the base of the canopy bounding box
        localisation : a string referencing a city of the localisation database (class variable), or a dict{'longitude':longitude, 'latitude':latitude}
        grid_shape: dimensions of the grid (voxel number per axis: [nx, ny, nz]). If None, shape will adapt to scene, using grid_resolution.
        grid_resolution: size (m) of voxels in x,y and z direction :[dx, dy, dz]. If None, resolution will adapt to scene using grid_shape.
        grid_orientation: angle (deg, positive clockwise) from X+ to North (default: 0).
        z_resolution (optional): tuple decribing individual voxel size (m) in z direction (from the soil to the top of the canopy). If None (default), grid_resolution is used.
        nbincli: number of inclination class withi each voxel

        Note
        If scene is set to None, class default grid parameters are used to replace None values for grid_resolution and grid_shape
        If scene is provided and both grid_resolution and grid_shape are set to None,  the class default grid shape is used
        If both grid_resolution and grid_shape are provided, grid is build idependantly of scene content.
        """

        self.scene = scene
        self.scene_unit = scene_unit
        
        try:
            self.convert = RatpScene.units[scene_unit]
        except KeyError:
            print 'Warning, unit', scene_unit, 'not found, ratp assume that it is meters'
            self.convert = 1
            
        self.entity = entity
        if self.entity is None and self.scene is not None:
            self.entity = {sh.id:1 for sh in scene}
            
        self.nitrogen = nitrogen
        if self.nitrogen is None and self.scene is not None:
            self.nitrogen = {sh.id:2 for sh in scene}
        
        self.area = area
        if self.area is None:
            self.area={}
        
        self.z_soil = z_soil
        if self.scene is None and self.z_soil is None:
            self.z_soil = RatpScene.default_grid['z_soil']
        
        if not isinstance(localisation, dict):
            try:
                self.localisation = RatpScene.localisation_db[localisation]
            except KeyError:
                print 'Warning : localisation',localisation, 'not found in database, using default localisation', RatpScene.localisation_db.iter().next()
                self.localisation = RatpScene.localisation_db.itervalues().next()
                
        self.grid_resolution = grid_resolution
        self.grid_shape = grid_shape
        
        if self.scene is None:
            if self.grid_resolution is None:
                self.grid_resolution = RatpScene.default_grid['resolution']
            if self.grid_shape is None:
                self.grid_shape = RatpScene.default_grid['shape']
        else:
            if self.grid_resolution is None and self.grid_shape is None:
                self.grid_shape = RatpScene.default_grid['shape']
            
        self.grid_orientation = grid_orientation
        self.z_resolution = z_resolution
        self.toric = toric
        self.nbincli = nbincli
        #
        self.distinc = []
        self.mu = []
        self.domain = domain
        
    def fit_grid(self, z_adaptive=False):
        """ Find grid parameters that fit the scene in the RATP grid
        """
        
        # fit regular grid to scene
        if self.scene is None:
            nbx, nby, nbz = self.grid_shape
            dx, dy, dz = self.grid_resolution # already in meter
            xo, yo, zo = 0, 0, 0 # origin
        else:
            # Find the bounding box that fit the scene
            tesselator = pgl.Tesselator()
            bbc = pgl.BBoxComputer(tesselator)
            bbc.process(self.scene)
            bbox = bbc.result
            zsoil = self.z_soil
            if zsoil is None:
                zsoil = bbox.getZMin() 
            
            if self.domain is None:
                xo = bbox.getXMin() * self.convert # origin    
                yo = bbox.getYMin() * self.convert
            else:
                xo = self.domain[0][0] * self.convert
                yo = self.domain[0][1] * self.convert
            zo = zsoil * self.convert
            
            if self.grid_resolution is not None and self.grid_shape is not None:
                nbx, nby, nbz = self.grid_shape
                dx, dy, dz = self.grid_resolution # already in meter
            else:
                if self.domain is None:
                    xmax = bbox.getXMax() * self.convert    
                    ymax = bbox.getYMax() * self.convert
                else:
                    xmax = self.domain[1][0] * self.convert
                    ymax = self.domain[1][1] * self.convert
                zmax = bbox.getZMax() * self.convert
                if self.grid_resolution is None:
                    nbx, nby, nbz = self.grid_shape
                    if self.domain is None:
                        if nbx > 1:
                            dx = (xmax - xo) / float(nbx - 1)# use nbx -1 to ensure min and max are in the grid 
                        else:
                            dx = (xmax - xo) * 1.01
                        if nby > 1:
                            dy = (ymax - yo) / float(nby - 1)
                        else:
                            dy = (ymax - yo) * 1.01
                    else:
                        dx = (xmax - xo) / float(nbx) #toric canopies allows coordinate outside the pattern
                        dy = (ymax - yo) / float(nby)
                    if nbz > 1:
                        dz = (zmax - zo) / float(nbz - 1)
                    else:
                        dz = (zmax - zo) * 1.01
                    # try to accomodate flat scene
                    if dz == 0:
                        dz = (dx + dy) / 2.
                    if dx == 0:
                        dx = (dy + dz) / 2.
                    if dy == 0:
                        dy = (dx + dz) / 2.
                if self.grid_shape is None: 
                    dx, dy, dz = self.grid_resolution
                    if self.domain is None:
                        nbx = int(numpy.ceil((xmax - xo) / float(dx)))
                        nby = int(numpy.ceil((ymax - yo) / float(dy)))
                    else: #dx,dy,dz are adjusted to fit the domain exactly
                        nbx = int((xmax - xo) / float(dx))
                        nby = int((ymax - yo) / float(dy))
                        dx = (xmax - xo) / float(nbx)
                        dy = (ymax - yo) / float(nby)
                    nbz = int(numpy.ceil((zmax - zo) / float(dz)))    
                # balance extra-space between both sides of the grid (except z i zsoil has been set)
                extrax = dx * nbx - (xmax - xo)
                xo -= (extrax / 2.)
                extray = dy * nby - (ymax - yo)
                yo -= (extray / 2.)
                if self.z_soil is None:
                    extraz = dz * nbz - (zmax - zo)
                    zo -= (extraz / 2.) 

        # dz for all voxels    
        if self.z_resolution is not None:
            dz = self.z_resolution[::-1] # dz is from top to base for ratp
            nbz = len(dz)
        else:
            dz = [dz] * nbz
            
        grid_pars = {'njx':nbx, 'njy':nby, 'njz':nbz,
                     'dx':dx, 'dy':dy, 'dz':dz,
                     'xorig':xo, 'yorig':yo, 'zorig':-zo} # zorig is a z offset in grid.py (grid_z = z + zo)
        
        return grid_pars
      
    def scene_transform(self):
        """ Transform scene for RATP input
        
            return entity, x,y,z,surface, nitrogen, sh_id lists
        """

        def _surf(mesh, iface):
            A,B,C = [mesh.pointList[i] for i in mesh.indexAt(iface)]
            return pgl.norm(pgl.cross(B-A, C-A)) / 2.0

        def _normal(mesh, iface):
            A,B,C = [mesh.pointList[i] for i in mesh.indexAt(iface)]
            n = pgl.cross(B-A, C-A)
            return n.normed()

        def _process(shape, discretizer):
            discretizer.process(shape)
            mesh = discretizer.result
            ifaces = range(mesh.indexListSize())
            s = [_surf(mesh,i) * self.convert**2 for i in ifaces]
            a = float(sum(s)) / self.convert**2
            phi = [pgl.Vector3.Spherical(_normal(mesh,i)).phi for i in ifaces]
            sh_id  = [shape.id] * len(s)
            n = [self.nitrogen[shape.id]] * len(s)
            entity = [self.entity[shape.id] - 1] * len(s) # entity 1 is encoded 0 in fill grid
            scale_area = [float(self.area.get(shape.id, a)) / a] * len(s)
            centers = [mesh.faceCenter(i) for i in ifaces]
            x, y, z = zip(*map(lambda x: (x[0] * self.convert, x[1] * self.convert, x[2] * self.convert), centers))
            s = (numpy.array(s) * numpy.array(scale_area)).tolist()

            return entity, x, y, z, s, n, sh_id, phi
          
        d = pgl.Discretizer()
        transform = map(lambda x: _process(x,d), self.scene)
        return map(lambda what: reduce(lambda x,y : x+y, what), zip(*transform))

            
        
    def grid(self, rsoil=0.20):
        """ Create and fill a RATP grid 

        :Parameters:
        - rsoil : soil reflectances in the PAR and NIR band

        :Output:
            - grid3d : ratp fortran grid object
            - vox_id : list of ratp voxel_id for all primitive in the grid
            - sh_id : list of shape_id for all primitive in the grid
            - area : list of radiative object area for all primitive in the grid
        """
    
        grid_pars = {'latitude': self.localisation['latitude'],
                     'longitude':self.localisation['longitude'],
                     'timezone': RatpScene.timezone,
                     'idecaly': RatpScene.idecaly,
                     'orientation': self.grid_orientation,
                     'toric': self.toric}
        
        grid_size = self.fit_grid()
        grid_pars.update(grid_size)
        
        entity, x, y, z, s, n, sh_id, theta = self.scene_transform()
        nent = max(entity) + 1
        
        if not hasattr(rsoil, '__len__'):
            rsoil = [rsoil]
        
        grid_pars.update({'rs':rsoil,'nent':nent})
        
        grid = Grid.initialise(**grid_pars)
        # store parameters for provenance
        self.grid_pars = grid_pars

        grid, mapping = Grid.fill_1(entity, x, y, z, s, n, grid) # mapping is a {str(python_x_list_index) : python_k_gridvoxel_index}
        # in RATP output, VoxelId is for the fortran_k_voxel_index (starts at 1, cf prog_RATP.f90, lines 489 and 500)
        index = range(len(x))
        vox_id = [mapping[str(i)] + 1 for i in index]
        # and one additional map that allows retrieving shape_id from python_x_index
        sh_id = [sh_id[i] for i in index]

        # save coordinates of centers of filled voxels
        self.voxel_map = voxel_map(grid)
        
        # compute distributions of orientation
        orientation = numpy.degrees(numpy.abs(theta)) % 90
        def _dist(inc):
            dist = numpy.histogram(inc, self.nbincli, (0,90))[0]
            return dist.astype('float') / dist.sum()
        df = pandas.DataFrame({'entity':[self.entity[sid] for sid in sh_id], 'inc':orientation})
        self.inc_data = df
        self.distinc = df.sort_values('entity').groupby('entity').apply(_dist).tolist()

        # estimate clumping
        self.mu = estimate_clumping(entity, x, y, z, s, mapping, grid)
        if any(map(numpy.isnan, self.mu)):
            raise ValueError('Cannot estimate mu')
        
        return grid, vox_id, sh_id, s

    def do_irradiation(self, rleaf=(0.1,), rsoil=0.20, doy=1, hour=12, Rglob=1, Rdif=1, mu=None, sources=None):
        """ Run a simulation of light interception for one wavelength
        
            Parameters:            
                - rleaf : list of leaf refectance per entity
                - rsoil : soil reflectance
                - doy : [list of] day of year [for the different iterations]
                - hour : [list of] decimal hour (0-24) [for the different iterations]
                - Rglob : [list of] global (direct + diffuse) radiation [for the different iterations] (W.m-2)
                - Rdif : [list of] direct/diffuse radiation ratio [for the different iterations] (0-1)
                - mu: if not None, force mu for all species to be set to this value
                - sources: a list of sequences giving elevation, azimuth and weight associated to sky vault sectors.
                if None, default RATP soc-weighted skyvault is used

        """
        
        grid, voxel_id, shape_id , areas = self.grid(rsoil=rsoil)
               
        print(' '.join(['clumping evaluated:'] + [str(self.mu[i]) for i in range(len(rleaf))]))
        if mu is None:
            entities = [{'rf':[rleaf[i]], 'distinc':self.distinc[i], 'mu':self.mu[i]} for i in range(len(rleaf))]
        else:
            entities = [{'rf':[rleaf[i]], 'distinc':self.distinc[i], 'mu':mu} for i in range(len(rleaf))]

        vegetation = Vegetation.initialise(entities, nblomin=1)
        
        if sources is None:
            sky = Skyvault.initialise()
        else:
            el, az, w = sources
            # omega (sr, sum=2pi) is used by ratp to weight Gfuntion in k
            # computation (mod_dir_interception.f90, line 112)
            # pc is used elsewhere (mod_Hemi_Interception), line 124) to compute
            # fraction intercepted in a given direction
            # to me, both should be consistent, ie giving same weighting system
            w = numpy.array(w)
            # force normalisation
            w /= w.sum()
            omega = w * 2 * numpy.pi
            sky = Skyvault.initialise(hmoy=el, azmoy=az, omega=omega, pc=w)
            
        met = MicroMeteo.initialise(doy=doy, hour=hour, Rglob=Rglob, Rdif=Rdif)

        dfvox = runRATP.DoIrradiation(grid, vegetation, sky, met)
        
        # 'PAR' is expected in  Watt.m-2 in RATP input,
        # whereas output is in micromol
        # => convert back to W.m2 (cf shortwavebalance, line 306)
        dfvox['ShadedPAR'] /= 4.6
        dfvox['SunlitPAR'] /= 4.6

        dfvox['Area'] = dfvox['ShadedArea'] + dfvox['SunlitArea']
        dfvox['PAR'] = (dfvox['ShadedPAR'] * dfvox['ShadedArea']
                        + dfvox['SunlitPAR'] * dfvox['SunlitArea']) / dfvox['Area']

        dfvox = dfvox.reset_index(drop=True)  # for backward compatibility reasons
        # TODO avoid and perform concat instead of merge
        dfvox = pandas.merge(dfvox, self.voxel_map.loc[:, ('VoxelId', 'x', 'y', 'z', 'Volume')])
        index = range(len(voxel_id))
        dfmap = pandas.DataFrame(
            {'primitive_index': index,
             'shape_id': shape_id,
             'VoxelId': voxel_id,
             'VegetationType': [self.entity[sh_id] for sh_id in shape_id],
             'primitive_area': areas}
        )

        return dfvox, dfmap


    def aggregate_light(self, dfvox, dfmap, spatial = True, temporal = True):
        """ Aggregate light outputs
        """
        output = pandas.merge(dfmap, dfvox)
        res = output
        
        def _process(df):
            shape_area = df['primitive_area'].sum()
            res = pandas.Series({   'VegetationType': df['VegetationType'].values[0],
                                    'day': df['day'].values[0],
                                    'hour': df['hour'].values[0],
                                    'ShadedPAR': numpy.sum(df['ShadedPAR'] * df['primitive_area']) / shape_area,#weighted mean of voxel values (weigth = primitive area)
                                    'SunlitPAR': numpy.sum(df['SunlitPAR'] * df['primitive_area']) / shape_area,
                                    'ShadedArea': numpy.sum(df['ShadedArea'] / df['Area'] * df['primitive_area']),#weighted mean of shaded fraction times shape_area
                                    'SunlitArea': numpy.sum(df['SunlitArea'] / df['Area'] * df['primitive_area']),
                                    'Area': shape_area,
                                    'PAR': numpy.sum(df['PAR'] * df['primitive_area']) / shape_area
            })
            return res
            
        
        if spatial:
            grouped = output.groupby(['Iteration', 'shape_id'])
            res = grouped.apply(_process).reset_index()
        if temporal:
            grouped = res.groupby(['shape_id'])
            how = {'VegetationType':numpy.mean, 'day':numpy.mean, 'hour':numpy.mean, 
                    'ShadedPAR':numpy.sum, 'SunlitPAR':numpy.sum, 
                    'ShadedArea': numpy.mean, 'SunlitArea': numpy.mean,
                    'Area': numpy.mean, 'PAR': numpy.sum}
            res = grouped.agg(how).reset_index()
            
        return res
      
    def plot(self, dfvox, dfmap, minval=None, maxval=None):
        output = pandas.merge(dfmap, dfvox)
        output = output.sort_values('primitive_index') # sort is needed to ensure matching with triangulation indices
        par = output['PAR']
        if minval is None:
            minval = min(par)
        if maxval is None:
            maxval = max(par)
        cmap = ColorMap()
        
        scene= pgl.Scene()
        discretizer = pgl.Discretizer()
        
        for sh in self.scene:
            discretizer.process(sh)
            mesh = discretizer.result
            mesh.colorList = []
            mesh.colorPerVertex = False
            colors = map(lambda x: cmap(x,minval,maxval,250., 20.), par[output['shape_id'] == sh.id])
            for color in colors:
                r, g, b = color
                mesh.colorList.append(pgl.Color4(r, g, b, 0))
                
            scene.add(mesh)
            
        pgl.Viewer.display(scene)
        
        return scene
            
