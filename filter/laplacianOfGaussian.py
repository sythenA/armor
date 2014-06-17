##############
#   code copied from armor.tests.roughwork  (volume 2013-10-16)

##########################################################
#   imports and setups
import time
from scipy import ndimage
from armor import pattern
from armor.objects2 import soulik, monsoon, kongrey, kongreymodelsall
LoG = ndimage.filters.gaussian_laplace
soulikOutputFolder = '/home/k/ARMOR/data/SOULIK/charts' + str(int(time.time())) +'/'  # don't overwrite past stuff if accessed by accident
sigma = 20

def initialise(ds=soulik, outputFolder=soulikOutputFolder, key1='', drawCoast=False):
    ds.fix(key1) #loading the images with the key '0828' and setting threshold=0
    ds.setOutputFolder(outputFolder)
    ds.setImageFolder(outputFolder)
    ds[0].show()
    ds.saveImages(flipud=False,drawCoast=drawCoast)

#############

def analyse(ds=soulik, outputFolder=soulikOutputFolder, drawCoast=False, sigma=sigma):
    ds.setImageFolder(outputFolder)
    for k in ds:
        #   laplaceofgaussian filter
        #   save image to a new folder
        #   test for typhoon eye
        #k.backupMatrix()
        k.matrix = LoG(k.matrix, sigma)
        #mx = k.matrix.max()
        #mn = k.matrix.min()
        #mx  =   0.10
        #mn  =  -0.05
        #k.vmax = mx
        #k.vmin = mn - (mx-mn) *0.2
        print k.name,
        #k.show()
    mx = max([k.matrix.max() for k in ds])
    mn = min([k.matrix.min() for k in ds])
    #mx = 0.1
    #mn = -0.1
    ds.setVmin(mn)
    ds.setVmax(mx)
    ds.setImageFolder(outputFolder)
    print '\n\n.........\nsaving images to', outputFolder
    ds.saveImages(flipud=False, drawCoast=drawCoast)
    return ds


