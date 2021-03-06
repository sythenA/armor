# armor/shiiba/regression2.py
# adapted from regression.py
# see regression.py for further remarks
# with a change: c1,.., c6 -> c1,..,c9
# 19 February 2013.

# to calculate the advection coefficiations after Shi-iba et al
# Takasao T. and Shiiba M. 1984:  Development of techniques for on-line forecasting of rainfall and flood runoff (Natural Disaster Science 6, 83)
# with upwind scheme etc

###################################################################
#   imports

import numpy as np
import numpy.ma as ma
from .. import pattern
import copy
################################################################
#   the functions

def centralDifference(phi0, phi1):

    """
    adapted from shiiba.py, internalising the parameters into the objects
    dt, dx, dy comes from the latter dbz image phi1
    25 January 2013, Yau Kwan Kiu.
        ----
    to compute the advection coefficients via the central difference scheme
    as a step to the shiiba method
    use numpy.linalg.lstsq for linear regression:  
        http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html

    We shall use the C/python convention for coordinate axes, but with the first axis going up,
    following the convention of the Central Weather Bureau and matplotlib (meshgrid) usage

    first axis
    ^
    |
    |
    + ----> second axis

    input:  phi0,phi1   - two armor.pattern.DBZ objects (wrapping a masked array)
    output: v           - an armor.pattern.VectorField object (wrapping a pair of masked arrays)
 
    
    """
    # setting up the parameters

    dt = phi0.dt    # use the attribute of the latter DBZ image
    dj = phi0.dx    # changed from phi1.dt to phi0.dt for compatibility, 13-3-2013
    di = phi0.dy

    ####################################################
    # defining the shifted masked arrays  
    #                              [ref: http://docs.scipy.org/doc/numpy/reference/maskedarray.generic.html 
    #                                   http://docs.scipy.org/doc/numpy/reference/routines.ma.html      ]
    ########    initialise
    #   phi0_up.matrix     = np.roll(phi0.matrix,+1,axis=0)   
    #   phi0_down.matrix   = np.roll(phi0.matrix,-1,axis=0)
    #   phi0_left.matrix   = np.roll(phi0.matrix,-1,axis=1)
    #   phi0_right.matrix  = np.roll(phi0.matrix,+1,axis=1)
    ########    to set the masks
    #   phi0_up.mask[ 0,:]  = 1      #mask the first (=bottom) row
    #   phi0_down.mask[-1,:]= 1      #mask the last (=top) row
    #   phi0_left.mask[:,-1]= 1      #mask the last (=right) column
    #   phi0_right.mask[:,0]= 1      #mask the first (=left) column


    phi0_up     = phi0.shiftMatrix( 1, 0)   # a new armor.pattern.DBZ object defined via DBZ's own methods
    phi0_down   = phi0.shiftMatrix(-1, 0)          
    phi0_left   = phi0.shiftMatrix( 0,-1)
    phi0_right  = phi0.shiftMatrix( 0, 1)

    ##############################################

    # applying the advection equation
    # see ARMOR annual report (1/3), section 4.2.1, esp. eqn (4.3)

    Y = (phi1.matrix-phi0.matrix)                   # regression:  Y = X.c, where c = (c1,...,c6,..,c9) 
                                                    # (up to signs or permutations) are the unknowns

    # setting up the proper mask for regression
    Y.mask = Y.mask + phi0_up.matrix.mask   + phi0_down.matrix.mask +\
                      phi0_left.matrix.mask + phi0_right.matrix.mask    # setting up the proper mask
                                                                        # for regression

    if phi1.verbose or phi0.verbose:
        print 'sum(sum(Y.mask))=', sum(sum(Y.mask))
    X = np.zeros((phi0.matrix.shape[0], phi0.matrix.shape[1], 9))     # a 9 components for each dbz pixel 
                                                        # -> 9 vector for (c1,c2,...,c9)
                                                        # where u=c1x+c2y+c3, v=c4x+c5y+c6,
                                                        #       q=c7x+c8y+c9,  j=x, i=y, 
                                                        # therefore up to +- signs or permutations, 
                                                        # X=(A1c1, A1c2, A1c3, A2c1, A2c2, A2c3)

    # Central difference scheme: phi(i+1)-phi(i-1) / 2di, etc
    if phi1.verbose or phi0.verbose:
        print "phi0,1.matrix.shape", phi0.matrix.shape, phi1.matrix.shape #debug
    A = ma.array([-dt*(phi0_down.matrix - phi0_up.matrix)   /(2*di),\
                  -dt*(phi0_left.matrix - phi0_right.matrix)/(2*dj)])  
    A = np.transpose(A, (1,2,0))                #swap the axes:  pixel dim1, pixel dim2, internal
    A.fill_value = -999
    Bj, Bi = np.meshgrid( range(phi0.matrix.shape[1]), range(phi0.matrix.shape[0]) )       #location stuff, from the bottom left corner

                                #############################
                                #  IS THE ABOVE CORRECT???  #
                                # or should that be something like
                                # meshgrid(phi0.matrix.shape[1], phi0.matrix.shape[0]
                                # and we have transpose (1,2,0) below?
                                #############################                                
    ##################################################
    # COORDINATE TRANSFORM ADDED 13 MARCH 2013
    Bi   -= phi0.coordinateOrigin[0]
    Bj   -= phi0.coordinateOrigin[1]
    #
    ##################################################

    B = ma.array([Bi,Bj]).transpose((1,2,0))                                          # (881x921x2), (i,j, (i,j) )
    
    #[a,b] * [[x,y],[z,w]] * [c,d].T = [acx+ady+bcz+bdw];  want:  [ac, ad, bc, bd]
    # debug
    #if phi0.verbose or phi1.verbose:
    #    print '== shapes for X, A and B: =='
    #    print X.shape, A.shape, B.shape
    X[:,:,0] = A[:,:,0]*B[:,:,0]        # coeffs for c1,..,c6,..,c9 up to a permutation i,j=y,x 
                                        # which we don't care for now
    X[:,:,1] = A[:,:,0]*B[:,:,1]       
    X[:,:,2] = A[:,:,0]                 # the constant term
    X[:,:,3] = A[:,:,1]*B[:,:,0]       
    X[:,:,4] = A[:,:,1]*B[:,:,1]        
    X[:,:,5] = A[:,:,1]
    X[:,:,6] = dt *B[:,:,0]             # c.f. p.32 of the December 2012 report
    X[:,:,7] = dt *B[:,:,1]        
    X[:,:,8] = dt
    


    if phi0.verbose or phi1.verbose:
        # debug
        print "== stats for X, A and B =="
        print "X.max, X.sum() = "
        print X.max(), X.sum()
    
        print "A.max, A.sum() = "
        print A.max(), A.sum()
        print "B.max, B.sum() = "
        print B.max(), B.sum()

        print Y.shape

    Y = Y.reshape(phi0.matrix.size,1)        # convert the pixel data into a column vector    
    X = X.reshape(phi0.matrix.size,9)

    # HACK FOR numpy problem:  dealing with numpy.linalg.lstsq which sees not the mask for masked arrays
    Y1 = ma.array(Y.view(np.ndarray)*(Y.mask==False))
    X1 = ma.array(X.view(np.ndarray)*(Y.mask==False))                #yes, that's right.  X* (Y.mask==0)d
    Y1.mask = Y.mask

    C, residues, rank, s = np.linalg.lstsq(X1,Y1)
    c1,c2,c3,c4,c5,c6,c7,c8,c9 = C

    #################################################################################
    #  the following line was changed on 8 march 2013
    #SStotal = ((Y1-Y1.mean())**2).sum()   # total sum of squares 
                                        # http://en.wikipedia.org/wiki/Coefficient_of_determination
                                        # array operations respect masks
    SStotal = phi1.var() * (1-phi1.mask).sum()
    #  end the following line was  changed on 8 march 2013
    #################################################################################
                                        
    # !!!! debug !!!!
    # print "SStotal=", SStotal
    # print "sum of residues=",residues[0]
    #
    #print C.shape, X1.shape, Y1.shape
    #print [v[0] for v in C]
    #C = np.array([v[0] for v in C])
    #residue2 = ((C * X1).sum(axis=1) - Y1)**2
    #
    #print "((C * X1).sum(axis=1) - Y1)**2 = ", residue2
    #print "difference:", residue-residue2
    print "Number of points effective, total variance, sum of squared residues:"
    print (1-Y.mask).sum(), ((Y-Y.mean())**2).sum(), ((Y1-Y1.mean())**2).sum(),
    print (1-Y.mask).sum() * Y.var(), (1-Y1.mask).sum() * Y1.var(), residues
    print '\n+++++ size of window (unmasked points): ', (Y.mask==False).sum()
    R_squared = 1 - (residues[0]/SStotal)
    print "c1,..c9 = "
    print C.reshape((3,3))
    print "R_squared=", R_squared, '\n=======================================\n'
    return ([c1[0],c2[0],c3[0],c4[0],c5[0],c6[0],c7[0],c8[0],c9[0]], R_squared)

