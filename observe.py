"""
== USE ==

from armor import pattern
from armor.observe import window as obsw

a = pattern.a
b = pattern.b
lowerLeft = (250, 200)
windowSize = (100, 100)

x = obsw(a, b, 250, 200, 100, 100, display=True, toFile='testing/test114/log.1.txt)

== RESULTS ==
"""

######################################
# imports
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from armor import pattern
from armor.shiiba import regression2 as regression
from armor.shiiba import regression3 as reg
from armor.shiiba import regressionCFLfree as cflfree
from testing.test112 import test112 as test
from armor.advection import semiLagrangian
sl = semiLagrangian
lsq = np.linalg.lstsq
import os
from imp import reload
import time
import pickle
time0= time.time()

def tic():
    global timeStart
    timeStart = time.time()

def toc():
    print "time spent:", time.time()-timeStart

dbz=pattern.DBZ

def window(a, b, bottom, left, height=100, width=100, searchWindowHeight=9,\
          searchWindowWidth=9, display=True, toFolder=''):
    # 1. create folder a.outputFolder/observation/time
    # 2. create windows aa bb and write image for aa, bb, bb-aa
    # 3. regress and write result
    # 4. get prediction and write image
    if toFolder=="":
        #toFolder = a.outputFolder + "bottom%d_left%d_height_%d_width_%d_searchHeight%d_searchWidth_%d" % (bottom,left,height,width, searchWindowHeight, searchWindowWidth)
        toFolder = a.outputFolder + str(int(time.time()) %  100000)
    if toFolder!=None and toFolder!=False:
        try:
            os.makedirs(toFolder)
            print a.outputFolder, "folder created!"
        except OSError:
            print a.outputFolder, "exists!"
            raise OSError

    # initialise the output string
    outputFolder =  toFolder        #alias
    output  = time.asctime()
    output += "\narmor.observe.window: \na = " + a.name + ", b = " + b.name
    output += "\nwindow: bottom=%d, left=%d, height=%d, width=%d" % (bottom, left, height, width)

    # create the windows and save
    aa = a.getWindow(bottom, left, width, height)
    bb = b.getWindow(bottom, left, width, height)
    diff = (bb-aa)
    aa.imagePath = outputFolder + 'a.window%d.png' % height
    bb.imagePath = outputFolder + 'b.window%d.png' % height
    aa.saveImage()
    bb.saveImage()
    
    # compute basic properties
    output += "mean of a.window = %f; mean of b.window = %f" %(aa.matrix.mean(),bb.matrix.mean())
    output += "Number of data points: a.window: %d, b.window %d" %\
                ( (1-aa.matrix.mask).sum(), (1-bb.matrix.mask).sum() )
    output += "common region: %d" % (1- (aa.matrix.mask+bb.matrix.mask)).sum()                
    
    corr = aa.corr(bb)[0,1]
    output += "\nCorrelation: %f;  Correlation-squared: %f" % (corr, corr**2)

    # regress
    regressionResults = cflfree.regressLocal(a=aa, b=b, gridSize=5,bottom=bottom,left=left,
                                            height=height,width=width,\
                                              searchWindowHeight=searchWindowHeight,\
                                              searchWindowWidth=searchWindowWidth,\
                                              display=False) 
    mn          = [v[0] for v in regressionResults]
    C           = [v[1] for v in regressionResults]
    Rsquared    = [v[2] for v in regressionResults]
    
    output += "\nTop results from CFL-relaxed regression (search window height: %d, width: %d)" %\
                                              (searchWindowHeight, searchWindowWidth)
    output += "\n(m, n),\tRsquared,\tc1,...,c9"
    for v in regressionResults[:12]:
        output += "\n(%d,%d),\t%f, %f %f %f %f %f %f %f %f %f" % (v[0][0],v[0][1],v[2],\
                 v[1][0], v[1][1],v[1][2],v[1][3],v[1][4],v[1][5],v[1][6],v[1][7],\
                 v[1][8])
    
    #get prediction
    (m,n), C, Rsquared = regressionResults[0]
    aa1 = getPrediction(C, aa)
    bb1 = b.getWindow(bottom=bottom+m, left=left+n, height=height, width=width)
    diff = bb1-aa1
    aa1.imagePath = outputFolder + "aa1.window.shiiba.prediction.png"
    bb1.imagePath = outputFolder + "bb1.window.shiiba.data.png"
    diff.imagePath = outputFolder + "bb1-aa1.window.shiiba.data.png"
    aa1.saveImage()
    bb1.saveImage()
    diff.saveImage()
    
    # compute correlation
    corr = aa1.corr(bb1)[0,1]
    output += "\nCorrelation between prediction and data in the window: %f;  Correlation-squared: %f" % (corr, corr**2)

    # output    
    if display:
        print output 
    open(toFolder+'.log.txt', 'w').write(output)
    return output
    

def main():
    a=pattern.a
    b=pattern.b
    a.outputFolder = "testing/test114/observations0200/"
    return window(a=a,b=b, bottom=250, left=250, height=100, width=100,\
         searchWindowHeight=7, searchWindowWidth=17, display=True, toFolder='')
         
if __name__ == '__main__':
    main()
