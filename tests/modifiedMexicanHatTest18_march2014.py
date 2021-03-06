#   modifiedMexicanHatTest18.py
#   two 3d charts in one

"""
1.  load xyz1   for compref(radar)
2.  load xyz2   for wrf
3.  fix xyz2
4.  charting 2 in one
"""
inputFolder='/media/TOSHIBA EXT/ARMOR/labLogs/2014-5-26-modifiedMexicanHatTest17_Numerical_Spectrum_for_Typhoon_Kong-Rey_RADAR/'
dataSource  = "Numerical_Spectrum_for_Typhoon_Kong-Rey_RADAR"
i=121

import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

xyz  = pickle.load(open(inputFolder+'XYZ.pydump','r'))
X   = xyz['X']
Y   = xyz['Y']
Z   = xyz['Z']

plt.close()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X, np.log2(Y), np.log2(Z), rstride=1, cstride=1)  #key line
plt.title(dataSource+ " " + str(i) + "DBZ images\n"+\
          "x-axis:  response intensity(from 0 to 20)\n"+\
          "y-axis:  log_2(sigma)\n"+\
          "z-axis:  log_2(count)\n")
plt.xlabel('response intensity')
plt.ylabel('log2(sigma)')
fig.show()

xyz1    = xyz
dataSource1 = dataSource
i1=i
#################################################################################

inputFolder='/media/TOSHIBA EXT/ARMOR/labLogs/2014-5-16-modifiedMexicanHatTest15_march2014/'
dataSource= "Numerical_Spectrum_for_Typhoon_Kong-Rey_march2014_sigmaPreprocessing10"
i=399

xyz  = pickle.load(open(inputFolder+'XYZ.pydump','r'))
X   = xyz['X']
Y   = xyz['Y']
Z   = xyz['Z']

plt.close()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X, np.log2(Y), np.log2(Z), rstride=1, cstride=1)  #key line
plt.title(dataSource+ " " + str(i) + "DBZ images\n"+\
          "x-axis:  response intensity(from 0 to 20)\n"+\
          "y-axis:  log_2(sigma)\n"+\
          "z-axis:  log_2(count)\n")
plt.xlabel('response intensity')
plt.ylabel('log2(sigma)')
fig.show()

xyz2=xyz
dataSource2 = dataSource
i2=i
##############################################################################

xyz2['X']  +=2  #in log2 scale
xyz2['Z']  +=2

plt.close()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
X   = xyz1['X']
Y   = xyz1['Y']
Z   = xyz1['Z']/121.
Z1  = Z
ax.plot_wireframe(X, np.log2(Y), np.log2(Z), rstride=1, cstride=1)  #key line
X   = xyz2['X']
Y   = xyz2['Y']
Z   = xyz2['Z']/399.
Z2  = Z
ax.plot_wireframe(X, np.log2(Y), np.log2(Z), rstride=1, cstride=1, colors="green")  #key line

ax.plot_wireframe(X, np.log2(Y), (np.log2(Z1)-np.log2(Z2))*1, rstride=1, cstride=1, colors="red")  #key line

plt.title("Blue: Averaged "+dataSource1+ " " + str(i1) + "DBZ images\n"+\
          "Green: Averaged "+dataSource2+ " " + str(i2) + "DBZ images\n"+\
          "Red:  1 x Difference of Blue and Green"
          "y-axis:  log_2(sigma)\n"+\
          "z-axis:  log_2(count)\n")
plt.xlabel('response intensity')
plt.ylabel('log2(sigma)')
fig.show()




