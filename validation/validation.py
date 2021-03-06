"""
validation.py
    script for validating the codes
    and to pick ones to be submitted to the CWB for further testing

Goals
    1.  compute the scores and optimise with respect to the parameters 
        given an algorithm and a set of data
    2.  compare the scores between algorithms and with human scoring
    3.  from each algorithm compute a set of candidates of the highest ranks
        and compare that with human judgement

Procedures
    1.  compute the scores
    2.  compute the ranks
    3.  return the scores and the ranks
    4.  ask for human input
    5.  optimise the parameters
Plan
    Input:  algorithm, dss, variable parameters
    Intermediate Output: ranking
    Final Output: optimal parameters, scoring of the algorithm

    All results - either tagged as an attribute to the armor.pattern2.DSS object
                  or create a new object for it 
                  or just use a dict
                
Ideas
    1.  cross checking/benchmarking between human and machine

"""

#   imports
from armor import pattern, pattern2, misc

#   defining the class to record the outcomes
class ValidationResults:
    def __init__(self, algorithm, DSS, **kwargs):
        self.algorithm  = algorithm
        self.DSS        = DSS
        for v in kwargs:
            setattr(self, v, kwargs[v])
            
#   defining the functions
#   test run


def readData():
    pass

def writeResults():
    pass

def benchmarking():
    pass








def main():
    