###################################################################################################

def upWind(phi0, phi1, convergenceMark = 0.00000000001):
    """ adapted to object oriented form 27-1-2013
    -----
    to compute the advection coefficients via the central difference scheme
    as a step to the shiiba method
    u(k-1) and v(k-1) are given, possibly, from previous upWind steps
    or from the central differnece scheme
    builds upon the central difference scheme
    11-1-2013
    """
    # algorithm:  1. start with the central difference scheme to obtain an initial (u0,v0)
    # 2. recursively regress for the next u(n+1), v(n+1) until convergence
    #to get the shifted arrays - copied from def centralDifference
    ###########
    dt = phi0.dt    # use the attribute phi1.dt of the latter DBZ image
    dj = phi0.dx    # or should we use phi0.dt? <-- decided on this for compatibility
                    #                               across functions -see. e.g. getPrediction()
                    #                               below
                    #                               13 march 2013
    di = phi0.dy
    verbose = phi0.verbose or phi1.verbose
    if verbose:
        print '==========================================================================='
        print 'di, dj, dt, convergenceMark =', di, dj, dt, convergenceMark
    phi0_up     = phi0.shiftMatrix( 1, 0)   # a new armor.pattern.DBZ object defined via DBZ's own methods
    phi0_down   = phi0.shiftMatrix(-1, 0)          
    phi0_left   = phi0.shiftMatrix( 0,-1)
    phi0_right  = phi0.shiftMatrix( 0, 1)

    [c1_, c2_, c3_, c4_, c5_, c6_,c7_,c8_,c9_ ], R_squared_ = centralDifference(phi0=phi0, phi1=phi1)

    if phi0.verbose and phi1.verbose:       # need to be very verbose to show pic!
        vect        = getShiibaVectorField((c1_, c2_, c3_, c4_, c5_, c6_,c7_,c8_,c9_ ),phi1)
        vect.show()

    J, I = np.meshgrid(np.arange(0,phi0.matrix.shape[1]), np.arange(0,phi0.matrix.shape[0]))
    ##################################################
    # COORDINATE TRANSFORM ADDED 13 MARCH 2013
    I   -= phi0.coordinateOrigin[0]
    J   -= phi0.coordinateOrigin[1]
    #
    ##################################################
    
    # see our ARMOR December 2012 annual report (1/3), section 4.2.1, esp. eqn (4.3)
    c1 = 9999; c2 = 9999 ;  c3=-9999 ; c4=9999 ; c5=-9999 ; c6= -9999   #initialise
    c7 = 999.9; c8= 999; c9=-999
    # perhaps I should change the following convergence criterion
    # from absolute value to component-wise-scaled correlations 
    while (c1_-c1)**2 + (c2_-c2)**2 + (c3_-c3)**2 + (c4_-c4)**2 + (c5_-c5)**2 + \
                (c6_-c6)**2 + (c7_-c7)**2 + (c8_-c8)**2 + (c9_-c9)**2 > convergenceMark:
        c1_=c1; c2_= c2; c3_=c3; c4_=c4; c5_=c5; c6_=c6; c7_=c7; c8_=c8; c9_=c9
        #debug
        #print "        print U0.shape, V0.shape, phi0.shape,  \nprint di.shape, dj.shape "
        #print U0.shape, V0.shape, phi0.shape, 
        #print di.shape, dj.shape
        U0  = c1_*I + c2_*J + c3_   # use old (c1,..c6,..,c9) to compute old U,V
        V0  = c4_*I + c5_*J + c6_   # to be used as estimates for the new U,V
        # Q0  = c7_*I + c8_*J + c9_  # not needed yet?
        upWindCorrectionTerm = abs(U0/(2*di)) * (2*phi0.matrix -phi0_down.matrix -phi0_up.matrix)  +\
                               abs(V0/(2*dj)) * (2*phi0.matrix -phi0_left.matrix -phi0_right.matrix)
        upWindCorrectionTerm = pattern.DBZ(dataTime=phi1.dataTime, matrix=upWindCorrectionTerm)

        # the following line doesn't work: takes up too much computation resource
        #upWindCorrectionTerm = abs(U0/(2*di)) * (2*phi0 -phi0_down -phi0_up)  +\
        #                       abs(V0/(2*dj)) * (2*phi0 -phi0_left -phi0_right)

        #print 'sum(upWindCorrectionTerm.mask==0)=',sum( (upWindCorrectionTerm.mask==0)) #debug
        [c1, c2, c3, c4, c5, c6, c7, c8, c9], R_squared = centralDifference(phi0=phi0 + dt *upWindCorrectionTerm,\
                                                              phi1=phi1) 
        if verbose: 
            print "\n##################################################################\n"
            print "c1, c2, c3, c4, c5, c6, c7, c8, c9: ",  c1, c2, c3, c4, c5, c6,c7,c8,c9
            print "\nR^2: ", R_squared
            print "\n##################################################################\n"
    return [c1, c2, c3, c4, c5, c6,c7,c8,c9], R_squared


