from . import pattern
# import armor.pattern as pattern
import numpy as np
import numpy.ma as ma
from imp import reload
from armor.advection import semiLagrangian as sl

dbz = pattern.DBZ
vec  = pattern.VectorField
#######################################################
#  useful examples for demo
a = dbz('20120612.0200')
b = dbz('20120612.0210')
c = dbz('20120612.0300')
d = dbz('20120612.0310')

a.load()
b.load()
U=ma.ones((881,921))
V=ma.ones((881,921))
U[450:,:   ] *=-1
V[   :,:450] *=-1
vect = vec(title='sample vector field', U=U.copy(), V =V.copy(), mask=a.matrix.mask)


size = 501
crux = ma.zeros((size,size))
crux.mask = False
crux[size//2:(size+1+size//30)//2, :]=80
crux[:, size//2:(size+1+size//30)//2]=80

crux1 = dbz(matrix=crux)


def antiClockwiseUV(x=921, y=881, magnitude =0.03):
    h1 = np.matrix(np.arange(-(y-1)//2, (y+1)//2) *magnitude)
    h2 = np.matrix(np.ones(x))
    C_U = -np.kron(h1.T, h2).view(np.ndarray)
    h1 = np.matrix(np.arange(-(x-1)//2, (x+1)//2) *magnitude)
    h2 = np.matrix(np.ones(y))
    C_V =  np.kron(h2.T, h1).view(np.ndarray)
    return C_U, C_V


def antiClockwiseField(x=921, y=881, magnitude = 0.03):
    U, V = antiClockwiseUV(x=x,y=y, magnitude=magnitude)
    return vec(name='Anti-clockwise Vector Field of dimension (x=%d, y=%d)' %(x,y),\
                title='Anti-clockwise Vector Field of dimension (x=%d, y=%d)' %(x,y),\
                U=U, V=V, gridSize=max(x,y)//20+1, mask = False)


vect = antiClockwiseField(magnitude = 0.01)


C_vect = antiClockwiseField(size,size)

crux1.verbose=True

if __name__=='__main__':
    crux1.show4()
    C_vect.show()
    crux2 = sl.interpolate2(crux1, C_vect, scope = (min(size//20,20), min(size//20,20)))
    crux2.show4()


