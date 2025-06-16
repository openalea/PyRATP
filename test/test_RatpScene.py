""" Unit tests for RatpScene module
"""
from openalea.ratp.RatpScene import RatpScene

from openalea.plantgl import all as pgl

def scene():
    s = pgl.Scene()
    #s.add(pgl.Sphere(slices=64,stacks=64))
    s.add(pgl.Sphere())
    return s

def test_init():
    s = RatpScene()
    assert s
    
    
def test_fitgrid():

    sc = scene()
    s = RatpScene(sc)

    assert s.fit_grid()
    
def test_scene_transform():

    sc = scene()
    s = RatpScene(sc)

    assert s.scene_transform()
    
def test_grid():
    sc = scene()
    s = RatpScene(sc)
    
    assert s.grid()
    
def test_irradiation():
    sc = scene()    
    s = RatpScene(sc)
    dfoutput = s.do_irradiation()
    s.aggregate_light(dfoutput)

    
def test_plot():
    sc = scene()
    s = RatpScene(sc)
    dfoutput = s.do_irradiation()
    s.plot(dfoutput[dfoutput['Iteration'] == 1])
    
