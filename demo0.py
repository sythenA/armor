#   sample script

from armor import pattern

a = pattern.DBZ('20120612.0200')
b = pattern.DBZ('20120612.0210')

a.load()
a.show()
a.backupMatrix()
a.showWithCoast()
a.restoreMatrix()

b.load()
b.show()

a.cov(b)
a.corr(b)
x=a.shiiba(b, searchWindowWidth=5, searchWindowHeight=3)
x.keys()

mn=x['mn']
vect= x['vect']
vect.show()

vect2 = vect+mn
vect2.show()


