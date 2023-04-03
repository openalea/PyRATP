import numpy
from alinea.pyratp.interface.geometry import normed, spherical, cartesian, \
    surface, normal, centroid, random_normals, move_points, unit_square_mesh


def test_spherical():
    v = normed((1, 0, 1))
    theta, phi = spherical(v)
    assert phi == 0
    numpy.testing.assert_almost_equal(theta, numpy.pi / 4)
    cart = cartesian(theta, phi)
    numpy.testing.assert_almost_equal(cart, v)


def test_triangle_math():
    face = range(3)
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0))

    numpy.testing.assert_almost_equal(surface(face, vertices), 0.5)
    numpy.testing.assert_almost_equal(normal(face, vertices), (0, 0, 1))
    numpy.testing.assert_almost_equal(centroid(face, vertices), (1./3, 1./3, 0))


def test_random_normals():
    n = random_normals(1)
    assert len(n) == 1
    assert len(n[0]) == 3
    n = random_normals(10)
    assert len(n) == 10
    assert len(n[0]) == 3


def test_move_points():
    vertices, faces = unit_square_mesh()
    x, y, z = zip(*vertices)
    newpoints = move_points(zip(x, y))