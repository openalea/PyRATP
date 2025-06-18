import sys
from openalea.mtg import *
from openalea.mtg.aml import *
import numpy as np

def extract_leaves(g, factor=100, nitrogen=2, grid_definition=None):
    """ Return the list of leaves with some properties.

    :Returns:
        Return for each leaf:
            - the id in the mtg
            - the vegetation type
            -  X, Y, Z coordinates
            - leaf area
            - leaf nitrogen content (:math:`g/m^2`)
    """
    x, y, z=g.property('XX'), g.property('ZZ'), g.property('YY')

    x = dict((k, v*factor) for k, v in x.items())
    y = dict((k, v*factor) for k, v in y.items())
    z = dict((k, v*factor) for k, v in z.items())

    max_scale = g.max_scale()
    leaf_area = g.property('leaf_area')
    leaves = [vid for vid in g.vertices(scale=max_scale) if leaf_area.get(vid,0)]
    leaves.sort()

    leaf_type = {}
    for vid in g.vertices(scale=2):
        l = [v for v in g.components_at_scale(vid, scale=max_scale) if leaf_area.get(v,0)]
        klass = g.class_name(vid)
        length = len(l)
        _entity = 1 #entity(klass, length)
        leaf_type.update(dict((k,_entity) for k in l))

    # convert dict into array

    _leaves = np.array(leaves)
    _leaf_type = np.array(list(leaf_type[vid] for vid in leaves), dtype=np.int)-1
    _x = np.array(list(x[vid] for vid in leaves))
    _y = np.array(list(y[vid] for vid in leaves))
    _z = np.array(list(z[vid] for vid in leaves))
    _leaf_area = np.array(list(leaf_area[vid] for vid in leaves))
    _leaf_nitrogen = np.ones(len(leaves))*nitrogen

    return _leaves, _leaf_type, _x, _y, _z, _leaf_area, _leaf_nitrogen

def test(fn = "mtg_test.txt"):
    g = MTG("mtg_test.txt")
    factor = 100

    l, lt, x, y, z, la, ln = extract_leaves(g)
    print(len(l))



def entity(klass, length):
    if klass == 'I':
        if length > 10:
            return 4
        else:
            return 3
    elif length > 10:
        return 2
    else:
        return 1








'''
def Z(x):
   val = Feature(x,"YY")
   if not val is None:
      return val * 100.
   else:
      if x != MTGRoot():
         raise Exception("The item " + str(x)
                         + ", different from the root, in the MTG without a Z coord was found")
      return None

def X(x):
   val = Feature(x,"XX")
   if not val is None:
      return val * 100.
   else:
      if x != MTGRoot():
         raise Exception("The item " + str(x)
                         + ", different from the root, in the MTG without a X coord was found")
      return None

def Y(x):
   val = Feature(x,"ZZ")
   if not val is None:
      return val * 100.
   else:
      if x != MTGRoot():
         raise Exception("The item " + str(x)
                         + ", different from the root, in the MTG without a Y coord was found")
      return None

def leaf_area(x):
    return Feature(x, "leaf_area")

def gu(x):
    return Components(x, Scale = 2)

def gu_leaf(x) :
    return [y for y in gu(x) if leaf_area(it(y)[0]) > 0]

def firstgu_leaf(x):
    return [y for y in gu_leaf(x) if Pos(gu_leaf(x), Father(y)) == Undef]

def as_type(x):
    if Class(x) =='I' and Size([Components(y) for y in Descendants(x)]) > 10 :
        return 4
    elif Class(x) =='I' and Size([Components(y) for y in Descendants(x)]) < 10 :
        return 3
    elif Class(x) !='I' and Size([Components(y) for y in Descendants(x)]) > 10 :
        return 2
    else :
        return 1

#def veg_flor_state(x):

ess= [[[[Index(x), as_type(x), X(y), Y(y), Z(y), leaf_area(y)] for y in Components(z)] for z in Descendants(x)] for x in firstgu_leaf(1)]

f = open('ess.csv', 'w')
for i in ess:
    for j in i:
        for p in j:
            for q in p:
                wrt = "{0},".format(q)
                f.write(wrt)
            f.write('\n')

f.close()
'''
'''
file = open('ess_pickled.txt', 'w')
cPickle.dump(ess,file,0)
file.close()

op = open('ess_pickled.txt')
ess_read = cPickle.load(op)
op.close()
'''
