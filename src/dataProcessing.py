import numpy as np
import csv
import matplotlib.pyplot as pyplot
from gBarGraph import *

# Conditional Debugging
debug = False

# Inputs
scaleFac 	= 10**6 # scaling factor
adList	= [[128,128], [64,64], [32,32], [16,16], [8,8]] #list of systolic array dimensions
dfList	= ["os", "ws", "is"]
nnList 	= ["AlphaGoZero", "DeepSpeech2", "FasterRCNN", "NCF_recommendation_short", "Resnet50", "Sentimental_seqCNN", "Transformer_short"]
layerCount	= [8, 6, 46, 8, 54, 4, 9]
typeOfData	= "cycles" # e.x. cycles, bandwidth etc.
xLabel = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']

rootFolder	= 'outputs/scaleOut_output_summary/'
figName = 'outputs/figures/scaleOut_cycles.png'

# Generate sum of all layers of each run
rtCycles, mdfList = sum_gen(adList=adList, dfList=dfList, nnList=nnList, \
							layerCount=layerCount, rootFolder=rootFolder, \
							typeOfData=typeOfData, scaleFac=scaleFac,  debug=debug)
# Generate grouped bar Plot
gBarGraph(rtCycles=rtCycles, xLabel=xLabel, figName=figName, \
			dfList=dfList, debug=debug)

with open('outputs/missingDataFileList.txt', mode='w') as msFile :
	msFile.writelines('%s\n' % element for element in mdfList)