def getShiibaVectorField(shiibaCoeffs, phi1, gridSize=25, name="",\
                     key="Shiiba vector field", title="UpWind Scheme"):
 
    """ plotting vector fields from shiiba coeffs
    input:  shiiba coeffs (c1,c2,c3,..,c6) for Ui=c1.I + c2.J +c3, Vj=c4.I +c5.J+c6
    and transform it via I=y, J=x, to Ux = c5.x+c4.y+c6, Vy = c2.x+c1.y+c3
    """
    # 1. setting the variables
    # 2. setting the stage
    # 3. plotting
    # 4. no need to save or print to screen

    # 1. setting the variables
    c1, c2, c3, c4, c5, c6,c7,c8,c9 = shiibaCoeffs
    c5, c4, c6, c2, c1, c3, c8,c7,c9 = c1, c2, c3, c4, c5, c6,c7,c8,c9     # x,y <- j, i switch
    # 2. setting the stage
    height= phi1.matrix.shape[0]
    width = phi1.matrix.shape[1]
    mask  = phi1.matrix.mask
    name  = "shiiba vector field for "+ phi1.name
    imagePath = phi1.name+"shiibaVectorField.png"
    key   = key
    ploTitle  = title
    gridSize = gridSize
    X, Y    = np.meshgrid(range(width), range(height))
    ##################################################
    # COORDINATE TRANSFORM ADDED 13 MARCH 2013
    Y   -= phi1.coordinateOrigin[0]     # "latitute"
    X   -= phi1.coordinateOrigin[1]     # "logtitude"
    #
    ##################################################
    Ux      = c1*X + c2*Y + c3
    Vy      = c4*X + c5*Y + c6
    Ux      = ma.array(Ux, mask=mask)
    Vy      = ma.array(Vy, mask=mask)
    #constructing the vector field object
    vect    = pattern.VectorField(Ux, Vy, name=name, imagePath=imagePath, key=key,
                                    title=title, gridSize=gridSize)
    return vect

