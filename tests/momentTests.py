# moments.py
# testing the invariant moments for the report on tuesday 25 june 2013
# date:  24-06-2013

"""
cd /media/KINGSTON/ARMOR/python
python
####
###
##
#

from armor.tests import momentTests as tests
reload(tests); result= tests.randomTest(maxLoopCount=8)
tests.saveTestResult(result)

#
##
###
#####
#reload(tests)
#G=tests.gaussianDemo()
#x = tests.main()


# just found the old code in armor.geometry.momentTests - use that and 
# the already written a.invariantMoments() method too
"""
import time
import os
import numpy as np
ma = np.ma
from numpy import exp
from armor import pattern
dbz = pattern.DBZ
from armor.geometry import moments
from armor import defaultParameters as dp

def gaussian(x,y, x0=0, y0=0, varx=2. ,vary=2.):
    g = exp(-(x-x0)**2/varx -(y-y0)**2/vary)
    return g

def gaussianDemo():
    X,Y = np.meshgrid(range(400),range(400))
    g   = 10.*gaussian(x=X,y=Y, x0=240, y0=260, varx=5000., vary=9800.)
    G   = dbz(matrix=g, vmin=-4, vmax=10)
    G.show()
    return G

def matchingTest(vector):
    """ input:  a list of corr coeff scores from moments
    output:  match or not
    criteria:
    all > 0.9 - yes
    all > 0.8, all but one > 0.9, four>.99   - yes
    else - no
    """
    point99 = len([v for v in vector if v>0.99])
    point9  = len([v for v in vector if v>0.90])
    point8  = len([v for v in vector if v>0.80])

    if point9 ==6:
        testResult = True
    elif point9 ==5 and point99 >=4 and point8==6:
        testResult = True
    else:
        testResult = False
    return testResult
    
def randomTest(dataFolder='../data_temp/', 
                #cmap='gray', 
                cmap=dp.defaultCmap,
                threshold=-999, maxLoopCount=1000, waitingTime=1):
    """testing random shapes with 3 - 7 moments
    """
    rand = np.random.random
    L = os.listdir(dataFolder)
    L = [v for v in L if (v[-4:] == '.dat') and (v[:7]=='COMPREF')]
    N = len(L)
    testRecord = []
    loopCount=0
    while loopCount < maxLoopCount:
        print '\n=================================='
        loopCount+=1
        if loopCount%2 != 0:
            print 'two random files'
            fileNumbers = (N*rand(2)).astype(int)
            filePairType='RANDOM'
        else:
            print 'TWO CONSECUTIVE FILES'
            fileNumber0 = int((N-1)*rand())
            fileNumbers = [fileNumber0, fileNumber0+1]
            filePairType='CONSECUTIVE'
        a = [0,0]
        for count, n in enumerate(fileNumbers):
            print L[n]
            filePath = dataFolder+ L[n]
            x = np.loadtxt(filePath)
            x = x.view(ma.MaskedArray)
            x.fill_value=-999
            x.mask = False
            x.mask += (x==-999) + (x==-99)
            if threshold ==-999 : # if we choose to use the original data
                a[count] = dbz(matrix=x, name=L[n],cmap=cmap)
            else:              # if we cut off and turn the diagram into 0-1
                a[count] = dbz(matrix=(x.filled()>=threshold), name=L[n],cmap=cmap, vmin=-0.5, vmax=1)
        a, b = a
        a.invar=a.invariantMoments()
        b.invar=b.invariantMoments()
        invar = [0,0,0,0,0,0,0,0]
        for i in range(1,8):
            invar[i] = np.corrcoef(a.invar[:i], b.invar[:i])[0,1]
        print '------------------------------'
        print a.name, '\n', 'invar moments', a.invar
        print '.................................'
        print b.name, '\n', 'invar moments', b.invar
        print '.................................'
        print 'correlations between (some of the) invariant moments'
        print 'FOR '+filePairType+ ' DATA PAIR\n', a.name, 'AND\n', b.name
        if threshold !=-999:
            print 'AND THRESHOLD =', threshold
        for i in range(1,8):
            print i, ":", invar[i], "\t"
        #a.copy().show4()
        #b.copy().show4()
        a.copy().showWithCoast()    # 2014-04-11
        b.copy().showWithCoast()        
        autoJudgement  = matchingTest(invar)   # our rule of thumb for auto testing
        print "autoJudgement:", autoJudgement
        humanJudgement = raw_input('Do they match [(y)es/(by)borderline yes/(n)o/(i)nsufficient data]? ')
        testRecord.append((a.name, b.name, autoJudgement, humanJudgement,invar))
    ### humanJudgement is used as ground truth
    truePositives  = len([v for v in testRecord if v[2] and ('y' in v[3].lower())])
    falsePositives = len([v for v in testRecord if v[2] and ('n' in v[3].lower())])
    falseNegatives = len([v for v in testRecord if not v[2] and ('y' in v[3].lower())])
    precision      = 1.* (truePositives+0.1)/ ((truePositives+0.1)+falsePositives)
    recall         = 1.* (truePositives+0.1)/ ((truePositives+0.1)+falseNegatives)
    F1             = 2.* precision * recall / (precision+recall)
    recordSheet= {'testRecord'    : testRecord,
                  'F1'            : F1,
                  'precision'     : precision,
                  'recall'        : recall,
                  'truePositives' : truePositives,
                  'falsePositives' : falsePositives,
                  'falseNegatives' : falseNegatives,
                  'NumberOfTrials' : maxLoopCount,
                 }
    return recordSheet

def saveTestResult(recordSheet, outputFolder='armor/tests/momentTests/'):
    fileName = str(int(time.time()))
    f = open(outputFolder+fileName,'w')
    f.write("# Hu's Invariant Moments Tests\n")
    f.write("# "+time.asctime()+"\n")
    
    L = sorted(recordSheet.keys())
    for i in L:
        if i == 'testRecord': 
            continue
        f.write('#'+str(i) + "\t:\t" + str(recordSheet[i]) +"\n")
    testRecord = recordSheet['testRecord']
    f.write('#--------------------------------------------\n')
    f.write('#Name1\tName2\tautoJudgement\thumanJudgement\tcorrelations(with one to seven moments)\n')
    f.write('#                                   [(y)es/(by)borderline yes/(n)o/(i)nsufficient data]\n\n')
    for entry in testRecord:
        f.write('\t'.join([str(v) for v in entry])+'\n\n')
    f.close()

def main():
    #gaussianDemo()
    testResult = randomTest(maxLoopCount=4)
    saveTestResult(testResult)
if __name__ =='__main__':
    main()



