"""
#   regridding:  source folder-> target folder

USE:

cd /media/TOSH~/ARMOR/python/

from armor import defaultParameters as dp
from armor.dataStreamTools import regridFolder as rf
reload(rf)
rf.regridFolder(dp.defaultRoot+"data/march2014/WRFEPS/20140311/",
                dp.defaultRoot+"data/march2014/WRFEPS[regridded]/20140311/",
                key1="WRF20")
rf.regridFolder(dp.defaultRoot+"data/march2014/WRFEPS/20140312/",
                dp.defaultRoot+"data/march2014/WRFEPS[regridded]/20140312/")
rf.regridFolder(dp.defaultRoot+"data/march2014/WRFEPS/20140313/",
                dp.defaultRoot+"data/march2014/WRFEPS[regridded]/20140313/")


"""
#   imports
import os, time
from armor import pattern
from armor.geometry import regrid
DBZ = pattern.DBZ
a=pattern.a

#   parameters

#   defining the functions

def regridFolder(sourceFolder, targetFolder, key1="", key2="", nokey1="asdfasdfxxzzzfxxk", referenceDBZ=pattern.a):
    time0 = int(time.time())
    print "..............................................................."
    print "sourceFolder:", sourceFolder
    print "starting time:", time.asctime()
    L   = os.listdir(sourceFolder)
    L   = [v for v in L if v.endswith(".txt") and key1 in v and key2 in v and (not nokey1 in v)]
    L.sort()
    if not os.path.exists(targetFolder):
        os.makedirs(targetFolder)
    if a.matrix.sum()==0:   #loading the reference DBZ object "the canvass"
        a.load()
    
    for fileName in L:
        print fileName,
        b   = DBZ(name="", dataPath=sourceFolder+fileName, outputPath=targetFolder+fileName)
        b.load()
        b1  = regrid.regrid(b,a)
        b1.outputPath   = b.outputPath
        b1.save()
        #print b.outputPath  #debug
        #print b1.outputPath #debug
        print ".. done"

    return {'timeSpent': int(time.time())-time0 }
