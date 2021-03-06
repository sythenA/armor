#   to carry out some studies for raw charts published by CWB

import numpy as np
import matplotlib.pyplot as plt
imshow = plt.imshow
from scipy import ndimage
from scipy import interpolate
import matplotlib as mpl
from scipy import cluster
import time
import os

outputFolder  ='/media/TOSHIBA EXT/CWB/temp/'               # <-- edit here
inputFolderBig  = '/media/TOSHIBA EXT/CWB/charts/'
inputFolders    = os.listdir(inputFolderBig)
inputFolders.sort()
inputFolders    = [inputFolderBig+v+'/' for v in inputFolders if v > "2013-10" and v < "2013-12"]


timeString      = str(int(time.time()))
imageAverage    = np.zeros((600,600,3))
imageCount      = 0
for inputFolder in inputFolders:
    print '\n==================================================='
    print inputFolder
    L   = os.listdir(inputFolder)
    L.sort()
    for imageName in L:
        imageCount +=1
        #imageName = '2014-05-20_1700.2MOS0.jpg'
        print imageName
        l   = plt.imread(inputFolder+imageName)
        #plt.imshow(l, origin='lower')
        #plt.show()
        imageAverage    = 1.*((imageCount-1)*imageAverage + l)/imageCount
        if imageCount % 200 ==0:
            imshow(imageAverage.astype(np.uint8), origin='lower')
            plt.savefig(outputFolder+ timeString + 'averageImage.jpg')
            plt.close()

