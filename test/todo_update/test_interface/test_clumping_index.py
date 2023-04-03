""" unit tests for clumping_index
"""
import numpy
from alinea.pyratp.interface.clumping_index import clark_evans, expand_point, \
    expand_points, get_clumping


def test_clark_evans():

    # a regular 3D grid
    vals = numpy.linspace(0, 1, 10)
    pts = [(x, y, z) for x in vals for y in vals for z in vals]
    domain = ((0, 0, 0), (1, 1, 1))
    print 'grid', clark_evans(pts, domain, filter_boundary=False)
    print 'grid corrected', clark_evans(pts, domain, filter_boundary=True)
    
    # a 2D random sample
    x, y = numpy.random.random_sample((2, 100))
    pts = zip(x, y)
    domain = ((0, 0), (1, 1))
    print 'random2D', clark_evans(pts, domain, filter_boundary=False)
    print 'random2D corrected', clark_evans(pts, domain, filter_boundary=True)
    
    # a 3D random sample
    x, y, z = numpy.random.random_sample((3, 100))
    pts = zip(x, y, z)
    domain = ((0, 0, 0), (1, 1, 1))
    print 'random3D', clark_evans(pts, domain, filter_boundary=False)
    print 'random3D corrected', clark_evans(pts, domain, filter_boundary=True)


def test_expand_point():
    x, y, z = 1.5, 1.5, 0
    area = 9
    normal = (0, 0, 1)
    expanded = zip(*expand_point(x, y, z, area, normal))
    expected0 = [(0.5, 2.5, 0.0),
                (1.5, 2.5, 0.0),
                (2.5, 2.5, 0.0),
                (0.5, 1.5, 0.0),
                (1.5, 1.5, 0.0),
                (2.5, 1.5, 0.0),
                (0.5, 0.5, 0.0),
                (1.5, 0.5, 0.0),
                (2.5, 0.5, 0.0)]
    numpy.testing.assert_array_equal(expanded, expected0)

    # with domain
    domain = (0, 0, 0), (1, 1, 1)
    expected = [(0.5, 1.0, 0.0),
                (1.0, 1.0, 0.0),
                (1.0, 1.0, 0.0),
                (0.5, 1.0, 0.0),
                (1.0, 1.0, 0.0),
                (1.0, 1.0, 0.0),
                (0.5, 0.5, 0.0),
                (1.0, 0.5, 0.0),
                (1.0, 0.5, 0.0)]
    expanded = zip(*expand_point(x, y, z, area, normal, domain=domain))
    numpy.testing.assert_array_equal(expanded, expected)

    # rotated expansion
    x1, y1, z1 = 0, 1.5, 1.5
    normal1 = (1, 0, 0)
    expanded = zip(*expand_point(x1, y1, z1, area, normal1))
    expected1 = [(0, 2.5, 2.5),
                 (0, 2.5, 1.5),
                 (0, 2.5, 0.5),
                 (0, 1.5, 2.5),
                 (0.0, 1.5, 1.5),
                 (0, 1.5, 0.5),
                 (0, 0.5, 2.5),
                 (0.0, 0.5, 1.5),
                 (0, 0.5, 0.5)]
    numpy.testing.assert_almost_equal(expanded, expected1)

    # multiple points
    x, y, z = 1.5, 1.5, 0
    x1, y1, z1 = 0, 1.5, 1.5
    xn, yn, zn = (x, x1), (y, y1), (z, z1)
    arean = [area] * 2
    normaln = (normal, normal1)
    expanded = zip(*expand_points(xn, yn, zn, arean, normaln))
    numpy.testing.assert_almost_equal(expanded, expected0 + expected1)


def test_clumping():
    x, y, z = numpy.random.random_sample((3, 100))
    s = [0.01] * 100
    n = [(0, 0, 1)] * 100
    domain = ((0, 0, 0), (1, 1, 1))

    print 'random3D', get_clumping(x, y, z, s, n, domain, expand=False)
    print 'random3D expanded', get_clumping(x, y, z, s, n, domain, expand=True)
