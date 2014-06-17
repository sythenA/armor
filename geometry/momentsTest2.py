import numpy as np
from armor import pattern
dbz = pattern.DBZ
a=dbz('20120612.0500')
a.load()
a.invar = a.invariantMoments()

results = []
for i in range(500, 800, 100):
    for j in range(0, 60, 10):
        print '\n................\n', i+j
        b = dbz('20120612.0%d'% (i+j))
        b.load()
        b.invar = b.invariantMoments()
        invarcorr    = np.corrcoef(a.invar, b.invar)[0,1]
        abcorr  = a.corr(b)[0,1]
        abdiff  = (a-b).matrix.sum()
        new_entry = {'name':b.name, 'invar':b.invar, 'invarcorr_with_a':invarcorr,
                        'abcorr':abcorr, 'abdiff':abdiff}
        print new_entry
        results.append(new_entry)



print '\n'.join( [str((v['name'], v['abcorr'], v['invarcorr_with_a'])) for v in results])

"""
>>> 
>>> print '\n'.join( [str((v['name'], v['abcorr'], v['invarcorr_with_a'])) for v in results])
('DBZ20120612.0500', 0.99999999999998357, 1.0)
('DBZ20120612.0510', 0.79027634220815035, 0.85896113414835562)
('DBZ20120612.0520', 0.65423439305159403, 0.84669831814122321)
('DBZ20120612.0530', 0.55863557204947378, 0.46526608468438641)
('DBZ20120612.0540', 0.51510627814769538, 0.45697332708811161)
('DBZ20120612.0550', 0.4846975577159281, 0.44356715004335795)
('DBZ20120612.0600', 0.45799322106919887, 0.53414554480197829)
('DBZ20120612.0610', 0.4441205386403172, 0.52312639491953572)
('DBZ20120612.0620', 0.42473678843533896, 0.53180241511776905)
('DBZ20120612.0630', 0.39456372334815559, 0.51291554878787038)
('DBZ20120612.0640', 0.38424143368383962, 0.5137104876081432)
('DBZ20120612.0650', 0.33020619421176139, 0.5097828913559842)
('DBZ20120612.0700', 0.29919791341683716, 0.49754509399539237)
('DBZ20120612.0710', 0.27827822938372304, 0.40966929612206548)
('DBZ20120612.0720', 0.26840515822728328, 0.40770789303925231)
('DBZ20120612.0730', 0.24619789822633639, 0.72923977223300163)
('DBZ20120612.0740', 0.22659310301784066, 0.36479258118205626)
('DBZ20120612.0750', 0.20220838367981797, 0.34227385176930225)
>>> 



"""
