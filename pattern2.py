# -*- coding: utf-8 -*-
# continued from pattern.py
# defining the basic object we will be working with

# Note:  makeVideo - it doesn't work yet - i haven't yet solved the issues about opencv
#                     so i am outputing the slides only for the moment
#                      2013-09-23
##############################################################################################
#
#==== imports ================================================================================
# some of the stuff were moved to defaultParameters.py
import copy
import time
import os
import re
import numpy
import numpy as np
import numpy.ma as ma
#import matplotlib
import matplotlib.pyplot as plt
#import scipy.misc.pilutil as smp
#import numpy.fft as fft
#import shutil
#import sys
import pickle
from copy import deepcopy
try:
    from scipy import signal
    from scipy import interpolate
except ImportError:
    #print "Scipy not installed"
    pass


#==== setting up the global parameters========================================================

import defaultParameters as dp
from defaultParameters import *     #bad habits but all these variables are prefixed with "default"
                                    # or at least i try to make them to
import colourbarQPESUMS                  # the colourbars for the Central Weather Bureau
import colourbarQPESUMSwhiteBackground   # the same as above, with white backgrounds

#==== importing pattern.py====================================================================
from . import pattern
try:
    from dataStreamTools import makeVideo as mv
except ImportError:
    print "import error!  opencv not installed(?!)"
from dataStreamTools import kongrey as kr
dbz = pattern.DBZ
ds  = pattern.DBZstream
#==== defining the classes ===================================================================

