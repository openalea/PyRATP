import sys
from openalea.mtg.aml import *
from openalea.plantgl.all import *
import cPickle

g = MTG("mtg_test.txt")

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
                wrt = '{0},'.format(q)
                f.write(wrt)
            f.write('\n')

f.close()

'''
file = open('ess_pickled.txt', 'w')
cPickle.dump(ess,file,0)
file.close()

op = open('ess_pickled.txt')
ess_read = cPickle.load(op)
op.close()
'''
