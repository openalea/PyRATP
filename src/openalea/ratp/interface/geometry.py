import numpy


def norm(vector):
    x, y, z = vector
    return numpy.sqrt(x ** 2 + y ** 2 + z ** 2)


def normed(vector):
    """ normalised coordinates of (0,point) vector
    """
    return numpy.array(vector) / norm(vector)


def spherical(vector):
    """ inclination (theta) and azimuth (phi) spherical angles"""
    x, y, z = normed(vector)
    theta = numpy.arccos(z)
    phi = numpy.arctan2(y, x)
    return theta, phi


def cartesian(theta, phi):
    """ cartesian coordinates of a unit vector with inclination theta and
    azimuth phi"""
    x = numpy.sin(theta) * numpy.cos(phi)
    y = numpy.sin(theta) * numpy.sin(phi)
    z = numpy.cos(theta)
    return x, y, z


def surface(face, vertices):
    a, b, c = [numpy.array(vertices[i]) for i in face]
    return norm(numpy.cross(b - a, c - a)) / 2.0


def normal(face, vertices):
    a, b, c = [numpy.array(vertices[i]) for i in face]
    return normed(numpy.cross(b - a, c - a))


def centroid(face, vertices):
    points = [numpy.array(vertices[i]) for i in face]
    x, y, z = zip(*points)
    return numpy.mean(x), numpy.mean(y), numpy.mean(z)


def random_normals(size=1):
    theta = numpy.pi / 2 * numpy.random.random_sample(size)
    phi = 2 * numpy.pi * numpy.random.random_sample(size)
    return zip(*cartesian(theta, phi))


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation arround
    the given axis by theta radians.
    """
    axis = numpy.asarray(axis)
    axis = axis / norm(axis)
    a = numpy.cos(theta / 2.0)
    b, c, d = -axis * numpy.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return numpy.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def rotate(points, rotation_mat):
    return [numpy.dot(rotation_mat, p) for p in points]


def move_points(xy_points, position = (0, 0, 0), orientation=(0, 0, 1),
                rotation=None):
    """ Move 2d xy points arround origin at 3D position with orientation

        If rotation is not None, points are rotated arround z before move
    """

    theta, phi = spherical(orientation)
    roty = rotation_matrix((0, 1, 0), theta)
    rotz = rotation_matrix((0, 0, 1), phi)
    x, y = zip(*xy_points)
    z = [0] * len(x)
    pts = zip(x, y, z)
    if rotation:
        rot = rotation_matrix((0, 0, 1), rotation)
        pts = rotate(pts, rot)
    px, py, pz = position

    newx, newy, newz = zip(*rotate(rotate(pts, roty), rotz))
    newx, newy, newz = px + numpy.array(newx), py + numpy.array(newy),\
                       pz + numpy.array(newz)

    return zip(newx, newy, newz)


def equilateral(area=1):
    """2d coordinates of an equilateral triangle centered on origin"""

    edge = 2 * numpy.sqrt(area / numpy.sqrt(3))
    height = numpy.sqrt(area * numpy.sqrt(3))

    return (
    (-edge / 2., -height / 3.), (edge / 2., -height / 3.), (0, 2 * height / 3.))


def unit_square_mesh():
    """A 2 triangle mesh representing ground unit area"""
    vertices = ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0))
    faces = ((0, 1, 2), (1, 2, 3))
    return vertices, faces