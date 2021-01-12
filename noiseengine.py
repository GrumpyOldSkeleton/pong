#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  noiseengine.py
# 
# NOTE!:
# pip3 install opensimplex 
#
# implements a simple 1D noise generator.
# 
# call next to get a perlin random in range -1..1
# call next with optional offset to get value ahead/behind the next val
# this is good for random x/y position value
# call nextMapped to get that value mapped to any range.

try:
    from opensimplex import OpenSimplex
except:
    print ('opensimplex not found.')
    print('To install opensimplex: pip3 install opensimplex')


class NoiseEngine1D():
    
    def __init__(self, seed=1):
        
        self.engine = OpenSimplex(seed)
        self.smoothness = 20
        self.x = 1
        
    def maprange(self, a, b, val):
        
        # map val from range a to range b
        (a1, a2), (b1, b2) = a, b
        return  b1 + ((val - a1) * (b2 - b1) / (a2 - a1))
        
    def next(self, offset=0):
        
        # return next value of noise
        self.x += 1
        return self.engine.noise2d(1, (self.x + offset) / self.smoothness)
        
    def nextMapped(self, mn, mx, offset=0):
        
        n = self.next(offset)
        return self.maprange((-1,1),(mn,mx),n)
        
    




        
