# test script for regression3
# regression3 : a more streamlined version of the shiiba regression and advection function/module

###########
#imports

import numpy as np
import numpy.ma as ma

from .. import pattern
from . import regression2 as regression

from ..advection import semiLagrangian
sl = semiLagrangian
from imp import reload
import time
lsq = np.linalg.lstsq

time0= time.time()

def tic():
    global timeStart
    timeStart = time.time()

def toc():
    print "time spent:", time.time()-timeStart

dbz=pattern.DBZ


################
# set up


def regress(a, b):

    phi0 = a.matrix
    phi1 = b.matrix

    phi0
    phi1
    phi1-phi0

    ##################
    # test
    phi0.sharedmask #check

    phi0.unshare_mask()
    phi1.unshare_mask()

    phi0.sharedmask #check
    phi0.up     = np.roll(phi0, 1, axis=0)
    phi0.down   = np.roll(phi0,-1, axis=0)
    phi0.right  = np.roll(phi0, 1, axis=1)
    phi0.left   = np.roll(phi0,-1, axis=1)
    phi0.sharedmask            
    phi0.left.sharedmask         #check
    phi0.up.sharedmask

    #masking the four edges
    for v in [phi0.up, phi0.down, phi0.left, phi0.right]:
        v.mask[ :, 0]   = True
        v.mask[ :,-1]   = True
        v.mask[ 0, :]   = True
        v.mask[-1, :]   = True    

    phi0.sharedmask            
    phi0.left.sharedmask         #check
    phi0.up.sharedmask
     
    phi0.up
    phi0.left

    #########################################################################
    # CENTRAL DIFFERENCE SCHEME

    # preparing for the regression:  defining the X and Y
    # advection equation:  
    #  phi1-phi0 = -dt [ (u,v). ((phidown-phiup)/2dI, (phileft-phiright)/2dJ) - q]
    # shiiba assumption:  u = c1*I+c2*J+c3, v=c4*I+c5*J+c6, q=c7*I+c8*J+c9
    #  for simplicity we let dt=dI=dJ=1


    print "\n=================================\nCentral difference scheme"
    #xxx= raw_input('press enter:')


    height, width = phi0.shape
    X, Y = np.meshgrid(range(width), range(height))
    I, J = Y, X

    I = I.view(ma.MaskedArray)
    J = J.view(ma.MaskedArray)
    I.mask = None
    J.mask = None

    imageList = [phi0, phi1, phi0.up, phi0.down, phi0.left, phi0.right, I, J]
    mask = phi0.mask


    #
    # get the union of masks...
    #

    for v in imageList:
        mask += v.mask

    # ... and share it
    for v in imageList:
        v.mask = mask

    phi0, phi1, phi0.up, phi0.down, phi0.left, phi0.right, I, J


    #
    #  
    ######################################################################

    #################################################################################
    #
    # and compress the data into one dim before we do further computation.
    # the two-dimensional structure is no longer needed.
    #
    phi0.sharedmask  # check
    phi1.sharedmask

    phi         =phi0.compressed()		# compressing phi0 into 1-dimensional phi
    phi_next    =phi1.compressed()		# same
    phiup       =phi0.up.compressed() 
    phidown     =phi0.down.compressed()
    phileft     =phi0.left.compressed()
    phiright    =phi0.right.compressed()
    I = I.compressed()
    J = J.compressed()

    xxx = np.vstack([phi, phi_next, phiup, phidown, phileft, phiright, I, J])   #test
    xxx[:,:10]
    xxx[:,10:20]
    xxx[:,20:]

    regressand = phi_next - phi
    A = -(phidown-phiup)/2
    B = -(phileft-phiright)/2
    regressor = np.zeros((9, len(regressand)))  # c1; c2; ... c9  one row for each coeff

    regressor[0,:] = A*I
    regressor[1,:] = A*J
    regressor[2,:] = A
    regressor[3,:] = B*I
    regressor[4,:] = B*J
    regressor[5,:] = B
    regressor[6,:] = I
    regressor[7,:] = J
    regressor[8,:] = 1

    regressor[:,:10]
    regressor[:,10:20]
    regressor[:,20:]


    C, residual, rank, s = lsq(regressor.T, regressand)
    residual = residual[0]

    SStotal = regressand.var() * len(regressand)
    Rsquared = 1 - residual/SStotal
    print "For the central difference scheme, C, Rsquared =" , C, Rsquared

    #
    # the above - central difference scheme, 22 Feb 2013
    ######################################################################

    #########################################################################
    # UPWIND SCHEME   - 23 Feb 2013

    # preparing for the regression:  defining the X and Y
    # advection equation:  
    #  phi1-phi0 = -dt [   (u,v)  . ((phidown-phiup)/2dI, (phileft-phiright)/2dJ) - q +
    #                     upWindCorrectionTerm], 
    #  where upWindCorrectionTerm 
    #            =     (|u|,|v|). ((2phi-phidown-phiup)/2dI, (2phi-phileft-phiright)/2dJ)
    #
    # shiiba assumption:  u = c1*I+c2*J+c3, v=c4*I+c5*J+c6, q=c7*I+c8*J+c9
    #  for simplicity we let dt=dI=dJ=1


    print "\n=================================\nupWInd scheme"
    #xxx= raw_input('press enter:')


    ###############################
    # upWind scheme parameters
    convergenceMark = 0.000000001

    C_ =  np.arange(9)*999      #just some random initialisation
    loopCount = 0
    while abs(C_-C).sum() > convergenceMark:
        loopCount +=1
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = C    
        C_ = C                      # keeping the old C
        U0 = c1*I + c2*J + c3
        V0 = c4*I + c5*J + c6
        # q  = c7*I + c8*J + c9   # just in case it's needed
        # In the following, dI=dJ=dt = 1 for simplicity    
        upWindCorrectionTerm = abs(U0)*(2*phi-phidown-phiup)/2 + abs(V0)*(2*phi-phileft-phiright)/2
        regressand = phi_next - phi + upWindCorrectionTerm
        # regressor unchanged - see equation (4.3) on p.32, annual report, december 2012
        C, residual, rank, s = lsq(regressor.T, regressand)
        residual = residual[0]
        SStotal = regressand.var() * len(regressand)
        Rsquared = 1 - residual/SStotal
        print "\n-------------------------------\n"
        print "Loop:", loopCount
        print "abs(C_-C).sum():", abs(C_-C).sum()
        print "Rsquared:", Rsquared
        print "shiiba coeffs:", C
        #print "upWindCorrectionTerm: (", len(upWindCorrectionTerm), ")",upWindCorrectionTerm, 

    ##################################
    # Shiiba regression results
    print "\n\n\n=============== Shiiba regression results for", a.name, "and", b.name
    print "Rsquared = ", Rsquared
    print "C = ", C
    return C, Rsquared


