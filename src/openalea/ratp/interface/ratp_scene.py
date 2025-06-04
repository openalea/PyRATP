
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>


""" A high level class interface to RATP
"""
from collections import Iterable
import pyratpmobidiv.interface.pgl_scene as pgls
from alinea.pyratp.interface.display import display_property
import numpy
import pandas
from alinea.pyratp.grid import Grid
from alinea.pyratp.interface.clumping_index import get_clumping
from alinea.pyratp.interface.geometry import unit_square_mesh
from alinea.pyratp.interface.smart_grid import SmartGrid
from alinea.pyratp.interface.surfacic_point_cloud import SurfacicPointCloud
from alinea.pyratp.micrometeo import MicroMeteo
from alinea.pyratp.runratp import runRATP
from alinea.pyratp.skyvault import Skyvault
from alinea.pyratp.vegetation import Vegetation


def sample_database():
    """ to test if th creative commons database of french city fits
    """
    return {'Montpellier': {'city': 'Montpellier', 'latitude':43.61,
                            'longitude':3.87}}


def is_pgl_scene(scene):
    if not pgls.pgl_imported:
        return False
    else:
        return isinstance(scene, pgls.pgl.Scene)


class RatpScene(object):
    """ High level class interface for RATP lighting model
    """

    localisation_db = sample_database()
    timezone = 0  # consider UTC/GMT time for date inputs
    idecaly = 0   # regular grid
    nitrogen = 2  # dummy value (g.m-2) for nitrogen per leaf area

    def __init__(self, scene=None, grid=None, entities=None, rleaf=0.15,
                 rsoil=0.2, orientation=0, localisation='Montpellier',
                 scene_unit='m', **grid_kwds):
        """
        Initialise a RatpScene.

        Arguments:
        scene: a pyratp.interface.surfacic_point_cloud or a plantgl.Scene or a
        {shape_id: vertices, faces} scene mesh dict encoding the 3D scene
        grid: a pyratp.interface.smart_grid instance encoding the voxel grid.
         If None (default), the grid is adjusted to fit the input scene.
        entities: a {shape_id: entity} dict defining entities in the scene. If
         None (default), all shapes are considered as members of the same entity
        rleaf: leaf reflectance or a {entity: leaf_reflectance} property dict.
        rsoil: soil reflectance or a list of soil reflectances in PAR and NIR
        orientation (float): the angle (deg, positive clockwise) from X+ to
         North (default: 0)
        localisation : a string referencing a city of the localisation database
         (class variable), or a dict{'longitude':longitude, 'latitude':latitude}
        scene_unit: a string indicating unit used for scene coordinates

        Other named args to this function are used for controlling grid shape
        when grid=None

        """

        # scene_box will be used to construct grid, if grid is None
        scene_box = ((0, 0, 0), (1, 1, 1))

        if scene is None:
            scene = {'plant': unit_square_mesh()}

        if isinstance(scene, SurfacicPointCloud):
            self.scene = scene
            self.scene_mesh = scene.as_scene_mesh()
            if grid is None:
                scene_box = scene.bbox()
        elif is_pgl_scene(scene):
            self.scene_mesh = pgls.as_scene_mesh(scene)
            self.scene = SurfacicPointCloud.from_scene_mesh(self.scene_mesh,
                                                            scene_unit=scene_unit)
            if grid is None:
                scene_box = pgls.bbox(scene, scene_unit)
        else:
            try:
                self.scene_mesh = scene
                self.scene = SurfacicPointCloud.from_scene_mesh(scene,
                                                                scene_unit=scene_unit)
                if grid is None:
                    vertices, faces = zip(*scene.values())
                    vertices = reduce(lambda pts, new: pts + list(new), vertices, [])
                    x, y, z = zip(*vertices)
                    scene_box = (
                    (min(x), min(y), min(z)), (max(x), max(y), max(z)))
            except Exception as details:
                print(details)
                raise ValueError("Unrecognised scene format: should be one of pgl.Scene, "
                      "SurfacicPointCloud or {sh_id:(vertices, faces)} dict")

        if grid is None:
            self.smart_grid = SmartGrid(scene_box=scene_box, **grid_kwds)
        elif isinstance(grid, SmartGrid):
            self.smart_grid = grid
        else:
            raise ValueError('Unrecognised grid format: should be None or a '
                             'SmartGrid instance')

        if entities is None:
            entities = {sh_id: 'default' for sh_id in self.scene_mesh}
        self.entities = entities
        # RATP entity code starts at 1
        ent = list(set(self.entities.values()))
        self.entity_map = dict(zip(ent, range(1, len(ent) + 1)))
        self.entity_code = numpy.array(
            [self.entity_map[entities[sh]] for sh in self.scene.shape_id])

        if not isinstance(rleaf, dict):
            # if not hasattr(rleaf, '__len__'):
            #     rleaf = [rleaf]
            rleaf = {'default': rleaf}
        self.rleaf = {self.entity_map[k]: rleaf[k] for k in self.entity_map}

        if not hasattr(rsoil, '__len__'):
            rsoil = [rsoil]
        self.rsoil = rsoil

        self.orientation = orientation

        if not isinstance(localisation, dict):
            try:
                self.localisation = RatpScene.localisation_db[localisation]
            except KeyError:
                print('Warning : localisation', localisation, \
                    'not found in database, using default localisation', \
                    RatpScene.localisation_db.iter().next())
                self.localisation = RatpScene.localisation_db.itervalues().next()
        #

        self.distinc = None
        self.nbinclin=0
        self.mu = None
        self.ratp_grid = None
        self.grid_indices = None

    def n_entities(self):
        """ return the number of distinct entities in the canopy"""
        return max(self.entity_code)

    def clumping(self):
        if self.mu is None:
            spc = self.scene
            grid = self.smart_grid
            x, y, z = spc.x, spc.y, spc.z
            xv, yv, zv = grid.within_cell_position(x, y, z, normalise=True)
            jx, jy, jz = grid.grid_index(x, y, z)
            entity = self.entity_code
            data = pandas.DataFrame(
                {'entity': entity, 'x': xv, 'y': yv, 'z': zv, 's': spc.area,
                 'n': spc.normals,
                 'jx': jx, 'jy': jy, 'jz': jz})
            mu = []
            domain = ((0, 0, 0), (1, 1, 1))
            grouped = data.groupby('entity')
            for e, dfe in grouped:
                gvox = dfe.groupby(('jx', 'jy', 'jz'))
                clumps = []
                for k, df in gvox:
                    clumping = get_clumping(df['x'], df['y'], df['z'], df['s'],
                                            df['n'], domain=domain)
                    min_mu = df['s'].mean() / df[
                        's'].sum()  # minimal mu in the case of perfect clumping
                    clumps.append(max(min_mu, clumping))
                mu.append(numpy.mean(clumps))
            self.mu = mu

        return self.mu

    def grid(self, rsoil=0.2):

        """ Create and fill a RATP grid

        :Parameters:
        - rsoil : soil reflectances
        """
        if not hasattr(rsoil, '__len__'):
            rsoil = [rsoil]

        if self.ratp_grid is None or rsoil != self.rsoil:

            self.rsoil = rsoil
            spc = self.scene
            grid_pars = {'latitude': self.localisation['latitude'],
                         'longitude': self.localisation['longitude'],
                         'timezone': self.timezone,
                         'idecaly': self.idecaly,
                         'orientation': self.orientation,
                         'rs': self.rsoil,
                         'nent': self.n_entities()
                         }
            grid_pars.update(self.smart_grid.ratp_grid_parameters())
            ratp_grid = Grid.initialise(**grid_pars)
            grid_indices = self.smart_grid.grid_index(spc.x, spc.y, spc.z,
                                                      check=True)
            jx, jy, jz = self.smart_grid.ratp_grid_index(*grid_indices)
            entity = self.entity_code - 1  # Grid.fill expect python indices
            nitrogen = [self.nitrogen] * spc.size
            ratp_grid, _ = Grid.fill_from_index(entity, jx, jy, jz, spc.area,
                                           nitrogen, ratp_grid)
            # RATPScene grid indices of individual surfacic points
            jx, jy, jz = grid_indices
            self.grid_indices = pandas.DataFrame({'point_id': range(len(jx)),
                                                  'jx': jx, 'jy': jy, 'jz': jz})
            self.ratp_grid = ratp_grid

        return self.ratp_grid

    def inclinations(self):
        df = self.scene.inclinations()
        df_ent = pandas.DataFrame({'shape_id': self.scene.shape_id,
                                   'entity': self.entity_code}).drop_duplicates()
        df = df.merge(df_ent)
        return [group['inclination'].tolist() for name, group in
                df.groupby('entity')]

    def inclination_distribution(self, nbinclin=9):
        if self.distinc is None or self.nbinclin != nbinclin:
            def _dist(inc):
                dist = numpy.histogram(inc, self.nbinclin, (0, 90))[0]
                return dist.astype('float') / dist.sum()
            self.nbinclin = nbinclin
            inclinations = self.inclinations()
            self.distinc = map(_dist, inclinations)

        return self.distinc

    def voxel_index(self):
        """Mapping between RATP (filled) VoxelId and RatpScene grid indices"""

        grid = self.ratp_grid

        if grid is None:
            return pandas.DataFrame({})

        nveg = grid.nveg

        if nveg == 0:
            return pandas.DataFrame({})

        index = numpy.arange(1, nveg + 1)
        # RATP fortan indices
        numx, numy, numz = grid.numx[:nveg], grid.numy[:nveg], grid.numz[:nveg]
        # associated smart_grid indices
        jx, jy, jz = self.smart_grid.decode_ratp_indices(numx - 1, numy - 1,
                                                         numz - 1)

        return pandas.DataFrame({'VoxelId': index, 'jx': jx, 'jy': jy, 'jz': jz})

    def do_irradiation(self, rsoil=0.20, doy=1, hour=12, Rglob=1,
                       Rdif=1, mu=None, sources=None, nbinclin=9):
        """ Run a simulation of light interception for one wavelength

            Parameters:
                - rleaf : list of leaf refectance per entity
                - rsoil : soil reflectance
                - doy : [list of] day of year [for the different iterations]
                - hour : [list of] decimal hour (0-24) [for the different
                 iterations]
                - Rglob : [list of] global (direct + diffuse) radiation [for
                 the different iterations] (W.m-2)
                - Rdif : [list of] direct/diffuse radiation ratio [for the
                 different iterations] (0-1)
                - sources: a list of sequences giving elevation, azimuth,
                 steradians and weights of sky vault.
                if None, default RATP soc skyvault is used

        """

        nent = self.n_entities()

        if mu is None:
            mu = self.clumping()
            print(' '.join(['clumping evaluated:'] + [str(mu[i]) for i in
                                                      range(nent)]))
        else:
            if not isinstance(mu, Iterable):
                mu = [mu] * nent
        inclins = self.inclination_distribution(nbinclin)
        entities = [{'rf': [self.rleaf[i + 1]], 'distinc': inclins[i], 'mu': mu[i]} for i
                    in range(nent)]
        grid = self.grid(rsoil=rsoil)
        vegetation = Vegetation.initialise(entities, nblomin=1)
        if sources == None:
            sky = Skyvault.initialise()
        else:
            el, az, strd, w = sources
            sky = Skyvault.initialise(hmoy=el, azmoy=az, omega=strd, pc=w)
        met = MicroMeteo.initialise(doy=doy, hour=hour, Rglob=Rglob, Rdif=Rdif)
        res = runRATP.DoIrradiation(grid, vegetation, sky, met)

        VegetationType, Iteration, day, hour, VoxelId, ShadedPAR, SunlitPAR, \
        ShadedArea, SunlitArea = res.T
        # 'PAR' is expected in  Watt.m-2 in RATP input, whereas output is in
        #  micromol => convert back to W.m2 (cf shortwavebalance, line 306)
        dfvox = pandas.DataFrame({'VegetationType': VegetationType,
                                  'Iteration': Iteration,
                                  'day': day,
                                  'hour': hour,
                                  'VoxelId': VoxelId,
                                  'ShadedPAR': ShadedPAR / 4.6,
                                  'SunlitPAR': SunlitPAR / 4.6,
                                  'ShadedArea': ShadedArea,
                                  'SunlitArea': SunlitArea,
                                  'Area': ShadedArea + SunlitArea,
                                  'PAR': (
                                         ShadedPAR * ShadedArea + SunlitPAR *
                                         SunlitArea) / (
                                         ShadedArea + SunlitArea) / 4.6,
                                  })

        return pandas.merge(dfvox, self.voxel_index())

    def scene_lightmap(self, dfvox, spatial='point_id', temporal=True):
        """  Aggregate light outputs along scene inputs

        Args:
            dfvox: a pandas data frame with ratp outputs
            spatial: a string indicating the aggregation level: 'point_id' or
             'shape_id' .
            temporal: should iterations be aggregated ?

        Returns:
            a pandas dataframe with aggregated outputs

        """
        dfmap = pandas.merge(self.scene.as_data_frame(), self.grid_indices)
        aggregated_area = dfmap.loc[:, (spatial, 'area')].groupby(spatial).agg(
            'sum').reset_index()
        aggregated_area = aggregated_area.rename(columns={'area': 'agg_area'})
        output = pandas.merge(pandas.merge(dfmap, aggregated_area), dfvox)

        def _process(df):
            w = df['area'] / df['agg_area']
            a_agg = df['agg_area'].values[0]
            res = pandas.Series(
                {'VegetationType': df['VegetationType'].values[0],
                 'day': df['day'].values[0],
                 'hour': df['hour'].values[0],
                 'ShadedPAR': numpy.sum(df['ShadedPAR'] * w),
                 # weighted mean of voxel values (weigth = primitive area)
                 'SunlitPAR': numpy.sum(df['SunlitPAR'] * w),
                 'ShadedArea': numpy.sum(
                     df['ShadedArea'] / df['Area'] * w) * a_agg,
                 # weighted mean of shaded fraction times shape_area
                 'SunlitArea': numpy.sum(
                     df['SunlitArea'] / df['Area'] *w) * a_agg,
                 'Area': a_agg,
                 'PAR': numpy.sum(df['PAR'] * w)})
            return res

        grouped = output.groupby(['Iteration', spatial])
        res = grouped.apply(_process).reset_index()

        if temporal and len(set(res['Iteration'])) > 1:
            grouped = res.groupby(spatial)
            how = {'VegetationType': numpy.mean, 'day': numpy.mean,
                   'hour': numpy.mean,
                   'ShadedPAR': numpy.sum, 'SunlitPAR': numpy.sum,
                   'ShadedArea': numpy.mean, 'SunlitArea': numpy.mean,
                   'Area': numpy.mean, 'PAR': numpy.sum}
            res = grouped.agg(how).reset_index()

        if spatial == 'point_id':
            res = res.merge(self.scene.shape_map())
        return res

    def plot(self, dfvox, by='point_id', minval=None, maxval=None):
        lmap = self.scene_lightmap(dfvox, spatial=by)
        if by == 'shape_id':
            df = lmap.loc[:, ('shape_id', 'PAR')].set_index('shape_id')
            prop = {k: df['PAR'][k] for k in df.index}
        else:
            prop = {sh_id: df.to_dict('list')['PAR'] for sh_id, df in
                    lmap.groupby('shape_id')}
        return display_property(self.scene_mesh, prop, minval=minval,
                                maxval=maxval)