#class DataStreamSets:
class DataStreamSet:        # correcting a long-standing typo 2014-03-09

    """
    class dataStreamSet:  DSS = dataStreamSet(ds0, ds1, ds2,...dsN) 
        where ds0 = observations, ds1, ds2,.. = models
        with the bare basic methods of analysis and output to panel of 20+ images
    """
    ############################################################################
    #   initialisation and basic function calls
    def __init__(self, ds0, *args):

        self.name   = ds0.name + '_' + '_'.join([v.name for v in args])
        self.obs    = ds0
        self.wrfs   = list(args)

    ############################################################################
    #   simple building block functions
    def getAllDataTimes(self):
        """
        get the union of the sets of dataTimes for all streams
        """
        dataTimes = set([v.dataTime for v in self.obs])
        for wrf in self.wrfs:
            dataTimes = dataTimes.union([v.dataTime for v in wrf])
        dataTimes = sorted(list(dataTimes))
        return dataTimes

    def getCommonDataTimes(self):
        """
        get the intersection of the sets of dataTimes for all streams
        """
        dataTimes = set([v.dataTime for v in self.obs])
        for wrf in self.wrfs:
            dataTimes = dataTimes.intersection([v.dataTime for v in wrf])
        dataTimes = sorted(list(dataTimes))
        return dataTimes

    def backupMatrices(self):
        self.obs.backupMatrices()
        for wrf in self.wrfs:
            wrf.backupMatrices()
    def restoreMatrices(self):
        self.obs.restoreMatrices()
        for wrf in self.wrfs:
            wrf.restoreMatrices()
    
    ############################################################################
    #   I/O's

    def load(self, stream_key="all", verbose=False, **kwargs):
        if stream_key == "all" or stream_key =="obs":
            print "loading obs"
            obs.load(**kwargs)
        if stream_key == "all" or stream_key =="wrf" or stream_key=="wrfs":
            print "loading wrfs"
            for wrf in wrfs:
                wrf.load(**kwargs)

    def unload(self, stream_key="all", verbose=False, **kwargs):
        if stream_key == "all" or stream_key =="obs":
            print "unloading obs"
            obs.unload(**kwargs)
        if stream_key == "all" or stream_key =="wrf" or stream_key=="wrfs":
            print "unloading wrfs"
            for wrf in wrfs:
                wrf.unload(**kwargs)

    def makeVideo2(self, ordering, outputFolder=''):
        """
        make video, with an ordering at each dataTime
        ordering = [[1,2,3,5], [3,4,6,1], ...] - first for the first dataTime, second for the second dataTime, etc
        """
        return mv.makeVideo( [self.obs] + self.wrfs,      # [ds0, ds1, ds2, ds3, ds4, ...], a list of armor.pattern.DBZstream objects
                           panel_cols = 5,              # number of colums in the panel
                           panel_rows = 5,              # no need to be filled
                           fourcc = cv.CV_FOURCC('F', 'L', 'V', '1'),
                           fps = defaultFps,
                           extension= '.avi',
                           #fourcc = cv.CV_FOURCC('P', 'I', 'M', '1'),
                           outputFileName ="",
                           outputFolder=outputFolder,
                           saveFrames = True,        # saving the frames as images
                           useCV2   = True,
                           ordering = ordering,           # ordering of the models
                          )

    def makeVideo1(self, ordering, outputFolder=''):
        """
        make video, with a single ordering for each dataStream in its entirety
        ordering = list, e.g. [2,3,4,5,1] <-- WRF2 goes first, then WRF3, WRF4, etc
        """
        ordering = [ordering] * len(self.getAllDataTimes())
        return self.makeVideo2(ordering, outputPath)

    ############################################################################
    #   analyses

    def analyse(self, algorithm):
        """
        input: algorithm
        output: ordering at each dataTime
            ordering = [[1,2,3,5], [3,4,6,1], ...] means WRF1, WRF2,WRF3, WRF5 for dataTime1; WRFs3,4,6,1, for the second dataTime, etc
    
        """
        pass

    def matching(self, algorithm, obsTime="", maxHourDiff=7, **kwargs):
        """
        input:
            algorithm   - the function defining the algorithm of matching
                algorithm(parameters):  (obs, wrf) -> score (real number)
                format of algorithm function: def alg1(a=pattern.a, ...., **kwargs):
            obsTime     - time at which obs is compared with the wrfs, e.g. "20140612.0200'
            maxHourDiff - the maximal time difference (in hours) between obs and wrfs, e.g. 7 (hours)
            kwargs      - parameters for the algorithm
        output:
            ranking with scores and optimal timeshifts    
        2014-03-07
        """
        if obsTime == "":                       # if the point for matching is not given, pick the first one
            obsTime = self.obs[0].dataTime
        
        ranking = []
        obs     = self.obs
        wrfs    = self.wrfs
        for wrf in wrfs:
            x       = algorithm(obs, wrf, obsTime=obsTime, maxHourDiff=maxHourDiff, **kwargs)
            score   = x['score']
            timeShift   = x['timeShift']
            ranking.append( {'wrf': wrf.name, 'timeShift': timeShift,   #timeShift: in hours
                            'score': score, 
                              'dataFolder': wrf.dataFolder,
                              'obsTime': obsTime,
                              'maxHourDiff': maxHourDiff    # tag them along just in case
                              } )  #dataFolder = for potential disambiguation 
            ranking.sort(key=lambda v:v['score'], reverse=True)
        return ranking


    def filtering(self, algorithm, stream_key="all", name_key="", verbose=False, **kwargs):
        """
        input:
            algorithm   - the function defining the algorithm of filtering
                algorithm(parameters):  changes a.matrix, a.name, no output given
                format of algorithm function: def alg1(a=pattern.a, **kwargs):
            stream_key  - keyword for choosing the DBZstreams to be filtered
                          if it's "obs" we filter just all of the self.obs
                          if it's "wrf" or "wrfs" we filter just all of the self.wrfs
            name_key    - keyword for choosing the DBZ patterns to be filtered

            kwargs      - parameters for the algorithm
        output:
            ranking with scores and optimal timeshifts    
        2014-03-07
        """
        obs     = self.obs
        wrfs    = self.wrfs
        #   first filter the obs
        if stream_key == "all" or stream_key == "obs" or stream_key == "OBS":
            for a in obs:
                if name_key in a.name:
                    algorithm(a, **kwargs)           # key line
                    if verbose:
                        print a.name
        if stream_key == "all" or stream_key == "wrf" or stream_key == "wrfs" \
                               or stream_key == "WRF" or stream_key == "WRFS" :
            for wrf in wrfs:
                for a in wrf:
                    if name_key in a.name:
                        algorithm(a, **kwargs)           # key line
                        if verbose:
                            print a.name
            

        
############################################

#   constants
DataStreamSets  = DataStreamSet #alias; # correcting a long-standing typo 2014-03-09
DSS = DataStreamSet # alias

"""
key example:  kongrey
"""
from dataStreamTools import kongrey as kr

