# -*- coding: utf-8 -*-
"""
patternMatchingTest20130904 Kong Rey
    purpose
        to carry out the plan in the document 
            2013-09-03-test-of-matching-algorithms.txt
        on STS Kong-Rey

    outline
        1.  massage the data, build the DBZstream objects (without loading),
            and store them
        2.  create the images, and store them
        3.  inspect the data and verify
        4.  construct a set of transformed data (881,921) with the right coords
            and store them for quick access
        5.  write the tests
        6.  carry out the tests --> output summaries and reports
    For details, see __init__.py

    Runs
        1.  on machine k-801, ubuntu 13, Room 801 Civil Engineering
            /media/k/KINGSTON/ARMOR/python
        2.  otherwise, adjust the parameters in the "settings" section
        
"""
######################
#   imports
import os, sys, re
import time
from armor import pattern
import numpy as np
import pickle

######################
#   settings

timeString = str(int(time.time()))

obs_folder      = '/home/k/ARMOR/data/KONG-REY/OBS/'
obs_lowerLeft   = (18., 115.)
obs_upperRight  = (29., 126.5)
obs_gridShape   = (881,921)

wrf_folder      = '/home/k/ARMOR/data/KONG-REY/WRFEPS/'
wrf_lowerLeft   = (20., 117.5)
wrf_upperRight  = (28., 124.5)
wrf_gridShape   = (150,140)
"""
/ARMOR/data/KONG-REY/WRFEPS/READMES/README.txt
STEP1:cp WRFWEPS data(M01~M20) to this file
      use getdata_m.gs regrid data as 0.005 degree data
STEP2:cd output/
      compile readbin.f 
      binary data(size:4*140*150*4(time step)=336,000) to ASCII data(x:140,y:150,left point 117.5,20.5,reso:0.05)
>>> 117.5 + 0.05*140
124.5
>>> 20.5+0.05*150
28.0
>>> 

"""

# pydump_folder = '/home/k/ARMOR/data/KONG-REY/pydumps/'  # for python intermediate files
#summary_folder  = '/home/k/ARMOR/data/KONG-REY/summary/' + timeString + '/'
summary_folder  = '/home/k/ARMOR/data/KONG-REY/summary/'
summaryFolder   = summary_folder   # ALIAS
try:
    os.makedirs(summary_folder + 'COMPREF/')
    os.makedirs(summary_folder + 'WRF/')
except OSError:
    pass

########################
#   building blocks

def getList(folder, key1="", key2="", key3=""):
    """get the list of files in the folder containing key1 and key2"""
    L   = os.listdir(folder)
    L   = [v for v in L if (key1 in v) and (key2 in v) and (key3 in v)]
    return L

def constructOBSstream(folder=obs_folder):
    """
    class DBZstream:
        def __init__(self, dataFolder='../data_temp/', 
                     #name="COMPREF.DBZ", 
                     name="",
                     lowerLeftCornerLatitudeLongitude=defaultLowerLeftCornerLatitudeLongitude, 
                     upperRightCornerLatitudeLongitude=defaultUpperRightCornerLatitudeLongitude,
                     outputFolder="",
                     imageFolder="",
                     preload=False):

    """    
    #L = getList(folder=folder, key1='COMPREF', key2='txt')
    #L = [v for v in L if os.path.isfile(folder+v)]
    ds = pattern.DBZstream(dataFolder= folder, 
                                 name="COMPREF.DBZ", 
                                 lowerLeftCornerLatitudeLongitude   = obs_lowerLeft ,
                                 upperRightCornerLatitudeLongitude  = obs_upperRight,
                                 outputFolder   = summaryFolder + 'COMPREF/',
                                 imageFolder    = summaryFolder + 'COMPREF/',
                                 preload=False)
    pickle.dump(ds, open(summary_folder + 'COMPREF/dbzstream.pydump', 'w'))
    return ds

def loadOBSstream(ds):
    print 'loading .0000'
    ds.load('.0000')
    ds.load('.0300')
    ds.load('.0900')
    print 'loading .1200'
    ds.load('.1200')
    ds.load('.1500')
    ds.load('.1800')
    ds.load('.2100')
    print 'cutting unloaded'
    ds.cutUnloaded()
    print 'dumping'
    pickle.dump(ds, open(summary_folder + 'COMPREF/dbzstreamLoaded.pydump', 'w'))
    return ds

