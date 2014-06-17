#   localFeaturesTest20131211.py
#   to use local feature extraction to compare 
#   kongrey WRF05.20130828.0900 v. COMPREF.20130828.1500
#   c.f. ARMOR-local-feature-extraction-and-deformation.docx

########################################
#   importing
import time
import numpy as np
from matplotlib import pyplot as plt
from armor import pattern
from armor import objects3 as ob
from armor.geometry import localFeatures as lf
from armor.geometry import smoothCutoff as cut
reload(cut)
reload(lf)
reload(ob)
########################################
#   setting up
kongrey = ob.kongrey
wrf     = ob.kongreywrf2
wrf.fix()

w = wrf('WRF05')[3]
print w.name    #check
w.load()
w.show()

k=kongrey('0828.1500')[0]
print k.name
k.load()
k.setThreshold(0)
k.show()

##########################################
#   defining the parameters


#r = 30
#sigma = 5
#r = 50
#sigma = 10

r=30
sigma=5

########################################
#   analysing

w1 = lf.thresholding(w, thres=30, N=15, scale=4, operator='opening')
k1 = lf.thresholding(k, thres=30, N=15, scale=20,operator='closing')

#w_coords = w.features[1]['coordinates']
#k_coords = k.features[1]['coordinates']
ww = w.getWindow(*w.features[1]['coordinates'])
kk = k.getWindow(*k.features[1]['coordinates'])

ww.show()
kk.show()

#ww1 = w.above(20)
#kk1 = k.above(20)

#########################################
#   can't do this straight, need to fix the grids - need arrays of the same sizes
#kk.gaussianCorr(ww, sigma=5, saveImage=False)
ww_mask = cut.linearMask(*ww.matrix.shape, r=r)
kk_mask = cut.linearMask(*kk.matrix.shape, r=r)
ww.backupMatrix()
kk.backupMatrix()
ww.matrix *= ww_mask
kk.matrix *= kk_mask

ww_canvass      = ma.zeros(w.matrix.shape, fill_value=-999)
kk_canvass      = ma.zeros(w.matrix.shape, fill_value=-999)
ww_canvass.mask = False
kk_canvass.mask = False


wi  = (w.matrix.shape[0] - ww.matrix.shape[0])//2
wj  = (w.matrix.shape[1] - ww.matrix.shape[1])//2
ki  = (k.matrix.shape[0] - kk.matrix.shape[0])//2
kj  = (k.matrix.shape[1] - kk.matrix.shape[1])//2

ww_canvass[wi:wi+ww.matrix.shape[0], wj:wj+ ww.matrix.shape[1]] = ww.matrix
kk_canvass[ki:ki+kk.matrix.shape[0], kj:kj+ kk.matrix.shape[1]] = kk.matrix

ww.matrix = ww_canvass
kk.matrix = kk_canvass

x = kk.gaussianCorr(ww, sigma=sigma, saveImage=False)



