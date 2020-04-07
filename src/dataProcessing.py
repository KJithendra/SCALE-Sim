import numpy as np
import csv
import matplotlib.pyplot as pyplot
from gBarGraph import gBarGraph
#Conditional Debugging
debug = False

scaleFac 	= 10**6 # scaling factor

adList	= [[128,128], [64,64], [32,32], [16,16], [8,8]] #list of systolic array dimensions
dfList	= ["os", "ws", "is"]
nnList 	= ["AlphaGoZero", "DeepSpeech2", "FasterRCNN", "NCF_recommendation", "Resnet50", "Sentimental_seqCNN", "Transformer_short"]
layerCount	= [8, 6, 46, 8, 54, 4, 9]
adCount	= len(adList)
dfCount = len(dfList)
nnCount	= len(nnList)

rtCycles	= np.zeros((adCount, dfCount, nnCount)) # Array of runtime cycles for each execution.

mdfList	= [] # List of Missing data files

rootFolder	= 'outputs/output_summary/'
typeOfData	= "cycles" # e.x. cycles, bandwidth etc.
for adIndex, ad in enumerate(adList) :
	for dfIndex, df in enumerate(dfList) :
		for nnIndex, nn in enumerate(nnList) :
			runFolder	= nn + "_" + str(ad[0]) + "_" + df + "/"
			fileName = rootFolder +  runFolder + "outputs/" + runFolder + nn + "_" + typeOfData + ".csv"
			
			# if (debug) :
			# 	print(f'File Name\t: {fileName}')
			
			#File Parsing and data Processing
			with open(fileName, mode = 'r') as file :
				fileContent	= csv.DictReader(file)
				lineCount	= 0
				totalCycles	= 0

				for line in fileContent:
					if (lineCount == 0) :
						lineCount += 1 #Added due to dictReader

					totalCycles	+= int(line["	Cycles"])
					lineCount	+= 1
				if (lineCount != (layerCount[nnIndex] + 1)) :
					mdfList.append(fileName)
				if (debug) :
					print(f'Total Cycles\t: {totalCycles}')
					print(f'Lines read\t: {lineCount}')
				rtCycles[adIndex][dfIndex][nnIndex] = totalCycles/scaleFac
			if debug:
				print(f'rtCycles[{adIndex}][{dfIndex}][{nnIndex}]\t: {rtCycles[adIndex][dfIndex][nnIndex]}\n')
if debug:
	print(f'{rtCycles}')
with open('outputs/missingDataFileList.txt', mode='w') as msFile :
	msFile.writelines('%s\n' % element for element in mdfList)

xLabel = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']
figName = 'outputs/figures/cycles.png'

gBarGraph(rtCycles=rtCycles, xLabel=xLabel, figName=figName, dfList=dfList, debug=debug)