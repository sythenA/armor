#   smoothCutoff.py
#   function to create a smooth cutoff of a given set
#   with the sigmoid function
#   under construction - 2014-03-14

import numpy as np
from scipy.interpolate import Rbf

def sigmoid(x):
    return 1./(1+np.exp(-x))


def rbf(arr, radius=10, threshold=0):
    """
    use:
        gradually slopiing off to (almost) 0 in the given radius
    ref:
        http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html#using-radial-basis-functions-for-smoothing-interpolation
    input:  
        arr     - an np.array
        radius  - a number

    """
    #   procedure:  1.  given array arr in centre;
    #               2.  threshold on the edge;  unknown values set as -999
    #               3.  build the x,y,z lists, skipping the z=-999
    #               4.  interpolate
    
    height, width   = arr.shape
    arr2            = np.ones((height+radius*2, width+radius*2)) * (-999.)
    arr2[0  , :]    = threshold   
    arr2[-1 , :]    = threshold   
    arr2[:  , 0]    = threshold
    arr2[:  ,-1]    = threshold
    arr2[radius:-radius , radius:-radius]   = arr      
    
    X, Y    = np.meshgrid(range(width+radius*2), range(height+radius*2))
    I, J    = Y.copy(), X.copy()
    Ii, Ji  = Y, X
    Z       = arr2
    I       = I.flatten()
    J       = J.flatten()
    Z       = Z.flatten()

    n       = len(Z)       
    I       = [I[t] for t in range(n) if Z[t]!=-999.]
    J       = [J[t] for t in range(n) if Z[t]!=-999.]
    Z       = [Z[t] for t in range(n) if Z[t]!=-999.]
    f       = Rbf(I, J, Z)
    Zi      = f(Ii, Ji)
    arr3    = np.reshape(Zi, (height+radius*2, width+radius*2))
    return arr3


def linearMask(height, width, r=10):
    """
    fade linearly to 0
    rectangular shape assumed
    r = width of buffer band
    """
    #arr2            = np.zeros((height+r*2, width+r*2)).astype(float)
    arr2            = np.zeros((height, width)).astype(float) # this convention makes more sense. 2013-12-16
    arr2[r  :-r ,   r   :-r]    = 1.
    
    for i in range(r):
        arr2[i      ,  i:-i]      = 1.*i/r
        arr2[-1-i   ,  i:-i]      = 1.*i/r
        arr2[i:-i      ,   i]      = 1.*i/r
        arr2[i:-i      ,  -1-i]    = 1.*i/r

    return arr2

    
    
    
    
    
    
    
    
    
    
    
    
    
    
