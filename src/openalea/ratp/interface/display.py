import warnings
from itertools import chain
from math import isnan

from alinea.pyratp.interface.color_map import ColorMap
import pyratpmobidiv.interface.pgl_scene as pgls


def jet_colors(x, minval=None, maxval=None):
    """ return jet colors associated to a vector of values"""
    if minval is None:
        minval = min(x)
    if maxval is None:
        maxval = max(x)
    cmap = ColorMap()

    return map(lambda v: cmap(v, minval, maxval, 250., 20.), x)


def nan_to_zero(values):
    return [0 if isnan(x) else x for x in values]


def property_as_colors(a_property, minval=None, maxval=None, gamma=None):
    """ transform a scalar property in a color property of same kind

        property is a {shape_id: value} or {shape_id: list of values} dict
    """

    values = a_property.values()
    if isinstance(values[0], list):
        values = list(chain.from_iterable(values))
    values = nan_to_zero(values)
    if minval is None:
        minval = min(values)
    if maxval is None:
        maxval = max(values)
    if gamma is None:
        gamma = 1
    norm = 0.5
    if minval != maxval:
        norm = maxval - minval
    values = map(lambda x: ((x - minval) / float(norm)) ** gamma, values)
    colors = jet_colors(values, 0, 1)
    color_property = {}
    for k, v in a_property.items():
        if isinstance(v, list):
            color_property[k] = []
            for i in range(len(v)):
                color_property[k].append(colors.pop(0))
        else:
            color_property[k] = colors.pop(0)

    return color_property


def display_property(scene_mesh, property, minval=None, maxval=None):
    colors = property_as_colors(property, minval=minval, maxval=maxval)
    if pgls.pgl_imported:
        scene = pgls.from_scene_mesh(scene_mesh, colors)
        return pgls.display(scene)
    else:
        warnings.warn('PlanGL not found, no display available!!')
        return scene_mesh

