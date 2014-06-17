"""
   reference:  
        http://pythoncodeblog.blogspot.tw/2011/06/python-read-binary-file.html
        /media/TOSHIBA EXT/ARMOR/data/readbin.f
        /home/k/ARMOR/binaryFiles/
"""
##  test 1
import time
time0   = time.time()
ifile   = "/media/TOSHIBA EXT/ARMOR/data/COMPREF/20130709/compref_mosaic/COMPREF.20130709.0000"
fp = open(ifile,"rb")
x   = []
for count in range(162300):
    #try:
        x.append(fp.read(10))
    #except:
    #    pass
#byte = fp.read(1)
#block = fp.read(30)
#(Year,) = struct.unpack('b',block[3:4])
fp.close()
time1   = time.time()
print x[:20]

print "time spent (seconds):", time1-time0

############################################################################

print "sleeping 2 seconds"
time.sleep(2)

##  test 2
##  http://stackoverflow.com/questions/8710456/reading-a-binary-file-with-python

import struct
import time
entryLength = 20
time0   = time.time()
ifile   = "/media/TOSHIBA EXT/ARMOR/data/COMPREF/20130709/compref_mosaic/COMPREF.20130709.0000"
fp  = open(ifile, "rb")
x   = fp.read()
y   = []
fp.close()
for i in range(162300/entryLength):
    y.append(struct.unpack("i"*(entryLength/4), x[i: i+entryLength]))

time1   = time.time()
print "time spent (seconds):", time1-time0
y[:100]

##  test 3 
#   from dr. feng

import struct
#fileD = open('RADARCV/COMPREF.20140501.1200.0p03.bin','rb')
#fileD = open('/media/TOSHIBA EXT/ARMOR/data/COMPREF/20130709/compref_mosaic/COMPREF.20130709.0000','rb')
fileD=open("/media/TOSHIBA EXT/ARMOR/data/1may2014/RADARCV/COMPREF.20140501.1200.0p03.bin",'rb')
i=1
data   = []
while i < 201:
    dataV = struct.unpack("!183f", fileD.read(4*183))
    data.append(dataV)
    # raw_input()
    i=i+1
fileD.close()
print data[100][:400]

