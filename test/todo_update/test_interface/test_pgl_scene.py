import alinea.pyratp.interface.pgl_scene as pgls
import numpy

if pgls.pgl_imported:

    def test_bbox():
        scene = pgls.unit_sphere_scene()
        box = pgls.bbox(scene)
        numpy.testing.assert_array_equal(box,
                                         ((-0.5, -0.5, -0.5), (0.5, 0.5, 0.5)))
        box = pgls.bbox(scene, scene_unit='dam')
        numpy.testing.assert_array_equal(box, ((-5, -5, -5), (5, 5, 5)))


    def test_shape_mesh():
        shape = pgls.pgl.Sphere()
        vertices, faces = pgls.shape_mesh(shape)
        assert len(vertices) == 58
        assert len(vertices[0]) == 3
        assert len(faces) == 112
        assert len(faces[0]) == 3

    def test_as_scene_mesh():
        sphere = pgls.pgl.Sphere()
        scene = pgls.pgl.Scene([sphere, sphere])
        sh_id = [sh.id for sh in scene]
        s_mesh = pgls.as_scene_mesh(scene)
        assert len(s_mesh) == 2
        assert len(s_mesh[sh_id[1]]) == 2

        geom = {'bud': sphere}
        s_mesh = pgls.as_scene_mesh(geom)
        assert 'bud' in s_mesh


    def test_from_scene_mesh():
        faces = ((0, 1, 2), (0, 2, 3), (0, 1, 3))
        vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        s_mesh = {1: (vertices, (faces[1],)),
                  2: (vertices, [faces[i] for i in (0, 2)])}
        # default color
        scene = pgls.from_scene_mesh(s_mesh)
        assert len(scene) == 2
        assert scene[0].geometry.colorList[0].green == 180
        # one color per shape
        scene = pgls.from_scene_mesh(s_mesh,
                                     colors={1: (0, 0, 0), 2: (1, 1, 1)})
        assert scene[0].geometry.colorList[0].green == 0
        assert scene[1].geometry.colorList[0].green == 1
        # one color per triangle
        scene = pgls.from_scene_mesh(s_mesh,
                                     colors={1: (0, 0, 0),
                                             2: [(1, 1, 1), (2, 2, 2)]})
        assert scene[0].geometry.colorList[0].green == 0
        assert scene[1].geometry.colorList[0].green == 1
        assert scene[1].geometry.colorList[1].green == 2
