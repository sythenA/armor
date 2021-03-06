###################################
#      WORK IN PROGRESS
#      ADAPTED FROM OLD clustering.py BASED ON THE CLASS weatherPattern.pattern2d
#      NOTE:  SINCE THIS CODE WAS INITIATED IN 2012, THE (i, j) are reversed
#             AS FROM OTHER MODULES OF THE armor PACKAGE:  HERE (i,j)=(x,y)
#             AND WE USE THE FIRST AND SECOND COMPONENTS TO FOR x, y RESPECTIVELY
# clustering.py
# reference:  http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.vq.kmeans2.html#scipy.cluster.vq.kmeans2

# a test on the k-means algorithm on scipy for weather systems segmentation
# 

# uses the Munkres implementation for the Hungarian algorithm
#   references: for Munkres http://software.clapper.org/munkres/ 
#                           
#               for the Hungarian algorithm
#                           http://en.wikipedia.org/wiki/Hungarian_algorithm
#####################################
# imports
#

from pylab import plot,show
#from numpy import vstack,array
#from numpy.random import rand
#from scipy.cluster.vq import kmeans,vq

import numpy as np
import numpy.ma as ma

import scipy.cluster
from scipy.cluster.vq import vq, kmeans2  # i don't think i am going to use vq; 
                                          # just keep it there anyway
from .. import pattern
dbz = pattern.DBZ

import os
import copy
import time

#####################################
# parameters
#  

width  = 921
height = 881

timeString = str(int(time.time()))

def getKmeans(a, k , threshold = 1, iter =40,  thresh=1e-05, 
                    minit='random', missing='warn'  ):
        """input : a, k threshold
        output : atk
        """
        if minit=="matrix":
            seeds, k    = k, len(k)
        a.k = k                                       # initialise (could move it to __init__ but not bothered for the moment)
        height, width = a.matrix.shape
        pixels = (a.matrix > threshold)
        print 'width, height:' , width, height            #debug
        print 'sum of relevant pixels:', sum(sum(pixels))  #debug
        dataPoints = [ [ (i,j)  for i in range(width) if pixels[j,i] ]  
                                for j in range(height)]
        dataPoints = sum(dataPoints,[])
        dataPoints = np.array(dataPoints)
        print dataPoints[:20]
        if minit =="matrix":
            a.centroids = kmeans2(data = dataPoints, k=seeds, iter=iter,
                                 thresh=thresh, minit=minit, missing=missing)
        else:
            a.centroids = kmeans2(data = dataPoints, k=k, iter=iter, thresh=thresh, 
                                       minit=minit, missing=missing)
        a.data      = dataPoints
        
        resultPattern            = ma.zeros((height, width))
        resultPattern.mask       = True
        resultPattern.fill_value =-999
        for i in range(len(dataPoints)):
            resultPattern[ dataPoints[i][1], dataPoints[i][0]] = a.centroids[1][i]
        resultPattern = dbz(name='Clustering for %s with %d clusters' %(a.name, k+1),\
                            matrix=resultPattern, vmin=0, vmax=k)

        atk = {'centroids':a.centroids, 'data':a.data, 'pattern': resultPattern}
        return atk

def fixColouringAndCompare(atk, btk):
    """
    15 April 2013
    input: atk, btk are clustering results
    output: btk['pattern'] and btk['centroids'][1] fixed
            returning the distanceSquaredMatrix and the indices
    """
    k = len(atk['centroids'][0])
    #k = a.k
    aClusters =[-999] * k       #initialising a length-k list for convenience
    bClusters =[-999] * k
    for i in range(k):                                
        # x-coord, y-coord, weight of the i-th cluster in a
        aClusters[i] = { 'x'     : atk['centroids'][0][i][0],    
                         'y'     : atk['centroids'][0][i][1],
                         'weight': len([v for v in atk['centroids'][1] if v ==i]),
                                   }
        # doing the same for b
        bClusters[i] = { 'x'     : btk['centroids'][0][i][0],   
                         'y'     : btk['centroids'][0][i][1],
                         'weight': len([v for v in btk['centroids'][1] if v ==i]),
                                   }
    distanceSquaredMatrix = np.ones((k,k))*(-999.)
    for i in range(k):
        for j in range(k):
            dist2 = ((aClusters[i]['x'] - bClusters[j]['x'])**2 \
                   +(aClusters[i]['y'] - bClusters[j]['y'])**2 ) 
            #print i,j, dist2  #debug
            distanceSquaredMatrix[i,j]  = dist2
    from munkres import Munkres
    m = Munkres()
    indices = m.compute(distanceSquaredMatrix.copy())   # munkres would alter the entries
    #indicies2=dict([(v[1], v[0]) for v in indices])
    indices2 = m.compute(distanceSquaredMatrix.copy().T)# munkres would alter the entries
    indices2Dict = dict(indices2)
    #print indices2      #debug
    #print indices2Dict
    
    bData=btk['data']
    bCentroids=btk['centroids']
    for i in range(len(bCentroids[1])):
        newColour  = indices2Dict[bCentroids[1][i]]
        btk['centroids'][1][i]  = newColour
        btk['pattern'].matrix[bData[i][1], bData[i][0]] = newColour  
    
    abCompare= {"distanceSquared"   : distanceSquaredMatrix,
                "indices"           : indices,
                "aClusters"         : aClusters,
                "bClusters"         : bClusters,
               }
    return abCompare

