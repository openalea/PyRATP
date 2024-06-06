import os
import tempfile
import numpy

from alinea.pyratp.interface.smart_grid import SmartGrid


def test_instantiate():
    grid = SmartGrid()
    assert grid.z_soil == 0
    assert not grid.toric
    assert grid.domain is None
    assert grid.x_dz is None
    numpy.testing.assert_array_equal(grid.origin, grid.default['origin'])
    numpy.testing.assert_array_equal(grid.resolution,
                                     grid.default['resolution'])
    numpy.testing.assert_array_equal(grid.shape, grid.default['shape'])


def test_auto_fit():
    scene_box = ((0, 0, 0), (1, 1, 1))
    domain = ((-0.1, -0.1), (1.1, 1.1))

    grid = SmartGrid(scene_box)
    numpy.testing.assert_array_equal(grid.shape, grid.default['shape'])
    grid_box = grid.bbox()
    numpy.testing.assert_array_less(grid_box[0], scene_box[0])
    numpy.testing.assert_array_less(scene_box[1], grid_box[1])

    grid = SmartGrid(scene_box, domain=domain)
    numpy.testing.assert_array_equal(grid.shape, grid.default['shape'])
    grid_box = grid.bbox()
    numpy.testing.assert_array_less(grid_box[0][:-1], domain[0])
    numpy.testing.assert_array_less(domain[1], grid_box[1][:-1])

    grid = SmartGrid(scene_box, toric=True)
    numpy.testing.assert_array_equal(grid.shape, grid.default['shape'])
    grid_box = grid.bbox()
    numpy.testing.assert_array_equal(grid_box[0][:-1], scene_box[0][:-1])
    numpy.testing.assert_array_equal(scene_box[1][:-1], grid_box[1][:-1])

    grid = SmartGrid(scene_box, resolution=[0.1, 0.1, 0.1])
    numpy.testing.assert_array_equal(grid.resolution, [0.1, 0.1, 0.1])
    numpy.testing.assert_array_equal(grid.shape, [11, 11, 11])

    grid = SmartGrid(scene_box, resolution=[0.1, 0.1, 0.1], toric=True)
    numpy.testing.assert_array_equal(grid.resolution, [0.1, 0.1, 0.1])
    numpy.testing.assert_array_equal(grid.shape, [10, 10, 11])

    grid = SmartGrid(scene_box, resolution=[0.1, 0.1, 0.1], toric=True,
                     z_soil=-1)
    assert grid.z_soil == -1
    numpy.testing.assert_array_equal(grid.shape, [10, 10, 21])

    grid = SmartGrid(scene_box, x_dz=(0.7, 0.4))
    numpy.testing.assert_array_equal(grid.shape, [10, 10, 2])
    numpy.testing.assert_raises(ValueError, SmartGrid, scene_box,
                                x_dz=(0.7, 0.3))

    flat_scene = ((0, 0, 0), (0, 0, 0))
    grid = SmartGrid(flat_scene)
    numpy.testing.assert_array_less((0, 0, 0), grid.resolution)
    grid = SmartGrid(flat_scene, resolution=[0.1, 0.1, 0.1])
    numpy.testing.assert_array_equal(grid.shape, [1, 1, 1])

    flat_zscene = ((0, 0, 0), (1, 1, 0))
    grid = SmartGrid(flat_zscene)
    assert grid.resolution[2] == grid.resolution[0]


def test_serialisation():
    scene_box = ((-numpy.pi, 0, 0), (1, 1, 1))
    grid = SmartGrid(scene_box, resolution=[0.1, 0.1, 0.1], toric=True,
                     z_soil=-1)

    assert grid.z_soil == -1
    numpy.testing.assert_array_equal(grid.shape, [42, 10, 21])
    numpy.testing.assert_array_almost_equal(grid.origin,
                                            (-3.1707963267948966, 0.0, -1),
                                            decimal=6)

    try:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        grid.save(path)
        grid = SmartGrid.load(path)

        assert grid.z_soil == -1
        numpy.testing.assert_array_equal(grid.shape, [42, 10, 21])
        numpy.testing.assert_array_almost_equal(grid.origin,
                                                (-3.1707963267948966, 0.0, -1),
                                                decimal=6)
    except Exception as e:
        raise e
    finally:
        os.remove(path)
        os.rmdir(tmpdir)


