# project incompleted:
# difficult to make it work like this since every specific setting of filter bank requires some tuning (e.g. dropping redundant layers) for the k-means algorithm to work

################################
# armor.texture.analysis1.py
# adapted from roughwork.py - 28-05-2013 
# try more sophisticated method
# make more clusters and group them spatially as in
# [1, p.7]
# [1] Contour and Texture Analysis for Image Segmentation
#     /media/KINGSTON/ARMOR/References/imagesegmentation/
#   https://mail.google.com/mail/u/0/?shva=1#search/thlee%40ntu.edu.tw+feature+extraction/13e5993eeb54c83a

"""
USE

cd /media/KINGSTON/ARMOR/python
python

from armor.texture import analysis1

reload(analysis1)
analysis1.main()

"""


######################
# imports

import os
import pickle
import numpy as np
import time
from armor import pattern
import matplotlib.pyplot as plt
dbz=pattern.DBZ
from scipy.cluster.vq import kmeans2

#######################
# defining the functions

def load(folder='armor/filter/'):
    # or /media/Seagate Expansion Drive/ARMOR/python/armor/filter/gaborFeatures1369996409
    t0 = time.time()
    pydumpList = [fl for fl in os.listdir(folder) if fl[-7:]==".pydump"]
    print '\n'.join(pydumpList)
    if len(pydumpList) ==1:
        d = pickle.load(open(folder+pydumpList[0],'r'))
        data = d['content']
    else:
        # initialise
        d = pickle.load(open(folder+pydumpList[0],'r'))
        data = np.zeros((d.shape[0], d.shape[1], len(pydumpList)))
        data[:,:,0] = d
        print "array size:", (d.shape[0], d.shape[1], len(pydumpList))
        for i in range(1,len(pydumpList)):
            data[:,:,i] = pickle.load(open(folder+pydumpList[i],'r'))
    timespent = time.time()-t0; print "time spent:",timespent
    return data

def main(inputFolder = '/media/Seagate Expansion Drive/ARMOR/python/armor/filter/gaborFeatures1369996409/', outputFolder = '/media/KINGSTON/ARMOR/texture/'):
    t0 = time.time()
    data = load(folder=inputFolder)
    height, width, depth = data.shape
    data = data.reshape(height*width, depth)
    #k=25
    #k=40
    #k=60
    k    = 80           ### <--------- change here ###########################
    clust = kmeans2(data=data[:,1::2], k=k, iter=10, thresh=1e-05,\
                     minit='random', missing='warn')

    os.makedirs(outputFolder+'k_' + str(k))
    texturelayer= []
    for i in range(k):
        print i
        texturelayer.append( (clust[1]==i).reshape(height,width) )
        #plt.imshow(cluster[i])
        #plt.show()
        if texturelayer[i].sum()==0:
            continue
        pic = dbz(  name='texture layer'+str(i),
                  matrix= np.flipud(texturelayer[i]), vmin=-2, vmax=1,
               imagePath=outputFolder+'k_' + str(k) + '/texturelayer' +\
                                                       str(i) + '.png')
        #pic.show()
        pic.saveImage()

    timespent= time.time()-t0;  print "time spent:",timespent
    
if __name__ == '__main__':
    main()
     
