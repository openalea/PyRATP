""" Interfaces for PlantGL scene / PlantGL display"""

import numpy

pgl_imported = False
try:
    import openalea.plantgl.all as pgl
    pgl_imported = True
except ImportError:
    pgl = None


def bbox(pgl_scene, scene_unit='m'):
    """ Bounding box of a pgl scene"""
    tesselator = pgl.Tesselator()
    bbc = pgl.BBoxComputer(tesselator)
    bbc.process(pgl_scene)
    box = bbc.result
    xmin, ymin, zmin = box.getXMin(), box.getYMin(), box.getZMin()
    xmax, ymax, zmax = box.getXMax(), box.getYMax(), box.getZMax()
    if scene_unit != 'm':
        units = {'mm': 0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10,
                 'hm': 100,
                 'km': 1000}
        convert = units.get(scene_unit, 1)
        xmin, ymin, zmin = numpy.array((xmin, ymin, zmin)) * convert
        xmax, ymax, zmax = numpy.array((xmax, ymax, zmax)) * convert

    return (xmin, ymin, zmin), (xmax, ymax, zmax)


def shape_mesh(pgl_shape, discretiser=None):
    if discretiser is None:
        discretiser = pgl.Discretizer()
    discretiser.process(pgl_shape)
    tset = discretiser.result
    return numpy.array(tset.pointList), numpy.array(tset.indexList)


def as_scene_mesh(pgl_scene):
    """ Transform a PlantGL scene / PlantGL shape dict to a scene_mesh"""
    discretizer = pgl.Discretizer()

    if isinstance(pgl_scene, pgl.Scene):
        return {sh.id: shape_mesh(sh, discretizer) for sh in pgl_scene}
    elif isinstance(pgl_scene, dict):
        return {sh_id: shape_mesh(sh, discretizer) for sh_id, sh in
                pgl_scene.items()}
    else:
        return pgl_scene


def from_scene_mesh(scene_mesh, colors=None):
    plant_color = (0, 180, 0)

    if colors is None:
        colors = {k: plant_color for k in scene_mesh}

    scene = pgl.Scene()
    for sh_id, mesh in scene_mesh.items():
        vertices, faces = mesh
        if isinstance(colors[sh_id], tuple):
            r, g, b = colors[sh_id]
            color_list = [pgl.Color4(r, g, b, 0)] * len(faces)
        else:
            color_list = [pgl.Color4(r, g, b, 0) for r, g, b in colors[sh_id]]
        shape = pgl.TriangleSet(vertices, faces)
        shape.colorList = color_list
        shape.colorPerVertex = False
        shape.id = sh_id
        scene += shape

    return scene


def display(scene):
    """ display a scene"""
    pgl.Viewer.display(scene)
    return scene


def unit_sphere_scene():
    return pgl.Scene([pgl.Sphere()])
