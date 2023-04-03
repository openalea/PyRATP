#
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>, November 2015
#

""" Methods for computing clumping indices of spatial distribution
"""

import numpy
from scipy import spatial


def _domain(pts):
    coords = numpy.array(numpy.ravel(pts)).reshape(len(pts[0]),len(pts))
    mins = coords.min(1)
    maxs = coords.max(1)
    return mins, maxs

def _volume(domain):   
    return numpy.prod(numpy.array(domain[1]) - numpy.array(domain[0]))
    
def _dnn(pts):
    """ distance to nearest neighbour for a set of points
    """
    
    tree = spatial.KDTree(pts)
    dnn = [d[1] for d in tree.query(pts,2)[0]]
    return dnn
    

def clark_evans(pts, domain=None, filter_boundary = False):
    """ Compute the clark and evans (1954) index of aggregation
    
        Parameters: 
        
        - pts: a list of point coordinates (n dimensions)
        - domain : a 2-tuple of n-tuples coordinates of extreme points (min, max) of the domain on which the index is to be computed.
                   If None, data extreme points are used
        - filter_boundary (bool): triger the filtering of border points in the estimation of the mean distance to neearest neibour.
                                  
    
        Details : 
            index = mean_of_distance_to_neighrest_neighbour / mean_distance_between_individual
            if distribution is random, index = 1, index tends to zero if data are clumped, and tens toward 2.15 if data are arranged in a perfectly repulsive pattern
            filtering boundary allows to avoid the bias due to the border effect described by Donnelly (1978), but requires a large sample to avoid too much waste/bias in the sub-sampling.
        Reference:
            Clark, P.J. and Evans, F.C., 1954. Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology 35: 445-453
            Donnelly, K. (1978) Simulations to determine the variance and edge-effect of total nearest neighbour distance. In Simulation methods in archaeology, Cambridge University Press, pp 91-95
    """
    
    if domain is None:
        domain = _domain(pts)
    
    n = len(pts)
    dimension = len(pts[0])
    
    density = float(n) / _volume(domain)
    
    
    # expected mean distance to nearest neighbour in case of a Poisson random point process
    re = 1. / (2 * numpy.power(density, 1. / dimension))
    
    # measured mean distance to nearest neighbour
    dnn = _dnn(pts)
    if filter_boundary:
        coords = numpy.array(numpy.ravel(pts)).reshape(dimension, n)
        lower_bound = numpy.repeat(domain[0], n).reshape(dimension, n) + 1.5 * re
        upper_bound = numpy.repeat(domain[1], n).reshape(dimension, n) - 1.5 * re
        dnn = numpy.array(dnn)[numpy.where((coords >= lower_bound) & (coords <= upper_bound))[1]]
    ra = numpy.mean(dnn)
        
    return float(ra) / re
    