#   modified mexican hat wavelet test.py
#   spectral analysis for RADAR and WRF patterns
#   NO plotting - just saving the results:  LOG-response spectra for each sigma and max-LOG response numerical spectra

import os, shutil
import time, datetime
import pickle
import numpy as np
from scipy import signal, ndimage
import matplotlib.pyplot as plt
from armor import defaultParameters as dp
from armor import pattern
from armor import objects4 as ob
#from armor import misc as ms
dbz = pattern.DBZ
testScriptsFolder = dp.root + 'python/armor/tests/'
testName    = "modifiedMexicanHatTest9"
timeString  = str(int(time.time()))
outputFolder = dp.root + 'labLogs/%d-%d-%d-%s/' % \
                (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday, testName)
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)
shutil.copyfile(testScriptsFolder+testName+".py", outputFolder+ timeString + testName+".py")

kongreywrf  = ob.kongreywrf
kongreywrf.fix()
kongrey     = ob.kongrey
monsoon     = ob.monsoon
monsoon.list= [v for v in monsoon.list if '20120612' in v.dataTime]
march2014   = ob.march2014
march2014wrf11  = ob.march2014wrf11
march2014wrf12  = ob.march2014wrf12
#sigmas  = [1, 2, 4, 5, 8 ,10 ,16, 20, 32, 40, 64, 80, 128, 160, 256, 320,]
sigmas  = [1, 2, 4, 5, 8 ,10 ,16, 20, 32, 40, 64]
dbzstreams = [kongreywrf]
summaryFile = open(outputFolder + timeString + "summary.txt", 'a')


for ds in dbzstreams:
    summaryFile.write("\n===============================================================\n\n\n")
    streamMean  = 0.
    dbzCount    = 0
    for a in ds:
        print "-------------------------------------------------"
        print testName
        print
        print a.name
        a.load()
        a.setThreshold(0)
        a.saveImage(imagePath=outputFolder+a.name+".png")

        L   = []
        a.responseImages = []   #2014-05-02
        #for sigma in [1, 2, 4, 8 ,16, 32, 64, 128, 256, 512]:
        for sigma in sigmas:
            print "sigma:", sigma
            a.load()
            a.setThreshold(0)
            arr0 = a.matrix
            #arr1 = signal.convolve2d(arr0, mask_i, mode='same', boundary='fill')
            #arr1    = ndimage.filters.gaussian_laplace(arr0, sigma=sigma, mode="constant", cval=0.0)        #2014-05-07
            arr1    = ndimage.filters.gaussian_laplace(arr0, sigma=sigma, mode="constant", cval=0.0) * sigma**2 #2014-04-29
            a1 = dbz(matrix=arr1.real, name=a.name + "_" + testName + "_sigma" + str(sigma))
            L.append({  'sigma'     : sigma,
                        'a1'   :  a1,
                        'abssum1': abs(a1.matrix).sum(),
                        'sum1'  : a1.matrix.sum(),
                      }) 
            print "abs sum", abs(a1.matrix.sum())
            #a1.show()
            #a2.show()
            plt.close()
            #a1.histogram(display=False, outputPath=outputFolder+a1.name+"_histogram.png")
            ###############################################################################
            #   computing the spectrum, i.e. sigma for which the LOG has max response
            #   2014-05-02
            a.responseImages.append({'sigma'    : sigma,        
                                     'matrix'   : arr1 * sigma**2,
                                     })

        pickle.dump(a.responseImages, open(outputFolder+a.name+"responseImagesList.pydump",'w'))

        a_LOGspec     = dbz(name= a.name + "Laplacian-of-Gaussian_numerical_spectrum",
                            imagePath=outputFolder+a1.name+"_LOGspec.png",
                            outputPath = outputFolder+a1.name+"_LOGspec.dat",
                            cmap = 'jet',
                            )
        a.responseImages    = np.dstack([v['matrix'] for v in a.responseImages])
        #print 'shape:', a.responseImages.shape    #debug
        a.responseMax       = a.responseImages.max(axis=2)  # the deepest dimension
        a_LOGspec.matrix = np.zeros(a.matrix.shape)
        for count, sigma in enumerate(sigmas):
            a_LOGspec.matrix += sigma * (a.responseMax == a.responseImages[:,:,count])
        a_LOGspec.vmin  = a_LOGspec.matrix.min()
        a_LOGspec.vmax  = a_LOGspec.matrix.max()
        print "saving to:", a_LOGspec.imagePath
        #a_LOGspec.saveImage()
        print a_LOGspec.outputPath
        #a_LOGspec.saveMatrix()
        #a_LOGspec.histogram(display=False, outputPath=outputFolder+a1.name+"_LOGspec_histogram.png")
        pickle.dump(a_LOGspec, open(outputFolder+ a_LOGspec.name + ".pydump","w"))
        #   end computing the sigma for which the LOG has max response
        #   2014-05-02
        ##############################################################################
                        

        #pickle.dump(L, open(outputFolder+ a.name +'_test_results.pydump','w'))     # no need to dump if test is easy
        x = [v['sigma'] for v in L]
        y1 = [v['abssum1'] for v in L]
        plt.close()
        plt.plot(x,y1)
        plt.title(a1.name+ '\n absolute values against sigma')
        plt.savefig(outputFolder+a1.name+"-spectrum-histogram.png")
        plt.close()

        #   now update the mean
        streamMeanUpdate = np.array([v['abssum1'] for v in L])
        dbzCount    += 1
        streamMean  = 1.* ((streamMean*(dbzCount -1)) + streamMeanUpdate ) / dbzCount
        sigmas      =[v['sigma'] for v in L]
        print "Stream Count and Mean so far:", dbzCount, streamMean
        #   now save the mean and the plot
        summaryText = '\n---------------------------------------\n'
        summaryText += str(int(time.time())) + '\n'
        summaryText += "dbzStream Name:" + ds.name + '\n'
        summaryText += "dbzCount:\t" + str(dbzCount) + '\n'
        summaryText +="sigma:\t\t" + str(sigmas) + '\n'
        summaryText += "streamMean:\t" + str(streamMean.tolist()) +'\n'
        print summaryText
        print "saving..."
        #   release the memory

        a.matrix = np.array([0])
        summaryFile.write(summaryText)
        plt.close()
        plt.plot(sigmas, streamMean)
        plt.title(ds.name + '- average laplacian-of-gaussian numerical spectrum for ' +str(dbzCount) + ' DBZ patterns')
        plt.savefig(outputFolder + ds.name + "_average_LoG_spectrum.png")
        plt.close()
summaryFile.close()