def constructWRFstream(folder=wrf_folder, M=1):
    """M = model number (from 1 to 20)
    """
    ds = pattern.DBZstream(dataFolder= folder, 
                                 name="WRF" + ('0'+str(M))[-2:] + ".DBZ", 
                                 lowerLeftCornerLatitudeLongitude   = wrf_lowerLeft ,
                                 upperRightCornerLatitudeLongitude  = wrf_upperRight,
                                 outputFolder   = summaryFolder + 'WRF/',
                                 imageFolder    = summaryFolder + 'WRF/',
                                 key1 = 'M' +("00" + str(M))[-2:],
                                 preload=False)
    # then sort out the dataTimes:  
    # 201308300000f003_M01.txt - 3-hour forecast at 20130830.0000 UTC
    for D in ds:
        # extract the forecast hour from "f___"
        fh = D.dataPath[-10:-8]
        dh = D.dataTime[ -4:-2]
        dh_new = ('0' + str(int(dh)+int(fh)))[-2:] + '00'
        D.dataTime = D.dataTime[:-4] + dh_new
    # cannot regrid/recentre until loaded!!!
    ds.load()
    #for D in ds:
    #    D.vmin=-50
    #ds.saveImages(flipud=True)
    ds.regrid(pattern.a)  # regrid to i,j=(881, 921)
    ds.recentre()
    for D in ds.list:
        # reset the D.name to something that makes sense
        D.name = 'WRF' + ('0'+str(M))[-2:] + '.' + D.dataTime
    pickle.dump(ds, open(summary_folder + 'WRF/dbzstream' + ('0'+str(M))[-2:] + '.pydump', 'w'))
    return ds

def constructAllWRFstreams(first=1, last=20):
    WRFstreams=[]
    for m in range(first, last+1):
        print m
        ds = constructWRFstream(M=m) 
        WRFstreams.append(ds)
    pickle.dump(WRFstreams, open(summary_folder + 'WRF/dbzstreamAll.pydump', 'w'))
    return WRFstreams


def constructAllWRFstreamsRegridded(first=1):
    pattern.a.load()
    WRFstreams = pickle.load(open(summary_folder+'WRF/dbzstreamAll.pydump', 'r'))
    for M in range(first, len(WRFstreams)+1):
        ds = WRFstreams[M-1]        # the models are labelled 1-20
        print "\n.......\n", M, ds.name 
        #ds.outputFolder = summary_folder+ 'WRF[regridded]'
        #debug
        #print ds[0].outputFolder
        #print ds[0].dataPath
        print 'loading...'
        ds.load()
        # debug
        #print ds[0].matrix.shape
        #ds[0].show()
        #ds[1].show()
        #ds[4].show()
        # END debug
        ds.setOutputFolder(summary_folder+'WRF[regridded]/')
        ds.setImageFolder(summary_folder+'WRF[regridded]/')
        #print 'outputFolder:', ds.outputFolder
        print ds[0].outputFolder
        print 'imageFolder:', ds.imageFolder
        print 'regridding...'
        ds.regrid(pattern.a)
        for D in ds:
            print D.name,
            if 'regridded' not in D.name:
                D.name += '[regridded]'
            # debug
            #print D.matrix.shape
            #D.show()
            # END debug
        print 'saving...'
        pickle.dump(ds, open(summary_folder + 'WRF[regridded]/dbzstream' + ('0'+str(M))[-2:] + '.pydump', 'w'))
    return WRFstreams
#######################
#   carryout

def createDBZimages(ds=summary_folder+'WRF/dbzstream01.pydump', withCoast=True, vmin=-0, vmax=100, toLoad=True):
    #or createDBZimages(ds=summary_folder+'COMPREF/dbzstream.pydump'):
    if isinstance(ds, str):     # load data if it's a string (i.e. path)
        ds = pickle.load(open(ds,'r'))
        #ds.load()
        print ds, ' -- ds setup' 
    #debug
    print ds[1].name, ds[1].imagePath
    for D in ds:
        if D.name.endswith('[regridded]'):
            D.name = D.name[:-11]
            print D.name
        D.vmin= vmin
        D.vmax= vmax
    #ds[0].show()
    print 'loading DBZ patterns'
    if toLoad:
        ds.load()
    #debug
    #ds[1].show()
    ds.saveImages(flipud=True,drawCoast=withCoast,verbose=False)

def createAllWRFimages(folder=summary_folder+'WRF/', first=1, last=20, vmin=-45, vmax=100, withCoast=False, toLoad=True):
    for m in range(first, last+1):
        print m
        # the pattern is already loaded in the regridded version of the WRF datastreams, so toLoad=False
        #createDBZimages(ds=summary_folder+'WRF[regridded]/dbzstream' + ('0'+str(m))[-2:] +'.pydump', vmin=vmin, vmax=vmax, toLoad=False)
        createDBZimages(ds= folder+'dbzstream' + ('0'+str(m))[-2:] +'.pydump', vmin=vmin, vmax=vmax, toLoad=toLoad, withCoast=withCoast)

