from alinea.pyratp.grid import Grid, grid_index, decode_index
import numpy


def test_read():
    fn = 'essaiRATP2/RATP/grille/grid3Da_2004.grd'
    g = Grid()
    g = Grid.read(fn)
    assert (g.njx, g.njy ,g.njz) == (19,20,18)
    assert 0.19 <= g.dx <= 0.21

    
def test_initialise():
    pars = {'latitude':0, 'longitude':0, 'timezone':0,'nent':1,'rs':(0,0),'idecaly':0, 'orientation':0} 
    pars.update({ 'njx':2, 'njy':2, 'njz':2, 'dx':0.5, 'dy':0.5, 'dz':[0.5]*2, 'xorig' : 0, 'yorig':0, 'zorig':0})
    
    grid = Grid.initialise(**pars)
    assert (grid.njx, grid.njy ,grid.njz) == (2, 2, 2)
    assert 0.49 <= grid.dx <= 0.51
    
def test_grid_index():
    # a X+-North oriented 2x2x2 grid, one corner at (0,0,0), with 0.5 cell size in all directions
    #cell boundaries are thus (0, 0.5, 1)
    pars = {'latitude':0, 'longitude':0, 'timezone':0,'nent':1,'rs':(0,0),'idecaly':0, 'orientation':0} 
    pars.update({ 'njx':2, 'njy':2, 'njz':2, 'dx':0.5, 'dy':0.5, 'dz':[0.5]*2, 'xorig' : 0, 'yorig':0, 'zorig':0})
    
    grid = Grid.initialise(**pars)
    
    # test x,y,z cell centers
    centers = numpy.arange(0.25, 1, 0.5)
    x,y,z = [centers] * 3
    expected = ([0, 1], [1,0], [1,0])
    computed = grid_index(x, y, z, grid, toric=False)
    numpy.testing.assert_array_equal(computed, expected, 'Centers of voxel have not been positioned in the corect RATP voxel')
    jx, jy, jz = map(numpy.array, computed)
    decoded = decode_index(jx + 1, jy + 1, jz + 1, grid)
    numpy.testing.assert_array_equal(decoded, (x, y, z), 'bad decoding')

    # test x,y,z cell boundaries, non toric
    boundaries = numpy.arange(0, 1.5, 0.5)
    expected = ([0, 1, -1], [1, 0, -1], [1, 0, -1])
    x,y,z = [boundaries] * 3
    computed = grid_index(x, y, z, grid, toric=False)
    numpy.testing.assert_array_equal(computed, expected, 'Boundaries of voxel have not been positioned in the corect RATP voxel')

    # test x,y,z cell boundaries, toric
    boundaries = numpy.arange(0, 1.5, 0.5)
    expected = ([0, 1, 0], [1, 0, 1], [1, 0, -1])
    x,y,z = [boundaries] * 3
    computed = grid_index(x, y, z, grid, toric=True)
    numpy.testing.assert_array_equal(computed, expected, 'Toric boundaries of voxel have not been positioned in the corect RATP voxel')

    # test x,y,z left outer points, toric
    pts = numpy.arange(-.5, 1., 0.25)
    #array([-0.5 , -0.25,  0.  ,  0.25,  0.5 ,  0.75])
    expected = ([1, 1,0, 0, 1, 1], [0, 0, 1, 1, 0, 0], [-1, -1, 1, 1, 0, 0])
    x,y,z = [pts] * 3
    computed = grid_index(x, y, z, grid, toric=True)
    numpy.testing.assert_array_equal(computed, expected, 'outer left x,y points have not been positioned correctly in the toric grid')
    
    # test x,y,z left outer points, z translation,  toric
    pars.update({ 'zorig':0.5}) # origin is shited 0.5 toward the soil
    grid = Grid.initialise(**pars)
    pts = numpy.arange(-.5, 1., 0.25)
    #array([-0.5 , -0.25,  0.  ,  0.25,  0.5 ,  0.75])
    expected = ([1, 1,0, 0, 1, 1], [0, 0, 1, 1, 0, 0], [1, 1, 0, 0, -1, -1])
    x,y,z = [pts] * 3
    computed = grid_index(x, y, z, grid, toric=True)
    numpy.testing.assert_array_equal(computed, expected, 'outer left x,y,z points have not been positioned correctly after z translation in the toric grid')