def getShiibaSourceField(shiibaCoeffs, phi1, cmap='Spectral'):
    """returns a scalar field i.e. pattern.DBZ object
    """
    height, width = phi1.matrix.shape
    mask = phi1.matrix.mask
    if len(shiibaCoeffs) ==9:
        c1, c2,c3, c4,c5,c6,c7,c8,c9=shiibaCoeffs
    else:
        c7,c8,c9 = shiibaCoeffs

    c8, c7, c9 = c7, c8, c9     #coordinate transform, i=y, j=x
    X, Y = np.meshgrid(range(width), range(height))
    ##################################################
    # COORDINATE TRANSFORM ADDED 13 MARCH 2013
    Y   -= phi1.coordinateOrigin[0]
    X   -= phi1.coordinateOrigin[1]
    #
    ##################################################
    Q = c7*X + c8*Y + c9
    Q = ma.array(Q, mask=mask)
    return pattern.DBZ(name=phi1.name+'_shiiba_source_term', matrix=Q,
                        dataPath  =phi1.dataPath+'_shiiba_source_term.dat',
                        outputPath=phi1.dataPath+'_shiiba_source_term.dat',
                        imagePath =phi1.dataPath+'_shiiba_source_term.png',
                        cmap=cmap, verbose=phi1.verbose)