def diff1(a,b, k=10, threshold=35, minit_a = "random", minit_b ="matrix", **kwargs) :
    """15 april 201
    new diff, version 1 : kmeans for b is unseeded
    """
    atk = getKmeans(a, k=k,threshold=threshold, minit=minit_a, **kwargs)
    if minit_b =="matrix":
        seeds = atk['centroids'][0]
        btk = getKmeans(b, k=seeds,threshold=threshold, minit=minit_b, **kwargs)    
    else:
        btk = getKmeans(b, k=k,threshold=threshold, minit=minit_b, **kwargs)    
    atk['pattern'].copy().show2()
    #btk['pattern'].copy().show2()
    abCompare = fixColouringAndCompare(atk, btk)
    #aClusters = abCompare['aClusters']
    #bClusters = abCompare['bClusters']
    aCentroids = atk['centroids'][0]
    bCentroids = btk['centroids'][0]
    indices         = abCompare['indices']
    indicesDict = dict(indices)
    displacements = [-999]*k
    for i in range(k):
        # we used x, y coords before
        displacements[i] = bCentroids[indicesDict[i]] - aCentroids[i]
    print displacements
    distanceSquared = abCompare['distanceSquared']
    weights     ={}
    dotProduct  ={}
    normalisedDotProduct ={}
    covar       = {}
    corr        = {}
    
    print "(x, y), weight:"
    for i,j in indices:
        acluster_i = (atk['pattern'].matrix==i)
        bcluster_i = (btk['pattern'].matrix==i)
        weights[i]     =  acluster_i.sum() * bcluster_i.sum()
        acluster_i = np.roll(acluster_i, int(round(displacements[i][1])), axis=0)  # we used x,y coords before
        acluster_i      = np.roll(acluster_i, int(round(displacements[i][0])), axis=1)
        dotProduct[i]   =  (acluster_i   *  bcluster_i).sum()
        normalisedDotProduct[i] = 1.* dotProduct[i] / ( acluster_i.sum()**.5 *\
                                    bcluster_i.sum()**.5    )  
        covar[i]        = (acluster_i * bcluster_i).mean() - \
                          acluster_i.mean() * bcluster_i.mean()
        corr[i]         = covar[i] / (acluster_i.var() * bcluster_i.var())**.5
        print  i,\
               aCentroids[i][0], aCentroids[i][1], '->\t',\
               bCentroids[j][0], bCentroids[j][1], '\t', \
               weights[i]
    print "\n.............\ni, weights[i], dotProduct[i], normalisedDotProduct[i]:"
    for i in range(k):
        print i, weights[i], dotProduct[i], normalisedDotProduct[i]

    btk['pattern'].copy().show2()

    distances = [(v, indicesDict[v], distanceSquared[v, indicesDict[v]]) \
                 for v in range(len(indices))]
    abCompare['distances']  = distances
    abCompare['atk']        = atk
    abCompare['btk']        = btk
    abCompare['weights']    = weights
    abCompare['dotProduct'] = dotProduct
    abCompare['corr']       = corr
    return abCompare

def getCovariance(atk, btk):
    """
    input: atk, btk are clustering results 
            e.g. atk=getKmeans(a, threshold=30, k = 10)
    output: covariances / correlations for the best matching
    """
    abCompare = fixColouringAndCompare(atk, btk)
    pass


####################


