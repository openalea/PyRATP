import numpy
from alinea.pyratp.interface.display import jet_colors, property_as_colors, \
    display_property


def test_jet_colors():
    colors = jet_colors(range(10))
    expected = [(20, 20, 250),
                (20, 147, 250),
                (20, 250, 224),
                (20, 250, 96),
                (71, 250, 20),
                (198, 250, 20),
                (250, 173, 20),
                (250, 45, 20),
                (250, 20, 20),
                (250, 20, 20)]
    numpy.testing.assert_array_equal(colors, expected)

    colors = jet_colors(range(10), minval=0, maxval=100)
    expected = [(20, 20, 250),
                (20, 31, 250),
                (20, 43, 250),
                (20, 54, 250),
                (20, 66, 250),
                (20, 77, 250),
                (20, 89, 250),
                (20, 100, 250),
                (20, 111, 250),
                (20, 123, 250)]

    numpy.testing.assert_array_equal(colors, expected)


def test_property_as_colors():
    properties = {'a_property': {1: 9, 2: 0}, 'another': {1: [9], 2: [0, 5]}}
    colors = property_as_colors(properties['a_property'])
    assert colors[1] == (250, 20, 20)
    assert colors[2] == (20, 20, 250)
    colors = property_as_colors(properties['another'])
    assert colors[2][0] == (20, 20, 250)
    assert colors[2][1] == (198, 250, 20)

    colors = property_as_colors(properties['a_property'], minval=0, maxval=100)
    assert colors[1] == (20, 123, 250)
    assert colors[2] == (20, 20, 250)


def test_display_property():
    faces = ((0, 1, 2), (0, 2, 3), (0, 1, 3))
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    s_mesh = {1: (vertices, (faces[1],)),
              2: (vertices, [faces[i] for i in (0, 2)])}
    a_property = {1: 0, 2: 9}
    sc = display_property(s_mesh, a_property)