def getPrediction(shiibaCoeffs,  a, cmap='', coeffsUsed=9):
    """
    equation (4.3), p.32, Annual Report December 2012
    input:  "a",  a DBZ object
    output: "a1", the prediction, a dbz object
    """

    if cmap == '':
        cmap = a.cmap

    dt  = a.dt
    dx  = a.dx
    dy  = a.dy
    di  = dy
    dj  = dx
    a_up     = a.shiftMatrix( 1, 0)   # a new armor.pattern.DBZ object defined via DBZ's own methods
    a_down   = a.shiftMatrix(-1, 0)          
    a_left   = a.shiftMatrix( 0,-1)
    a_right  = a.shiftMatrix( 0, 1)

    height,width= a.matrix.shape

    try:
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = shiibaCoeffs   # i want 9 coeffs
        #defining the grid:
        X, Y    = np.meshgrid(range(width), range(height)) # can change here for coord transforms
                                                            # e.g. -> range(-centre, width-centre)
        ##################################################
        # COORDINATE TRANSFORM ADDED 13 MARCH 2013
        Y   -= a.coordinateOrigin[0]
        X   -= a.coordinateOrigin[1]
        #
        ##################################################
        J, I    = X, Y
        #print J, I,       #debug
        #print J.shape, I.shape, J.shape==I.shape
        # calculating the U, V and Q:
        U       = c1*I + c2*J + c3
        V       = c4*I + c5*J + c6
        Q       = c7*I + c8*J + c9
    except TypeError:
        # if fails, check if shiibaCoeffs are actually a pattern.VectorField object
        #
        U       = shiibaCoeffs.U
        V       = shiibaCoeffs.V
        Q       = 0
    
    #############
    # as before:
    upWindCorrectionTerm = abs(U/(2*di)) * (2*a.matrix -a_down.matrix -a_up.matrix)+\
                           abs(V/(2*dj)) * (2*a.matrix -a_left.matrix -a_right.matrix)
    A1                   = (a_down.matrix -a_up.matrix)    * (U/(2*dx))
    A2                   = (a_left.matrix -a_right.matrix) * (V/(2*dy))
    #Q                    = Q
    if coeffsUsed==6:
        phi_hat              = a.matrix - dt * (A1 + A2   ) - upWindCorrectionTerm
    else:
        phi_hat              = a.matrix - dt * (A1 + A2 -Q) - upWindCorrectionTerm

    a1  = pattern.DBZ(name = "shiiba prediction for " + a.name,
                     matrix   = phi_hat.copy(),
                     dt       = dt,
                     dx       = dx,
                     dy       = dy,
                    outputPath= "shiiba_prediction_for_"+a.name+"_and_dt_"+str(dt) +".txt",
                   imagePath="shiiba_prediction_for_"+a.name+"_and_dt_"+str(dt) +".txt",
               coastDataPath=a.coastDataPath,
                   database =a.database,
                   cmap     =a.cmap,
                   vmin     =a.vmin, 
                   vmax     =a.vmax, 
                   verbose  =a.verbose)
                       
    return a1