def makeImageWithCentroids(a,k = 0, matrix =[], threshold = -98764, colourbar =''):           # threshold = lower bound for the pixel intensity we look at
        """14 sept 2012, 
        codes copied from main()
        """
        if matrix ==[]:
            matrix =  copy.deepcopy(a.matrix)
        width =  len(matrix[0])
        height = len(matrix)
        zMax   = matrix.max()
        if threshold == -98764:
            threshold = zMax - 30     # setting a threshold intelligently
        if k==0 :
           try:              
               k = a.k      # use a.k if k not given
               print a.name,'.k', a.k
           except AttributeError:
               print "you need to supply k = no. of clustering centre as an argument!"
               raise AttributeError
        else:
               a.k = k       # else set a.k = k
        print "\n-------------------\n k, threshold = ", k, threshold
        #x=raw_input('press enter:')       #debug

        # can delete (one of) these attributes first if you don't like them and want to get a new set of clusters
        # testing if a.centroids/data are defined;  if not, get them.
        try:
            centroids, data = a.centroids, a.data
        except AttributeError: 
            x = a.getKmeans(k=k, threshold=threshold)
            centroids, data = x['centroids'], x['data']
            a.centroids, a.data = centroids, data  #save it
        #centroids, data = a.getKmeans(k= k, threshold=threshold)      # <---- this line is replace by the four lines above
        print type(centroids)
        print centroids
        centroidWeight = {}   #initialising
        for i in range(k):
            centroidWeight[i] = int( np.log2(1+len([v for v in centroids[1] if v ==i])))
        for index in range(k):
            centroid = centroids[0][index]
            i, j = [int(v) for v in centroid]
            # change the intensity (and thus colour) and replot
            # matrix[j,i] = 80
            print '(', j, ',', i, ')'
            for ii in range(i-0-2*centroidWeight[index],i+1+ 2*centroidWeight[index]): # fixing the size of the marker ...
                                                                                  #  according to the log centroid weight
                try:
                    matrix[j,ii] = 50              
                except IndexError:     #ignore if out of range
                    continue                
            for jj in range(j-0-2*centroidWeight[index],j+1+ 2*centroidWeight[index]):
                try:
                    matrix[jj,i] = 50
                except IndexError:     #ignore if out of range
                    continue                

        ##############
        #  3. making the image

        img = a.makeImage(matrix=matrix, colourbar=colourbar)
        # a.print2screen() #test
        return img

    ##################################################
    ##     makeImageWithClusters
    ##    18-9-2012
    ##   
