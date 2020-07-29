# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 16:03:23 2020
"""

import pickle 
import matplotlib.pyplot as plt
from utilities import spk2rates,rasterPlot,spectrum1ch
import numpy as np

##################### LOAD ONE OF THE DATASETS ######################

dataFolder='../../data/' #or any existing folder where you want to store the output
keysLocation='../../data/dataKeys'              
dataKeys = pickle.load(open(keysLocation, "rb"))
whichDataset=0
assert(whichDataset<len(dataKeys))
filename=dataFolder+'spikeData'+dataKeys[whichDataset]+'.p'
dataDict=pickle.load(open(filename, "rb"))
spkTimes=dataDict['spk_session']

######################## CONVERT SPIKES TO RATES ##############

tMin=0
tMax=spkTimes[0][100] #tMax=spkTimes[0][-1]
rasterPlot(spkTimes,tMin,tMax)

nChannels=len(spkTimes)
splittingGap=np.empty(nChannels)

tFirst=spkTimes[0][0]
tLast=0
for ch in range(nChannels):
     tLast=max(tLast,spkTimes[ch][-1])
     tFirst=min(tFirst,spkTimes[ch][0])
     splittingGap[ch]=np.ceil(np.mean(spkTimes[ch][1:]-spkTimes[ch][:-1]))

binSize=np.mean(splittingGap) # heuristics to pick the bin size
rates=spk2rates(spkTimes,binSize)
print('bin size = '+str(binSize)+' ms')
plt.plot(rates[0][:-1])
plt.show()

################### COMPARE TRANSFORMS##########################

nBins=rates.shape[1]
width=int(nBins/10)

ch=0 #do this for the 10 channels with the most spikes

freqs1,powerSpectrum1=spectrum1ch(rates[ch][:width])
freqs2,powerSpectrum2=spectrum1ch(rates[ch][-width:])
plt.plot(freqs1,powerSpectrum1,freqs2,powerSpectrum2)
plt.xlim((0,500))