###

###    

def convert(shiibaCoeffs, phi1, gridSize=25, name="",\
                     key="Shiiba vector field", title="UpWind Scheme"):
    """alias
    """
    return getShiibaVectorField(shiibaCoeffs, phi1, gridSize, name,\
                     key, title)

def convert2(shiibaCoeffs, phi1, cmap='Spectral'):
    """alias
    """
    return getShiibaSourceField(shiibaCoeffs=shiibaCoeffs, phi1=phi1, cmap=cmap)

def showShiibaVectorField(phi0,phi1):
    shiibaCoeffs, R_squared = upWind(phi0,phi1)
    vect                    = getShiibaVectorField(shiibaCoeffs, phi0)
    vect.show()
    return shiibaCoeffs, R_squared

#def shiiba(phi0, phi1, convergenceMark = 0.00001):
#    ### a pointer for the moment
#    ###
#    return upWind(phi0, phi1, convergenceMark = 0.00001)


def shiiba(phi0, phi1):
    """alias
    """
    shiibaCoeffs, R_squared = showShiibaVectorField(phi0, phi1)
    return shiibaCoeffs, R_squared

def shiibaNonCFL(phi0, phi1, mask=None, windowHeight=5, windowWidth=5,\
                 convergenceMark=0.0000001,):
    """ to find the shiiba coeffs without the CFL condition
    plan:
    to shift and regress, minimising the average R^2     
    """ 
    #parameters
    verbose = phi0.verbose or phi1.verbose

    #0. initialise a matrix for the r^2
    #1. put the mask on phi0
    #2. roll back phi1 by (m,n);  per our convention, internal stuff we use (i,j), not (x,y); i=y, j=x

    R2s     = {}    #dict to record the R^2s
    ShiibaCoeffs = {}    #dict to record the shiiba coeffs
    if mask!=None:
        phi0.matrix.mask = mask        # put the mask on phi0

    for m in range(-(windowHeight-1)/2, (windowHeight+1)/2):
        for n in range(-(windowWidth-1)/2, (windowWidth+1)/2):
            phi1_temp = phi1.shiftMatrix(m,n)
            [c1, c2, c3, c4, c5, c6,c7,c8,c9], R2 = upWind(phi0=phi0, phi1=phi1_temp,\
                                                    convergenceMark=convergenceMark)
            R2s    [(m,n)] = R2
            ShiibaCoeffs[(m,n)] = [c1, c2, c3, c4, c5, c6,c7,c8,c9]
        if phi0.verbose and phi1.verbose:
            print "\n-++++++++++++++++++++++++++++-\n(m,n), [c1,c2,c3,c4,c5,c6,..c9], R2 = \n",\
                                                (m,n), [c1,c2,c3,c4,c5,c6,c7,c8,c9], R2

    #getting the (m,n) for max(R2)
    (m, n) = max(R2s, key=R2s.get)
    if verbose:
        print "\nfor the given mask, \nMax R2:+++++++++++++++++++++++++++-\n",\
                "(m,n), [c1,c2,c3,c4,c5,c6,..,c9], R2 = \n", (m,n), [c1,c2,c3,c4,c5,c6,c7,c8,c9], R2

    return (m,n), ShiibaCoeffs, R2s



def interpolation():
    """to interpolate after movements (translation, advection, rotation, etc)
    estimate phi1^(x,y) = sum_{s=x-1,x,x+1; t=y-1,y,y+1} H(s-x_pullback)*H(t-y_pullback)*phi0(s,t)
                        where H = weight function: H(x)=x cut-off and levelled at two ends 0,1 
                              _
                        H = _/

    """
    pass

def semiLagrangeAdvect():
    """to compute the semi-Lagrangian advection of a grid, given a velocity field
    """
    pass



















