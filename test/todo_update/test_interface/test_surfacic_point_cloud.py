import os
import tempfile

import numpy
from alinea.pyratp.interface.surfacic_point_cloud import SurfacicPointCloud


def test_spc_instantiation():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    for w in (
    'x', 'y', 'z', 'area', 'shape_id', 'normals', 'properties', 'size'):
        assert hasattr(spc, w)
    spc = SurfacicPointCloud(100, 100, 100, 10000, scene_unit='cm')
    assert spc.x == spc.y == spc.z == spc.area == 1  # m2

    faces = (range(3),)
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0))
    sc = {'0': (vertices, faces)}
    spc = SurfacicPointCloud.from_scene_mesh(sc)
    assert spc.area == 0.5
    numpy.testing.assert_array_equal(spc.normals, ((0, 0, 1),))


def test_data_frame():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    df = spc.as_data_frame()
    assert df.shape == (1, 9)
    spc.properties.update({'a_property': {0: 3}})
    df = spc.as_data_frame()
    assert df.shape == (1, 10)


def test_as_scene_mesh():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    sc = spc.as_scene_mesh()
    assert 0 in sc
    v, f, = sc[0]
    assert len(f) == 1
    assert len(v) == 3


def test_as_triangle_scene():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    sc = spc.as_triangle_scene()
    assert 0 in sc
    triangles = sc[0]
    assert len(triangles) == 1
    pts = triangles[0]
    assert len(pts) == 3
    assert len(pts[0]) == 3


def test_serialisation():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    try:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.csv')
        spc.save(path)
        spc2 = SurfacicPointCloud.load(path)
        assert spc.x == spc2.x
        numpy.testing.assert_almost_equal(spc.normals, spc2.normals)

        spc.properties.update({'a_property': {0: 3}})
        spc.save(path)
        spc2 = SurfacicPointCloud.load(path)
        assert 'a_property' in spc2.properties
        for k in spc.properties['a_property']:
            assert k in spc2.properties['a_property']
    except Exception as e:
        raise e
    finally:
        os.remove(path)
        os.rmdir(tmpdir)


def test_bbox():
    faces = ((0, 1, 2), (0, 2, 3), (0, 1, 3))
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    sc = {'0': (vertices, faces)}
    spc = SurfacicPointCloud.from_scene_mesh(sc)
    expected = ((0.0, 0.0, 0.0), [1. / 3] * 3)
    numpy.testing.assert_almost_equal(spc.bbox(), expected)


def test_inclinations():
    faces = ((0, 1, 2), (0, 2, 3), (0, 1, 3))
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    sc = {1: (vertices, (faces[1],)), 2: (vertices, [faces[i] for i in (0, 2)])}
    spc = SurfacicPointCloud.from_scene_mesh(sc)
    df = spc.inclinations()
    inc = {g: x.to_dict('list')['inclination'] for g, x in
     df.groupby('shape_id')}
    numpy.testing.assert_array_equal(inc[1], [90.0])
    numpy.testing.assert_array_equal(inc[2], [0.0, 90.0])


def test_subset():
    faces = ((0, 1, 2), (0, 2, 3), (0, 1, 3))
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    sc = {1: (vertices, (faces[1],)), 2: (vertices, [faces[i] for i in (0, 2)])}
    spc = SurfacicPointCloud.from_scene_mesh(sc)
    sub = spc.subset(point_id=1)
    assert len(sub.as_data_frame()==1)
    sub = spc.subset(shape_id=2)
    assert len(sub.as_data_frame()==2)