def makeImageWithClusters(a,k = 0, matrix =[], threshold = -98764, colourbar ='', 
                              indices=[], centroids=[], data=[]):        # threshold = lower bound for the pixel intensity we look at
        """18 sept 2012, 
        adapted from makeImageWithCentroids()
                 and diff()
        to draw clusters with different colours
        """
        if matrix ==[]:
            matrix =  copy.deepcopy(a.matrix)
        try:
            img = a.image.copy()
        except AttributeError: 
            img = a.makeImage(matrix=a.matrix, colourbar=a.colourbar)
        width =  len(matrix[0])
        height = len(matrix)
        zMax   = matrix.max()
        if threshold == -98764:
            threshold = zMax - 30     # setting a threshold intelligently
        if k==0 :
           try:              
               k = a.k      # use a.k if k not given
               print a.k
           except AttributeError:
               print "you need to supply k = no. of clustering centre as an argument!"
               raise AttributeError
        else:
               a.k = k       # else set a.k = k
        print "\n-------------------\n k, threshold = ", k, threshold
        # testing if a.centroids/data are defined;  if not, get them.
        # can delete (one of) these attributes first if you don't like them and want to get a new set of clusters

        if centroids ==[] or data ==[]:
            try:
                centroids, data = a.centroids, a.data
            except AttributeError: 
                #centroids, data = a.getKmeans(k= k, threshold=threshold) #old
                #a.centroids, a.data = centroids, data  
                x = a.getKmeans(k=k, threshold=threshold)                   #new
                a.centroids, a.data = x['centroids'], x['data']
        print type(centroids)
        print centroids
        centroidWeight = {}   #initialising
        if indices ==[]:
            indices =range(k)
        for i in indices:
            centroidWeight[i] = int( np.log2(1+len([v for v in centroids[1] if v ==i])))
        count = -1            # initialising
        for index in indices:
            count +=1
            try: 
                print index,(count*220 *5//k % 255, (count*255*2 //k +100) % 255, (count*255*3+200) //k % 255), centroids[0][index]
            except IndexError:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Destroyed/created !!!!!!!!!!!!!!!!!!!! :\n", index, '\n---------------------------------------'
                x = raw_input("press enter to continue:")
                continue
            dataCluster = [data[v] for v in range(len(data)) if centroids[1][v] == index ]
            centroid = centroids[0][index]       # keeping this line just in case
            for point in dataCluster:
                img.putpixel(point, (count*220 *5//k % 255, (count*255*2 //k +100) % 255, (count*255*3+200) //k % 255))
                #img.putpixel(point, (count*255//k, 0, 255 - count*255//k)  )      #alternative colouring scheme, from high to low
        return img
    ##   end - makeImageWithClusters
    #######################################################################################

def diff_old(a,b,k=0, newSeeding = True, threshold = -98764, outputFolder ='') :
            ######  REWRITE IN PROGRESS  - 8 APRIL 2013 ##########
            ######  NEED TO CONVERT THE IMAGING PROCESS TO A PYPLOT-BASED ONE ######
            ######  REF: http://matplotlib.org/users/artists.html#customizing-your-objects ###
            ######  OR PERHAPS I SHOULD FOCUS ON GETTING PYTHON IMAGE LIBRARY(PIL) RIGHT??###
            """ to measure the displacement (velocity field) of a system (somewhat stochastically)
            input:  two pattern2dWithClustering objects (or, in the end, two pattern2d objects)
            output:  cluster displacement fields based on k-means 
            NOT over-riding the weatherPattern.pattern2d.__sub__ method
            """
            '''
            USE:
            a=pattern.a
            b=pattern.b
            import armor.kmeans.clustering as clust
            x= clust.diff(a,b,k=20, threshold=35)
            '''
            a = a
            b = b
            if k == 0:
               try:              
                   k == a.k      # use a.k if k not given
               except AttributeError:
                   print "need supply k = no. of clustering centre as an argument!\n --> setting default = 5"
                   k = 5
                   a.k = 5
            else:
               a.k = k       # else set a.k = k

            print "\n----------------------\n**** a, b, k =", a.name, b.name, k
            if newSeeding:
                # kmeans for the first pattern
                #aCentroids, aData = a.getKmeans(k=k, threshold = threshold)           
                x = a.getKmeans(k=k, threshold=threshold)
                aCentroids, aData = x['centroids'], x['data']
                # kmeans for the second pattern
                #bCentroids, bData = b.getKmeans(k=k, threshold = threshold ) #old
                x = b.getKmeans(k=k, threshold=threshold)                       #new
                bCentroids, bData = x['centroids'], x['data']               
                a.centroids, a.data = aCentroids, aData 
                b.centroids, b.data = bCentroids, bData 
            else:
                aCentroids, aData = a.centroids, a.data 
                bCentroids, bData = b.centroids, b.data 
            #############################
            # first setting aCluster, bCluster 
            #       = lists of dicts 
            #       =[{'x': x-coord, 'y': y-coord, 'weight': cluster size (or weight)}]
            aClusters =[0] * k       #initialising a length-k list for convenience
            bClusters =[0] * k
            for i in range(k):                                        # i = 0,1,..., 5 by default
                aClusters[i] = { 'x'     : aCentroids[0][i][0],    # x-coord, y-coord, weight of the i-th cluster in a
                                 'y'     : aCentroids[0][i][1],
                                 'weight': len([v for v in aCentroids[1] if v ==i]),
                               }
                bClusters[i] = { 'x'     : bCentroids[0][i][0],    # doing the same for b
                                 'y'     : bCentroids[0][i][1],
                                 'weight': len([v for v in bCentroids[1] if v ==i]),
                               }
                #print 'aClusters, bClusters', aClusters, bClusters     #debug
            #############################
            # now do the matching
            #     first compute the distance-squared matrix - multiplied by weights
            #  ---> a[0],...a[k-1]
            #  |
            #  |
            #  v
            #  b 
            distanceSquaredMatrix = np.zeros((k,k))
            for i in range(k):
                for j in range(k):
                    distanceSquaredMatrix[i,j] = ((aClusters[i]['x'] - bClusters[j]['x'])**2   \
                                                 +(aClusters[i]['y'] - bClusters[j]['y'])**2 ) \
                                                 # * aClusters[i]['weight'] * bClusters[j]['weight']
                                                 #  the above line is commented out for testing and debugging
            #print "distanceSquaredMatrix:", np.array([int(x) for x in sum(distanceSquaredMatrix.tolist(),[]) ]).reshape(k,k)  #debug
            #     now use the Munkres implementation for the Hungarian algorithm
            #     reference: for Munkres http://software.clapper.org/munkres/ 
            from munkres import Munkres, print_matrix
            m = Munkres()
            indices = m.compute(distanceSquaredMatrix)
            # the following line (print_matrix ...) is commented out:  error message
            """
                Lowest cost match:
                Traceback (most recent call last):
                  File "<stdin>", line 1, in <module>
                  File "clustering.py", line 166, in diff
                    print_matrix(distanceSquaredMatrix, msg='Lowest cost match:')
                  File "/usr/local/lib/python2.7/dist-packages/munkres.py", line 730, in print_matrix
                    width = max(width, int(math.log10(val)) + 1)
                ValueError: math domain error
            """
            #print_matrix(distanceSquaredMatrix, msg='Lowest cost match:')   
             
            for i, j in indices:
                print aClusters[i]['x'], aClusters[i]['y'], '->\t', bClusters[i]['x'], bClusters[i]['y'], \
                      '\t', aClusters[i]['weight'] * bClusters[j]['weight']
            #################################
            # make some nice picture outputs
            img1 = a.img.copy()
            img2 = b.img.copy()

            count = 0
            for i,j in indices:
                count +=1
                Xa = int(aClusters[i]['x'])
                Ya = int(aClusters[i]['y'])
                Xb = int(bClusters[j]['x'])
                Yb = int(bClusters[j]['y'])
                for ii in range(Xa-10, Xa+11):
                    try:
                        img1.putpixel((ii,Ya), (count *220*5 //k % 255, (count*255*2 //k + 100) % 255, (count*255*3+200) //k % 255))
                    except IndexError:
                        continue
                for jj in range(Ya-10, Ya+11):
                    try:
                        img1.putpixel((Xa,jj), (count*220 *5//k % 255, (count*255*2 //k +100) % 255, (count*255*3+200) //k % 255))
                    except IndexError:
                        continue

                for ii in range(Xb-10, Xb+11):
                    try:
                        img2.putpixel((ii,Yb), (count *220 *5//k % 255, (count*255 *2 //k +100) % 255, (count*255 *3+200) //k % 255))
                    except IndexError:
                        continue
                for jj in range(Yb-10, Yb+11):
                    try:
                        img2.putpixel((Xb,jj), (count*220 *5//k % 255, (count*255*2 //k +100) % 255, (count*255 *3+200) //k % 255))
                    except IndexError:
                        continue
            img1.show()
            img2.show()
            indices.sort( key = lambda w : (-aClusters[w[0]]['weight']) )

            print [(w, aClusters[w[0]]['weight']) for w in indices]
            img3 = a.makeImageWithClusters(k=k, indices = [v[0] for v in indices], threshold = threshold)
            img4 = b.makeImageWithClusters(k=k, indices = [v[1] for v in indices], threshold = threshold)
            a.print2screen(img3)
            b.print2screen(img4) 

            logScore =  np.log(np.array(distanceSquaredMatrix).sum())
            timeString = str(int(time.time()))

            if outputFolder != '':
                #a.print2file(path =outputFolder +timeString +'centroids-a-score-' +str(round(logScore,4))+'.png', img = img1)
                a.print2file(path =outputFolder + str(round(logScore,4))+ 'centroids-a-score-' +'.png', img = img1)
                a.print2file(path =outputFolder + str(round(logScore,4))+ 'centroids-b-score-' +'.png', img = img2)
                a.print2file(path =outputFolder + str(round(logScore,4))+ 'clusters-a-score-'  +'.png', img = img3)
                b.print2file(path =outputFolder + str(round(logScore,4))+ 'clusters-b-score-'  +'.png', img = img4)
            #################################
            # return: [ ((ax1,ay1),(bx1,by1)), ((ax2,ay2),(bx2,by2)),... ] , log (total cost)

            print "\n...............\nScore (log sum distance) = " , logScore
            return indices, logScore


    #######################################################################################
    ##
    ##
def diffWithCreationAndDestruction(a,b,k=0, newSeeding = True, threshold = -98764, outputFolder ='', seedBwithA= True) :
            ####
            ####  HARD HAT AREA - NOT YET MODIFIED FROM OLD weatherPattern package(2012)
            ####        today: 17 April 2013
            ####
            """ modified from the function a.diff():
            with creation/destruction of clusters added

            input:  two pattern2dWithClustering objects (or, in the end, two pattern2d objects)
            output:  cluster displacement fields based on k-means 
                                                     -- 3-10-2012
            I plan to replace diff: (which i no longer maintain) with this function.  Or perhaps i shall call this diff2:.
                                                     -- 4-10-2012
            """
            a = a
            b = b
            if k == 0:
               try:              
                   k == a.k      # use a.k if k not given
               except AttributeError:
                   print "need supply k = no. of clustering centre as an argument!\n --> setting default = 5"
                   k = 5
                   a.k = 5
            else:
               a.k = k       # else set a.k = k

            print "\n----------------------\n**** a, b, k =", a.name, b.name, k
            if newSeeding:
                # kmeans for the first pattern
                aCentroids, aData = a.getKmeans(k=k, threshold = threshold)           
                if seedBwithA:
                    # branching added 4-10-2012
                    #bCentroids, bData = b.getKmeans(k=aCentroids[0], threshold = threshold )           
                    x = b.getKmeans(k=k, threshold=threshold)
                    bCentroids, bData = x['centroids'], x['data']
                else:
                    # kmeans for the second pattern
                    #bCentroids, bData = b.getKmeans(k=k, threshold = threshold )
                    x = b.getKmeans(k=k, threshold=threshold)
                    bCentroids, bData = x['centroids'], x['data']
                a.centroids, a.data = aCentroids, aData 
                b.centroids, b.data = bCentroids, bData 
            else:
                aCentroids, aData = a.centroids, a.data 
                bCentroids, bData = b.centroids, b.data 
            #############################
            # first setting aCluster, bCluster 
            #       = lists of dicts 
            #       =[{'x': x-coord, 'y': y-coord, 'weight': cluster size (or weight)}]
            aClusters =[0] * k       #initialising a length-k list for convenience
            bClusters =[0] * k
            for i in range(k):                                        # i = 0,1,..., 5 by default
                aClusters[i] = { 'x'     : aCentroids[0][i][0],    # x-coord, y-coord, weight of the i-th cluster in a
                                 'y'     : aCentroids[0][i][1],
                                 'weight': len([v for v in aCentroids[1] if v ==i]),
                               }
                bClusters[i] = { 'x'     : bCentroids[0][i][0],    # doing the same for b
                                 'y'     : bCentroids[0][i][1],
                                 'weight': len([v for v in bCentroids[1] if v ==i]),
                               }
                #print 'aClusters, bClusters', aClusters, bClusters     #debug

            ############################################## 
            #  new:  3-10-2012
            #  adding aNullClusters (weight=0 , location same) for vanishing/creation

            aNullClusters = [{'x':v['x'], 'y':v['y'], 'weight':0 }  for v in aClusters]
            bNullClusters = [{'x':v['x'], 'y':v['y'], 'weight':0 }  for v in bClusters]
            aClustersModified = aClusters + aNullClusters           # a vector (list) of length 2k
            bClustersModified = bClusters + bNullClusters

            # 
            # 
            ##############################################

            #############################
            # now do the matching
            #     first compute the distance-squared matrix - multiplied by weights
            #  ---> a[0],...a[k-1]
            #  |
            #  |
            #  v
            #  b 

            ###########################################
            # modified: 3-10-2012
            
            distanceSquaredMatrix = np.zeros((2*k, 2*k))
            for i in range(2*k):
                for j in range(2*k):
                    distanceSquaredMatrix[i,j] =    (aClustersModified[i]['x'] - bClustersModified[j]['x'])**2   \
                                           +        (aClustersModified[i]['y'] - bClustersModified[j]['y'])**2   \
                                           +   1.0 * abs(np.log((1.0+aClustersModified[i]['weight'])/(1.0+bClustersModified[j]['weight'])))
                                                   #^--let's try this - why not
            #print "distanceSquaredMatrix:", np.array([int(x) for x in sum(distanceSquaredMatrix.tolist(),[]) ]).reshape(k,k)  #debug

            #
            ###########################################

            ##################################################################################
            #     now use the Munkres implementation for the Hungarian algorithm
            #     reference: for Munkres http://software.clapper.org/munkres/ 
            from munkres import Munkres, print_matrix
            m = Munkres()
            indices = m.compute(distanceSquaredMatrix)
           
            print 'x, y, and log of smoothed weight ratio:'
            for i, j in indices:
                print aClustersModified[i]['x'], aClustersModified[i]['y'], '->\t',   \
                      bClustersModified[i]['x'], bClustersModified[i]['y'],           \
                      '\t', np.log((1.0+aClustersModified[i]['weight']) / (1.0+ bClustersModified[j]['weight']))
            #################################
            # make some nice picture outputs
            img1 = a.img.copy()
            img2 = b.img.copy()

            count = 0
            meanDisplacementWeightedX = 0
            meanDisplacementWeightedY = 0
            totalWeight = 0
            for i,j in indices:
                count +=1
                Xa = int(aClustersModified[i]['x'])
                Ya = int(aClustersModified[i]['y'])
                Xb = int(bClustersModified[j]['x'])
                Yb = int(bClustersModified[j]['y'])
                #meanDisplacementWeightedX += (Xb-Xa) * np.log(1.0+aClustersModified[i]['weight'] * bClustersModified[j]['weight'])/2
                #meanDisplacementWeightedY += (Yb-Ya) * np.log(1.0+aClustersModified[i]['weight'] * bClustersModified[j]['weight'])/2

                meanDisplacementWeightedX += (Xb-Xa) * (aClustersModified[i]['weight'] + bClustersModified[j]['weight'])/2
                meanDisplacementWeightedY += (Yb-Ya) * (aClustersModified[i]['weight'] + bClustersModified[j]['weight'])/2
                totalWeight +=  (aClustersModified[i]['weight'] + bClustersModified[j]['weight'])/2

                for ii in range(Xa-10, Xa+11):
                    try:
                        #img1.putpixel((ii,Ya), (count *220*5 //k % 255, (count*255*2 //k + 100) % 255, (count*255*3+200) //k % 255))
                        img1.putpixel((ii,Ya), (0,0,0))
                    except IndexError:
                        continue
                for jj in range(Ya-10, Ya+11):
                    try:
                        img1.putpixel((Xa,jj), (0,0,0))
                    except IndexError:
                        continue

                for ii in range(Xb-10, Xb+11):
                    try:
                        img2.putpixel((ii,Yb), (0,0,0))
                    except IndexError:
                        continue
                for jj in range(Yb-10, Yb+11):
                    try:
                        img2.putpixel((Xb,jj), (0,0,0))
                    except IndexError:
                        continue
                #################################################
                # adding an "arrow" to img2, 4 Oct 2012
                # like this:
                #   ------> 
                #   ^
                #   |
                #   |
                #   |
                #
                count = -1
                if Xb - Xa != 0:
                  for ii in range(Xb, Xa, np.sign(Xa-Xb)):    #going backwards
                    count +=1
                    img2.putpixel( (ii,Yb), (150,50,150) )
                    if count < 6:
                       for jj in range(-count, count+1):
                           try:
                               img2.putpixel((ii,Yb +jj), (150,50,150))
                           except IndexError:
                               continue                   
                count = -1
                if Yb -Ya != 0:
                  for jj in range(Yb, Ya, np.sign(Ya-Yb)):
                    count +=1
                    img2.putpixel( (Xa, jj), (150,50,150))
                    if count < 4:
                       for ii in range(-count, count+1):
                           try:
                               img2.putpixel((Xa+ii,jj), (150,50,150))
                           except IndexError:
                               continue
                #
                ################################################# 

            meanDisplacementWeightedX = (meanDisplacementWeightedX+0.0)/ totalWeight
            meanDisplacementWeightedY = (meanDisplacementWeightedY+0.0)/ totalWeight

            #####################################################
            #  adding a total vector sum in the middle
            print '\n-------------------------------\nWeighed total displacement:', meanDisplacementWeightedX, ',', meanDisplacementWeightedY

            #tX = int(meanDisplacementWeightedX /k)
            #tY = int(meanDisplacementWeightedY /k)                       
            tX = int(meanDisplacementWeightedX * 20)
            tY = int(meanDisplacementWeightedY * 20)

            x = width //2
            y = height//2

            count = -1
            if tX != 0:
                for ii in range(x+tX, x, np.sign(-tX)):   # going backwards
                    count +=1
                    try:
                       img2.putpixel( (ii, y+tY), (255,0,255) )
                    except IndexError: 
                        print 'index error!!!!!!!!!!!'
                    if count < 15:
                       for jj in range(-count, count+1):
                           try:
                               img2.putpixel((ii,y+tY+jj), (255,0,255))
                           except IndexError:
                               continue                   
            count = -1
            if tY != 0:
                for jj in range(y+tY, y, np.sign(-tY)):
                    count +=1
                    img2.putpixel( (x, jj), (255,0,255))
                    if count < 10:
                       for ii in range(-count, count+1):
                           try:
                               img2.putpixel((x+ii,jj), (255,0,255))
                           except IndexError:
                               continue
            #xxx = raw_input("press enter:") #debug               

            #
            #################################################


            img1.show()
            img2.show()
            indices.sort( key = lambda w : (-aClustersModified[w[0]]['weight']) )

            print [(w, aClustersModified[w[0]]['weight']) for w in indices]
            img3 = a.makeImageWithClusters(k=k, indices = [v[0] for v in indices[:k]], threshold = threshold)        # only indices up to k are healthy 
            img4 = b.makeImageWithClusters(k=k, indices = [v[1] for v in indices[:k]], threshold = threshold)        # the rest are dummy
            a.print2screen(img3)
            b.print2screen(img4) 

            logScore =  np.log(np.array(distanceSquaredMatrix).sum())
            timeString = str(int(time.time()))

            if outputFolder != '':
                #a.print2file(path =outputFolder +timeString +'centroids-a-score-' +str(round(logScore,4))+'.png', img = img1)
                a.print2file(path =outputFolder + str(round(logScore,4))+ 'centroids-a-k_' +str(k) +'-threshold_' +str(threshold) +'.png', img = img1)
                a.print2file(path =outputFolder + str(round(logScore,4))+ 'centroids-b-k_' +str(k) +'-threshold_' +str(threshold) +'.png', img = img2)
                a.print2file(path =outputFolder + str(round(logScore,4))+ 'clusters-a-k_'  +str(k) +'-threshold_' +str(threshold) +'.png', img = img3)
                b.print2file(path =outputFolder + str(round(logScore,4))+ 'clusters-b-k_'  +str(k) +'-threshold_' +str(threshold) +'.png', img = img4)
            #################################
            # return: [ ((ax1,ay1),(bx1,by1)), ((ax2,ay2),(bx2,by2)),... ] , log (total cost)

            print "\n...............\nScore (log sum distance) = " , logScore
            return indices, logScore

       ##
       ## end of diffWithCreationAndDestruction()
       #####################################################################################################################  
#################################################
#						#
#		 main():			#
#						#
#################################################

def main(filePath, k = 6 , width = width, height = height, threshold = 1):
        #
        # just a test script
        #
        c = pattern2dWithClustering( name = 'c', path = filePath,
                                      width=width, height=height, 
                                      colourbar = 'colourbarCWBwhiteBackground')

        #c.print2screen()  #test


        ###########
        # 2. getting the kmeans first with half the threshold, and twice the number of centroids
        # 11-9-2012

        #centroids, data = c.getKmeans(k= k * 2, threshold=threshold /2) #old
        x = c.getKmeans(k= k * 2, threshold=threshold /2)
        centroids, data = x['centroids'], x['data']
        print type(centroids)
        print centroids
        centroidWeight = {}   #initialising
        for i in range(k):
            centroidWeight[i] = int( np.log2(1+len([v for v in centroids[1] if v ==i])))
        for index in range(k):
            centroid = centroids[0][index]
            i, j = [int(v) for v in centroid]
            # change the intensity (and thus colour) and replot
            #c.matrix[j,i] = 30
            for ii in range(i-0-centroidWeight[index],i+1+ centroidWeight[index]): # fixing the size of the marker ...
                                                                                  #  according to the log centroid weight
                c.matrix[j,ii] = 1             
            for jj in range(j-0-centroidWeight[index],j+1+ centroidWeight[index]):
                c.matrix[jj,i] = 1


        ###########
        # 1. getting the kmeans
        x = c.getKmeans(k= k, threshold=threshold)
        centroids, data = x['centroids'], x['data']
        
        print type(centroids)
        print centroids
        centroidWeight = {}   #initialising
        for i in range(k):
            centroidWeight[i] = int( np.log2(1+len([v for v in centroids[1] if v ==i])))
        for index in range(k):
            centroid = centroids[0][index]
            i, j = [int(v) for v in centroid]
            # change the intensity (and thus colour) and replot
            #c.matrix[j,i] = 80
            for ii in range(i-0-2*centroidWeight[index],i+1+ 2*centroidWeight[index]): # fixing the size of the marker ...
                                                                                  #  according to the log centroid weight
                c.matrix[j,ii] = 50              
            for jj in range(j-0-2*centroidWeight[index],j+1+ 2*centroidWeight[index]):
                c.matrix[jj,i] = 50
        ##############
        #  3. making the image

        c.img = c.makeImage()
        # c.print2screen() #test
        return c
#        # the following codes are from 
#        #   http://glowingpython.blogspot.tw/2012/04/k-means-clustering-with-scipy.html
#        # assign each sample to a cluster
#        idx,_ = vq(data,centroids)
#        # some plotting using numpy's logical indexing
#        idx,_ = vq(data,centroids)
#        plot(data[idx==0,0],data[idx==0,1],'ob',
#             data[idx==1,0],data[idx==1,1],'or',
#             data[idx==2,0],data[idx==3,1],'oy',
#             data[idx==3,0],data[idx==3,1],'oo')             
#        plot(centroids[:,0],centroids[:,1],centroids[:,2],centroids[:,3],'sg',markersize=8)
#        show()


if __name__== '__main__':

        #######################################################################
        #  loading the image

        k = 10          # set k = no. of clusters here
        threshold = 40
        height = 561
        width = 441
        outputFolder = '../DEMO-pics/clustering/'
        inputFolder = '../data-QPESUMS/'
        inputFilesList = os.listdir(inputFolder)
        inputFilesList.sort()
        N = len(inputFilesList)

        for i in range(400,N):   # can change here
            fileName = inputFilesList[i]
            try:
                clusteredImage = main( filePath = inputFolder + fileName, k =k, 
                                       threshold = threshold, width=width, height=height)
            except ValueError:
                print i, 'ValueError! ', fileName
                continue
            except IndexError:
                print i , 'indexError! ', fileName
                continue
            if i % 3 == 0:
                 clusteredImage.print2screen()
            clusteredImage.print2file(outputFolder+fileName+ '-with-' + str(k) + '-clusters-and-threshold-'+str(threshold) +'.png')
            print '\n===================================================\n', \
                                   i, fileName, ';\n-------------------\n',

