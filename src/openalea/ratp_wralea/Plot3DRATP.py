from openalea.plantgl import scenegraph as sg
from openalea.plantgl.scenegraph._pglsg import Color3
import numpy as np

def Plot3DRATP(scene1, color):
    '''
      Change material of scene1 elements according to RATP output (i.e. color)
      color = liste de tuple !
      scene1  = scene1 plant GL
      update each  shape appearance attribute  with a new material object for changing colors !
    '''
    
    # write the node code here.
    for k,i in enumerate(scene1):
      NewColor = color[k]*65536
      R=  int(NewColor%256)
      G=  int((NewColor%65536)/256)
      B =  int(NewColor/65536)
      mat = sg.Material(name=str(k),ambient=Color3(R,G,B),diffuse=1.02,)
      i.appearance =  mat       # set material to the shape

    return scene1,