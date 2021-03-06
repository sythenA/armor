# from:  14-06-2013 , roughwork.py, KINGSTON/ARMOR/python
# testing clustering parameters : texture versus location and intensity

"""cd /media/Seagate\ Expansion\ Drive/ARMOR/python/
 python
import time
time.sleep(10800)

 
 """
######################
# imports and setups
featureFolder='armor/texture/1370506584/gaborFeatures/'
k = 144
x_factor, y_factor, intensity_factor = 0.05, 0.05, 10    # adjust this!!!
timestamp=1370506584

###
params = (x_factor, y_factor, intensity_factor)

from armor import pattern
dbz=pattern.DBZ
import pickle
import time
import numpy as np
from armor.texture import analysis
t0=time.time()
a =  pattern.a
reload(analysis)
data = analysis.load(folder=featureFolder)

data.shape
height,width,depth = data.shape

X,Y = np.meshgrid(range(width), range(height))


####################################################

# test starts here
#k = 144
#x_factor, y_factor, intensity_factor = 0.05, 0.05, 10    # adjust this!!!
# params = (x_factor, y_factor, intensity_factor)

X,Y = np.meshgrid(range(width), range(height))


data= data.reshape(height*width, depth)
X   = X.reshape(height*width) * x_factor
Y   = Y.reshape(height*width) * y_factor
Z   = a.matrix.filled().reshape(height*width) * intensity_factor

XYZ = np.vstack([X,Y, Z]).T
data3 = np.hstack([data,XYZ])
data=data.reshape((881,921,36))

del XYZ
del X
del Y
del Z

height3=height
width3=width
depth3 = depth+3
data3=data3.reshape(height3,width3,depth3)

data3.shape
normalisation = 1/(data3.reshape((height3*width3, depth3)).var(axis=0)) **.5

data3 = data3 * normalisation


textureFolder = 'armor/texture/'+ str(timestamp) +'/textureLayers%g_%g_%g_%g/' % ((k,)+params)
textureThickFolder = 'armor/texture/'+ str(timestamp) +'/textureLayers%gthick_%g_%g_%g/' %((k,)+params)
clust, texturelayer = analysis.computeClustering(data=data3, k=k, textureFolder=textureFolder)


# making combined pics
CLUST = dbz(matrix=clust[1].reshape((881,921)))
CLUST.name = "k=%d, x,y,intensity multiplication factors = %g, %g, %g" % ((k,)+params)
#CLUST.show4()
for cmap in ['hsv', 'jet', 'prism','Spectral']:
    CLUST.cmap= cmap
    CLUST.imagePath='/media/Seagate Expansion Drive/ARMOR/python/armor/texture/'+str(timestamp)+'/textureLayers%d_%g_%g_%g/texturelayers_%s.png' % ((k,) + params +(cmap,)) 
    CLUST.imagePath+= cmap + '.png'
    #CLUST.show4()
    CLUST.flipud().saveImage()


# very slow process
segmentation = analysis.computeSegmentation(clust=clust, outputFolder=textureThickFolder)
timeused=time.time()-t0
print 'time used:', 

# pickle it
pickle.dump({'a':a, 'clust':clust,  #'texturelayer':texturelayer, 'data':data, 
                'segmentation':segmentation, 'timeused': timeused}, 
               open(textureFolder+'dataclustsegmentationetc.pydump','w'))

# output to screen

for i in range(k):
    print i
    if (texturelayer[i]*(1-a.matrix.mask)).sum() < 50: continue
    dbz(matrix=texturelayer[i],vmin=-2, vmax=1).show()



