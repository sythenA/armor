#  regressionCFLfree.py
#  taken from test112.variantD (local noncfl) and variantC (global noncfl as a special case
#  of local noncfl)
"""
TEST:

cd /media/KINGSTON/ARMOR/2013/python/
python
from armor.shiiba import regressionCFLfree as cfl
"""

###################################################################
# imports
import numpy as np
import numpy.ma as ma
from .. import pattern
from ..shiiba import regression2 as regression
from ..shiiba import regression3 as reg
from ..shiiba import upWind    # 21 march 2013
from imp import reload
import time
#from copy import deepcopy

###################################################################
# restart here

dbz = pattern.DBZ

###################################################################
# setups

a= pattern.a        # for demo
b= pattern.b

###################################################################
# defining the functions

time0= time.time()

def tic():
    print "\n************************\ntimer started"
    global timeStart
    timeStart = time.time()
    return timeStart

def toc():
    timeSpent=time.time()-timeStart
    print "\n*************************\ntime spent:", timeSpent
    return timeSpent


###################################################################
# defining the functions

def regressLocal(a, b, bottom=550, left=600, height=50, width=50,
             gridSize=5, searchWindowHeight=9, searchWindowWidth=9, display=False,
              useRecursion=False, preScale=1,
              centre=(0,0),
              ):
    """
    3.  nonCFL local regression
    """
    # local case (without taking care of the edge effects)
    tic()
    results=[]      # [((i,j), C, Rsquared)]
    for i in range(centre[0]+int(-searchWindowHeight/2)+1, centre[0]+int(searchWindowHeight/2)+1):
        for j in range(centre[1]+int(-searchWindowWidth/2)+1, centre[1]+int(searchWindowWidth/2)+1):
            print "\n**********************************\n"
            print "(i, j) =", i, j
            aa = a.getWindow(bottom=bottom, left=left, height=height, width=width)
            bb = b.getWindow(bottom=bottom+i, left=left+j, height=height, width=width)
            if useRecursion:
                """use old codes
                """
                C, Rsquared = reg.regress(aa,bb)
            else:
                """use new codes
                """
                x = upWind.regress(aa,bb,preScale=preScale)
                C=x['C']
                Rsquared=x['Rsquared']
            #print C,Rsquared
            if display:
                vect        = regression.convert(C, aa)
                vect.name   = 'shiiba vector field for ' + aa.name + ' and ' + bb.name
                vect.title  = vect.name
                vect.gridSize= gridSize
                vect.show()
            results.append([(i,j), C, Rsquared])
    results.sort(key=lambda v: v[2], reverse=True)        # sort according to Rsquared
    toc()
    return results

