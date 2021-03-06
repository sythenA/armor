# -*- coding: utf-8 -*-
#   codes for the report 
#   /media/KINGSTON/ARMOR/labReports/normalised_correlation_test2013-11-15
"""
[ARMOR] Normalised correlation 比對結果分析
Yau Kwan Kiu
2013-11-15
1. 各種 thresholds
2. 取 threshold 與取 volume 之結果之差比較
3. KONG-REY： MODEL 與 OBSERVATIONS之分析比較
4. 由大尺度開始挑選最相似的，再進入小尺度
5. 各階段 image normalisation, 有無平移
6. 九宮格
7. 時間軸上移動（plotting the centroid only）
"""

#   use 2 samples:  kongrey Observation and kongrey WRF

#   load the relevant objects
from armor import pattern
from armor import objects3

reload(pattern)
reload(objects3)
ob  = objects3
kongrey = ob.kongrey
kongreywrf  = ob.kongreywrf2
kongreywrf.fix()
wrf=kongreywrf

#   find of 20130828.0600 in kongrey
l   = len(kongrey)
r   = [r for r in range(l) if kongrey[r]==kongrey('20130828.0600')[0]][0]

k   = kongrey[r]
k.load()
k.setThreshold(0)
k.getCentroid()
k.shortTermTrajectory(kongrey)

#########################################################################
from armor import pattern
from armor import objects3
reload(pattern)
reload(objects3)
ob  = objects3
kongreywrf  = ob.kongreywrf2
kongreywrf.fix()
wrf=kongreywrf
l=len(wrf)
r   = [r for r in range(l) if wrf[r]==wrf('20130828.0600')[0]][0]
w   = wrf[r]
w.load()
w.setThreshold(0)
w.getCentroid()
w.shortTermTrajectory(wrf, key1='WRF01', timeInterval=3)

from armor.tests import roughwork20131106 as rw
reload(rw)  ; rw.testB('/home/k/ARMOR/documents/2013-final-report/testA1384023968from20130828.0800to20130828.0900.pydump')

rw.testB()