#compref = pattern.DBZstream(dataFolder= kr.obs_folder,
#                 #name="COMPREF.DBZ", 
#                 name="",
#                 lowerLeftCornerLatitudeLongitude = kr.obs_lowerLeft , 
#                 upperRightCornerLatitudeLongitude = kr.obs_upperRight ,
#                 outputFolder= kr.summary_folder,
#                 imageFolder=kr.summary_folder,
#                 key1="",               # keywords to pick out specific files
#                 key2="",               # used only once in the __init__
#                 key3="",
#                 preload=False,
#                 imageExtension = '.png',     
#                 dataExtension  = '.txt',
#                 )
"""
print 'loading observations'
obs = kr.constructOBSstream(dumping=False)
print 'loading models',
wrfsFolder = kr.defaultWRFdumpsFolder # '/home/k/ARMOR/data/KONG-REY/summary/WRF[regridded]'
wrfs = []
for i in range(1,21):
    print i,
    wrf = pickle.load(open(wrfsFolder+'dbzstream' + ('0'+str(i))[-2:] + '.pydump'))
    #wrf.setDataFolder(asdfasdf)      # haven't defined this function in pattern.DBZstream yet
    wrfs.append(wrf)

kongreyDSS = DSS(obs, *wrfs)
"""

print 'constructing kongreyDSS'
obs = ds(name="COMPREF.DBZ", dataFolder=defaultRootFolder + 'data/KONG-REY/OBS/')
wrfs = []
for i in range(1,21):
    print i, 
    wrfName = name='WRF'+ ('0'+str(i))[-2:]
    wrf = ds(name=wrfName, key1=wrfName, 
             dataFolder=defaultRootFolder + 'data/KONG-REY/summary/WRF[regridded]/')
    wrfs.append(wrf)
kongreyDSS = DSS(obs, *wrfs)


def constructDSS(obsFolder, wrfsFolder):
    obsName     = obsFolder.split("/")[-1]
    wrfsName    = wrfsFolder.split("/")[-1]
    print 'Constructing DSS from:', obsName, ",", wrfsName
    print obsFolder
    print wrfsFolder
    obs = ds(name=obsName, dataFolder=obsFolder)
    wrfs = []
    for i in range(1,21):
        print i, 
        wrfName = name='WRF'+ ('0'+str(i))[-2:]
        wrf = ds(name=wrfName, key1=wrfName, 
                 dataFolder=wrfsFolder)
        wrfs.append(wrf)
    dss = DSS(obs, *wrfs)
    return dss

print "constructing march11 - march13 DSS objects"
march11 = constructDSS(dp.defaultRootFolder+"data/march2014/QPESUMS/", 
                       dp.defaultRootFolder+"data/march2014/WRFEPS[regridded]/20140311/")
march11.name    = "Rainband_11_March_2014"
march11.obs.list= [v for v in march11.obs.list if '20140311' in v.dataTime]

march12 = constructDSS(dp.defaultRootFolder+"data/march2014/QPESUMS/", 
                       dp.defaultRootFolder+"data/march2014/WRFEPS[regridded]/20140312/")
march12.name    = "Rainband_12_March_2014"
march12.obs.list= [v for v in march12.obs.list if '20140312' in v.dataTime]

march13 = constructDSS(dp.defaultRootFolder+"data/march2014/QPESUMS/", 
                       dp.defaultRootFolder+"data/march2014/WRFEPS[regridded]/20140313/")
march13.name    = "Rainband_13_March_2014"
march13.obs.list= [v for v in march13.obs.list if '20140313' in v.dataTime]

print "constructing may2014 DSS objects"
may19 = constructDSS(dp.defaultRootFolder+"data/may14/QPESUMS/",
                        dp.defaultRootFolder+"data/may14/WRFEPS19[regridded]/")
may19.name    = "Rainband_19_May_2014"
may19.obs.list= [v for v in may19.obs.list if '20140519' in v.dataTime]

may20 = constructDSS(dp.defaultRootFolder+"data/may14/QPESUMS/",
                        dp.defaultRootFolder+"data/may14/WRFEPS20[regridded]/")
may20.name    = "Rainband_20_May_2014"
may20.obs.list= [v for v in may20.obs.list if '20140520' in v.dataTime]


may21 = constructDSS(dp.defaultRootFolder+"data/may14/QPESUMS/",
                        dp.defaultRootFolder+"data/may14/WRFEPS21[regridded]/")
may21.name    = "Rainband_21_May_2014"
may21.obs.list= [v for v in may21.obs.list if '20140521' in v.dataTime]

may22 = constructDSS(dp.defaultRootFolder+"data/may14/QPESUMS/",
                        dp.defaultRootFolder+"data/may14/WRFEPS22[regridded]/")
may22.name    = "Rainband_22_May_2014"
may22.obs.list= [v for v in may22.obs.list if '20140522' in v.dataTime]

may23 = constructDSS(dp.defaultRootFolder+"data/may14/QPESUMS/",
                        dp.defaultRootFolder+"data/may14/WRFEPS23[regridded]/")
may23.name    = "Rainband_23_May_2014"
may23.obs.list= [v for v in may23.obs.list if '20140523' in v.dataTime]










