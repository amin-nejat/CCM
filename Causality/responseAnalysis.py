# -*- coding: utf-8 -*-

"""
Created on Wed Jul 29 13:29:24 2020
"""

import numpy as np
import pickle
import itertools as it
import matplotlib.pyplot as plt 

def analyzeResponse(spkTimes,stimCh,pulseStarts,pulseDurations):

     """
     The 4 input arguments:
          
     spkTimes: a list containg the nChannels spike trains
     stimCh: which channel was stimulated (one number)
     stimTimes: stimes   t < S when channel stimCh was stimulated
     stimDurations: the function causality_vs_response that returns all you need to make the barplots.  
     """
     
     ## if you want to convert spkTimes to rates
     # bin Size = 10 ## or larger 
     #stim_times=np.round((np.array(spkTimes)-offset)/binSize)
     #stim_durations=np.round(np.array(stim_durations)/binSize)
     # rates_stim,offset=spk2rates(spk_stim,binSize=binSize) #output is a numpy array

     binSize=5
     preCushion=10
     postCushion=4
     postInterval=750
     preInterval=100

     nChannels=len(spkTimes)
     assert(stimCh>=1 and stimCh<=nChannels) #stimCh is the ID of the perturbed channel under the assumption that channels are numbered from one, not zero
     assert(len(pulseStarts)==len(pulseDurations))
     nEvents=len(pulseStarts)
        
     preBinEdges=np.array([-preInterval-preCushion,-preCushion])
     postBinEdges=np.arange(postCushion,postCushion+postInterval,binSize)

     n_postBins=len(postBinEdges)-1
 
     preCount=np.ma.array(np.zeros((nEvents,nChannels)),mask=False)
     preCount.mask[:,stimCh-1]=True
     
     postCounts=np.ma.array(np.zeros((n_postBins,nEvents,nChannels,)),mask=False)
     postCounts.mask[:,:,stimCh-1]=True
     
     # Also to initialize: meanPostRates, meanPreRates, postCounts, postIncrements

     for event, channel in it.product(range(nEvents),(x for x in range(nChannels) if x != stimCh-1)):
          print("event = "+str(event)+" and channel = "+str(channel))
          firstIndex=np.where(spkTimes[channel]>=pulseStarts[event]-preCushion-preInterval)[0][0]
          lastIndex=np.where(spkTimes[channel]<pulseStarts[event]+pulseDurations[event]+postCushion+postInterval)[0][-1]
          times=spkTimes[channel][firstIndex:lastIndex+1]-pulseStarts[event]

          preCount[event,channel]=np.histogram(times,preBinEdges)[0]  #pre-stimulus spike rate computed over the maximal duration used for the post-stimulus rate
          postCounts[:,event,channel]=np.histogram(times,pulseDurations[event]+postBinEdges)[0]
          
     incrementsByBin=postCounts/binSize-preCount/preInterval #summed through broadcasting 
     mean_incrByBin=np.mean(incrementsByBin,1) #statistic over events
     std_incrByBin=np.std(incrementsByBin,1)#statistic over events
     
     incrementsByLapse=np.cumsum(postCounts,0) #1
     incrementsByLapse=np.transpose(incrementsByLapse, (1, 2, 0)) #2
     incrementsByLapse=incrementsByLapse/np.cumsum(np.diff(postBinEdges)) #3
     incrementsByLapse=np.transpose(incrementsByLapse, (2,0,1)) #4     
     incrementsByLapse=incrementsByLapse-preCount/preInterval
     
     mean_incrByLapse=np.mean(incrementsByLapse,1)#statistic over events
     std_incrByLapse=np.std(incrementsByLapse,1)#statistic over events
     
     # meanPreRate=np.mean(preCount,0)/preInterval
     # meanPostRates_byBin=np.mean(postCounts,0)/binSize
     # meanPostRates_byBulk=np.cumsum(np.mean(postCounts,0),1)/binSize
     #  meanIncrements = masked array of length nChannels with mean rate increment over trials  (channel = afferent is masked)
     
     output={"stimulated_channel":stimCh,\
             "binSize":binSize,\
             "preCushion":preCushion,"postCushion":postCushion,\
             "preInterval":preInterval,"postInterval":postInterval,\
             "preBinEdges":preBinEdges,"postBinEdges":postBinEdges,\
             "mean_incrByBin":mean_incrByBin,"std_incrByBin":std_incrByBin,\
             "mean_incrByLapse":mean_incrByLapse,"std_incrByLapse":std_incrByLapse}

     return(output)

def plotResponses(output):          

     edges=responseAnalysisOutput["postBinEdges"]
     midpoints=(edges[:-1]+edges[1:])/2             

     nChannels=96
     plt.plot(midpoints,output["mean_incrByLapse"][:,0:nChannels])
     plt.xlabel("time (ms)")
     plt.ylabel("rate increment")
     
     
     efferent=0
     plt.plot(midpoints,output["mean_incrByLapse"][:,0])
     plt.title("response of channel "+str(efferent)+" to channel "+str(output["stimulated_channel"]))
     
     return()


if __name__=="__main__":

     whichDataset=2
     whichAfferentInd=0

     dataFolder='../../data/' #or any existing folder where you want to store the output
     keysLocation='../../data/dataKeys'              
     dataKeys = pickle.load(open(keysLocation, "rb"))

     assert(dataKeys[whichDataset][1]!=0)

     stim_filename=dataFolder+'spikeData'+dataKeys[whichDataset][1]+'.p'
     stimulated=pickle.load(open(stim_filename, "rb"))
     spk_stim=stimulated['spk_session']
     stim_times=np.array(stimulated['stim_times'])
     stim_durations=np.array(stimulated['stim_durations'])
     stim_chs=np.array(stimulated['stim_chan']) #warning: this gives the id of stimulated channels under the convention taht numbers channels from one, not zero 
     
     afferent=stim_chs[whichAfferentInd] #the first 
     ch_inds=np.array([i for i,x in enumerate(stim_chs) if x==afferent]).astype(np.int64)
               
     responseAnalysisOutput=analyzeResponse(spk_stim, afferent, stim_times[ch_inds],stim_durations[ch_inds])
     plotResponses(responseAnalysisOutput)          