def regressGlobal(a,b, gridSize=20, searchWindowHeight=9, searchWindowWidth=9,\
                 display=False, useRecursion=False, 
                 centre=(0,0),                          # 2013-10-17 
                 ):
    """
    3.  nonCFL global regression, a special case of the above
    """
    '''
    Extreme Case:  search window = (3, 21) - okay.
    time spent: 100.260792971
    
    [[(1, 5), array([ -2.63135953e-03,   1.59539319e-03,   4.19678262e-01,
            -1.27937030e-03,   5.10425263e-04,   4.83055658e-01,
            -2.28178341e-03,  -4.03608691e-04,   1.44962411e+00]), 0.81778155615575665], 
    [(1, 6), array([ -2.19781287e-03,   1.43823238e-03,   3.48443842e-01,
            -8.72068167e-04,   6.92383017e-04,  -8.63004509e-02,
            -1.95438561e-03,  -7.79039368e-04,   1.46662461e+00]), 0.81533674267187606], 
    [(0, 6), array([ -2.16242655e-03,   1.03009249e-03,   8.83211464e-01,
            -1.42946321e-03,   8.53812947e-04,   5.02341471e-02,
            -5.91245193e-04,  -1.26550752e-03,   1.05446222e+00]), 0.81271652217175949], 
    [(1, 4), array([ -2.56008429e-03,   1.51305751e-03,   3.72421282e-01,
            -1.00436126e-03,   5.02240237e-05,   8.02817269e-01,
            -2.54769814e-03,   1.22208557e-05,   1.35380990e+00]), 0.81011722909235506], 
    '''
    height, width = a.matrix.shape
    # global case - need to take care of the edge effects
    # this is constructed as a special case of the above (variant D),
    # in which A is given a window of size 
    # ~ (height-search window height)x(width-search window width)
    # if searchWindowWidth=1, no trimming needed
    # if searchWindowWidth=3, trim one from left and one right
    # if searchWindowWidth=2, trim one from right
    # if searchWindowWidth=4, trim one from left, two from right
    #mainWindowHeight    = height - searchWindowHeight +1 
    #mainWindowWidth     = width  - searchWindowWidth  +1
    mainWindowHeight    = height - searchWindowHeight +1 - abs(centre[0]) # 2013-10-17 
    mainWindowWidth     = width  - searchWindowWidth  +1 - abs(centre[1])
    mainWindowBottom    = (searchWindowHeight -1)//2   # 4->1, 3-> 1, 1->0, 2->0, 5->2
    mainWindowLeft      = (searchWindowWidth  -1)//2  #+ centre[1]   
    #mainWindowBottom    = (searchWindowHeight -1)//2 #+ centre[0]   # 2013-10-17
    tic()
    results = regressLocal(a=a, b=b, bottom=mainWindowBottom, left=mainWindowLeft, 
                    height=mainWindowHeight, width=mainWindowWidth,
                    gridSize=gridSize, searchWindowHeight=searchWindowHeight,
                    searchWindowWidth=searchWindowWidth, display=display, 
                    useRecursion=useRecursion,
                    centre=centre,
                    )
    toc()
    return results
##############################################################

def regressLocalAll(a, b, windowSize=100, iRange=range(250, 600, 100),\
                    jRange=range(100, 800, 100), searchWindowHeight=7,\
                    searchWindowWidth=15, useRecursion=False, plotting=True ):
    mn      = {}
    C       = {}
    Rsquared= {}
    CR2     = {}
    timeStart = time.time()

    for i in iRange:         # cutting out the edge
        for j in jRange:     # just look where there is data
            #############
            # 1. get the dbz window
            # 2. regress
            # 3. record the C and Rsquared
            # 1. get the dbz window
            print "(y, x) of the lower left corner of the regression box=", (i,j)
            try:
                results = regressLocal(a=a, b=b, bottom=i, left=j, height=100, width=100, \
                     gridSize=5, searchWindowHeight=searchWindowHeight,\
                      searchWindowWidth=searchWindowWidth, display=False,\
                      useRecursion=useRecursion)
                mn[(i,j)], C[(i,j)], Rsquared[(i,j)] = results[0]
                CR2[(i,j)] = (results[0][0], results[0][2])
            except:
                print "\n..............\n("+str(i) + ", " + str(j) + "): Error!\n..........\n"
                mn[(i,j)] = "ERROR"
                C[(i,j)] = "ERROR"
                Rsquared[(i,j)] = "ERROR"
                CR2[(i,j)] = "ERROR"
    timeSpent = time.time()-timeStart

    #######
    # making the plot
    #...
    if plotting:
        m = np.zeros((881,921))
        for v in Rsquared.keys():
            if Rsquared[v] != "ERROR":
                m[v[0]:v[0]+windowSize, v[1]:v[1]+windowSize] = Rsquared[v]

        M = dbz(name='R-squared for local non-CFL regression,\nfor dbz20120612.0200-0210',\
                matrix=m, vmax=1, vmin=0, cmap='jet')
        #M.matrix = np.flipud(M.matrix)
        M.show2()

    return {'mn': mn, 'C':C, 'Rsquared':Rsquared, 'CR2':CR2, 'timeSpent':timeSpent}

#####################################


def main():
    results1 = regressLocal(a,b)
    results2 = regressGlobal(a,b)
    return results1, results2
    
if __name__ == "__main__":
    main()