def interpolate(C, a):

    #####################################
    # interpolation
    scalar1 = regression.convert2(C, a)
    scalar1.name = "source term for" + a.name + "and" + b.name
    scalar1.show2()
    scalar1.show3()
    vect1   = regression.convert(C, a)
    vect1.show()
    tic()
    a1  = sl.interpolate2(a, vect1)
    toc()
    a1.show()
    return a1, vect1, scalar1

def corr(a,b):
    phi0 = a.matrix.flatten()
    phi1 = b.matrix.flatten()
    return ma.corrcoef(phi0,phi1)

def main(a, b):
    C, Rsquared = regress(a, b)
    a1, vect1, scalar1 = interpolate(C,a)
    diff    = b-a1
    diff.cmap = 'hsv'
    diff.show()
    corr_a_b    = corr(a,b)
    corr_a1_b   = corr(a1,b)
    print diff.matrix.max()
    print diff.matrix.min()
    print diff.matrix.mean()
    print diff.matrix.var()
    
    return {'a1':a1, 'vect1':vect1, 'scalar1':scalar1, 'C':C, 'Rsquared':Rsquared,
            'corr_a_b':corr_a_b, 'corr_a1_b': corr_a1_b}

if __name__ == "__main__":
    a = dbz('20120612.0200')
    b = dbz('20120612.0210')

    a.load()
    b.load()

    main()
    
"""