def test_grid_index():
    # similar to grid_index tests in ratp.test_grid
    grid = SmartGrid(shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5))
    toric_grid = SmartGrid(shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5),
                           toric=True)
    xdz_grid = SmartGrid(shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5),
                         x_dz=[0.8, 0.2])

    # test x,y,z cell centers
    centers = numpy.arange(0.25, 1, 0.5)
    x,y,z = [centers] * 3
    # array([ 0.25,  0.75]), array([ 0.25,  0.75]), array([ 0.25,  0.75])
    expected = [0, 1], [0, 1], [0, 1]
    expected_ratp = [0, 1], [1, 0], [1, 0]
    computed = grid.grid_index(x, y, z)
    computed_ratp = grid.ratp_grid_index(*computed)
    numpy.testing.assert_array_equal(computed, expected)
    numpy.testing.assert_array_equal(computed_ratp, expected_ratp)

    # test x,y,z cell centers, xdz grid
    centers = numpy.arange(0.25, 1, 0.5)
    x,y,z = [centers] * 3
    # array([ 0.25,  0.75]), array([ 0.25,  0.75]), array([ 0.25,  0.75])
    expected = [0, 1], [0, 1], [0, 0]
    expected_ratp = [0, 1], [1, 0], [1, 1]
    computed = xdz_grid.grid_index(x, y, z)
    computed_ratp = xdz_grid.ratp_grid_index(*computed)
    numpy.testing.assert_array_equal(computed, expected)
    numpy.testing.assert_array_equal(computed_ratp, expected_ratp)

    # test x,y,z cell boundaries, non toric
    boundaries = numpy.arange(0, 1.5, 0.5)
    x, y, z = [boundaries] * 3
    expected = [0, 1, 2], [0, 1, 2], [0, 1, 2]
    expected_ratp = [0, 1, 2], [1, 0, -1], [1, 0, -1]
    computed = grid.grid_index(x, y, z)
    computed_ratp = grid.ratp_grid_index(*computed)
    numpy.testing.assert_array_equal(computed, expected)
    numpy.testing.assert_array_equal(computed_ratp, expected_ratp)

    # test x,y,z cell boundaries, toric
    boundaries = numpy.arange(0, 1.5, 0.5)
    x, y, z = [boundaries] * 3
    expected =  [0, 1, 0], [0, 1, 0], [0, 1, 2]
    expected_ratp = [0, 1, 0], [1, 0, 1], [1, 0, -1]
    x, y, z = [boundaries] * 3
    computed = toric_grid.grid_index(x, y, z)
    computed_ratp = toric_grid.ratp_grid_index(*computed)
    numpy.testing.assert_array_equal(computed, expected)
    numpy.testing.assert_array_equal(computed_ratp, expected_ratp)

    # test x,y,z left outer points, toric
    pts = numpy.arange(-.5, 1., 0.25)
    # array([-0.5 , -0.25,  0.  ,  0.25,  0.5 ,  0.75])
    expected_ratp = ([1, 1, 0, 0, 1, 1], [0, 0, 1, 1, 0, 0], [2, 2, 1, 1, 0, 0])
    x, y, z = [pts] * 3
    computed = toric_grid.grid_index(x, y, z)
    computed_ratp = toric_grid.ratp_grid_index(*computed)
    numpy.testing.assert_array_equal(computed_ratp, expected_ratp)

    # test x,y,z left outer points, z translation,  toric
    grid = SmartGrid(shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5), toric=True,
                     z_soil=-0.5)
    pts = numpy.arange(-.5, 1., 0.25)
    # array([-0.5 , -0.25,  0.  ,  0.25,  0.5 ,  0.75])
    expected_ratp = ([1, 1, 0, 0, 1, 1], [0, 0, 1, 1, 0, 0], [1, 1, 0, 0, -1, -1])
    x, y, z = [pts] * 3
    computed = grid.grid_index(x, y, z)
    computed_ratp = grid.ratp_grid_index(*computed)
    numpy.testing.assert_array_equal(computed_ratp, expected_ratp)


def test_ratp_parameters():
    grid = SmartGrid()
    pars = grid.ratp_grid_parameters()
    return pars

def test_voxel_centers():
    grid = SmartGrid(shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5))
    centers = grid.voxel_centers([0,1],[0,1],[0,1])
    expected = ([ 0.25,  0.75], [ 0.25,  0.75], [ 0.25,  0.75])
    numpy.testing.assert_array_equal(centers, expected)

    scene_box = ((0.25, 0.25, 0.25), (1.25, 1.25, 1.25))
    grid = SmartGrid(scene_box, shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5))
    centers = grid.voxel_centers([0,1],[0,1],[0,1])
    expected = ([ 0.5,  1], [ 0.5,  1], [ 0.5,  1])
    numpy.testing.assert_array_equal(centers, expected)

    grid = SmartGrid(shape=(2, 2, 2), resolution=(0.5, 0.5, 0.5),x_dz=[0.1, 0.3])
    centers = grid.voxel_centers([0,1],[0,1],[0,1])
    expected = ([ 0.25,  0.75], [ 0.25,  0.75], [ 0.05,  0.25])
    numpy.testing.assert_array_equal(centers, expected)