def patternMatchingTest(matchingAlgorithm,
            observations= '/home/k/ARMOR/data/KONG-REY/summary/COMPREF/dbzstream.pydump', 
            modelsFolder= '/home/k/ARMOR/data/KONG-REY/summary/WRF[regridded]/',
            #key1='0828',
            key1='',
            key2='',
            #key3='',
            kwargs = {},        # keyword arguments for the matchinging algorithm, just in case
            verbose=True
            ):
    """
    the COMPREF observations are loaded in situ since it need not be regridded
    whereas the model data are pre-regridded and stored
    """
    t0 = time.time()
    ds1 = pickle.load(open(observations,'r'))
    ds1.list = [v for v in ds1.list if (key1 in v.dataTime or key1 in v.name) \
                                   and (key2 in v.dataTime or key2 in v.name)]
    ds1.list.sort(key=lambda v:v.dataTime)
    # debug
    #print ds1.list
    print 'loading list with keywords [ %s %s ]' %(key1, key2) 
    ds1.load(verbose=verbose)
    # end debug
    modelsList = [v for v in os.listdir(modelsFolder) if '.pydump' in v]
    modelsList.sort(key = lambda v: int(re.findall(r'\d+',v)[0]))
    print "modelsList", modelsList
    scores = {}             # scores = {model number: [('dataTime', score), ('dataTime', score),...], ...}
    print 'loading ds2 (model data)'
    for path in modelsList:
        modelIndex = int(re.findall(r'\d+', path)[0])
        ds2 = pickle.load(open(modelsFolder+path, 'r'))
        # debug
        ds2.list = [v for v in ds2.list if key1 in v.dataTime]
        # end debug

        ####################
        # key lines
        print 'computing scores between %s and %s ...' %(ds1.name, ds2.name)
        s, matching_algorithm_name   = matchingAlgorithm(ds1, ds2)   # list of the form [('20120612.0000', 0.9),...]  
        scores[modelIndex] = dict(s) # { model index: {'dataTime': score,...}, ...}
        # debug
        if verbose:
            print scores
            print '..................................................'
        #
        ####################

    print 'sorting the results...'
    #print 'scores', '\n', scores  #debug
    # bestMatchAtEachTime
    T1 = [v.dataTime for v in ds1]
    T2 = [v.dataTime for v in ds2]  #any ds2 will do - they are the same, in this case we pick the last one 
    T  = set(T1).intersection(T2)
    dataTimeList  = sorted(list(T))
    #print 'dataTimeList:', dataTimeList      #debug
    highestScores = []
    for t in dataTimeList:
        print t
        highestScoreAt_t = max([scores[u][t] for u in scores.keys()])
        new_entry = (t, highestScoreAt_t, [u for u in scores.keys() if scores[u][t]==highestScoreAt_t])
        print new_entry
        highestScores.append(new_entry)

    # bestMatchOverall
    print scores      # debug
    averageScores = [(Model, np.mean(scores[Model].values())) for Model in scores.keys()]    # list of [(Model, mean score),...]
    highestScore = max([v[1] for v in averageScores])
    bestMatch    = [u[0] for u in averageScores if u[1]==highestScore] 
    # debug
    print 'average scores , highest average, best match', averageScores, highestScore, bestMatch
    #xx= raw_input('press enter')    


    bestMatchAtEachTime = highestScores
    bestMatchOverall    = (highestScore, bestMatch)

    # the following lines do not work well since oftentimes we have multiple pointers (names) to a single object/function
    # and so they are replaced by returning the function name in the function itself
    #allvars = vars()
    #matching_algorithm_name = [v for v in allvars if allvars[v]==matchingAlgorithm][0]
    result= {'best matches'          : bestMatchAtEachTime, 
             'best overall match'    : bestMatchOverall, 
             'all scores'            : scores,
             'matching algorithm'    : matching_algorithm_name,
             'dataset1[obs]'         : observations,
             'dataset2[models]'      : modelsFolder,
             'time spent'            : time.time() - t0,
             }

    pickle.dump(result, open(summary_folder+ 'pydumps/results_' + matching_algorithm_name+ '+' +\
                             key1 + '+' + key2 + str(int(time.time())) + '.pydump', 'w'))

    print "time spent:", time.time()-t0
    return result


def pmt(*args, **kwargs):
    """alias"""
    return patternMatchingTest(*args,**kwargs)

def patternMatchingTestThreeSeparateDays(matchingAlgorithm):
    L = ['0828', '0829', '0830']
    results =[]
    for key in L:
        res= patternMatchingTest(matchingAlgorithm=matchingAlgorithm,
                                key1= key)
        results.append(res)
    return results

def pmt3d(*args, **kwargs):
    """alias"""
    return patternMatchingTestThreeSeparateDays(*args, **kwargs)


#################################################
#   the various matching algorithms

def plain_correlation(ds1, ds2):
    return ds1.corr(ds2), 'plain_correlation'  #result, name

def moments(ds1, ds2):
    """
    moments - global
    """
    return ds1.invariantMomentsCorr(ds2), 'moments_global'


def regionalGlobalMoments(ds1, ds2):
    """
    moments - regional /averaged
    """
    return ds1.regionalAndGlobalInvariantMomentsCorr(ds2), 'moments_regional+global'

def test4():
    """
    gabor filter?!
    """
    pass
def test5():
    pass
def test6():
    pass
def test7():
    pass
def test8():
    pass

def main0(*args):
    print args

def main(*args):
    #massageData()
    createDBZimages()
    constructTransformedDBZstreams()
    patternMatchingTest()
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()

"""
if __name__ == '__main__':
    import sys
    args = sys.argv
    main(*args)
"""
