import numpy as np
import csv
import matplotlib.pyplot as pyplot

#Conditional Debugging
debug = False

# nnCount		= 7 # Number of neural networks
# dfCount		= 3 # Number of dataflows
# rtCycles	= np.zeros((dfCount, nnCount)) # Array of runtime cycles for each execution.
scaleFac 	= 10**6 # scaling factor

adList	= [[8,8], [16,16], [32,32], [64,64], [128,128]] #list of systolic array dimensions
dfList	= ["os", "ws", "is"]
nnList 	= ["AlphaGoZero", "DeepSpeech2", "FasterRCNN", "NCF_recommendation", "Resnet50", "Sentimental_seqCNN", "Transformer"]
layerCount	= [8, 6, 46, 8, 54, 4, 891]
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

def gBarGraph(rtCycles=np.zeros([1,1,1]),
				xLabel=['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7'],
				figName='outputs/figures/cycles.png',
				debug=False):
	rtcShape = rtCycles.shape
	barWidth = 0.25
	barColor = ['#4F81BD', '#9F4C7C', '#9BBB59']
	fig, axes = pyplot.subplots(1,rtcShape[0], figsize=(rtcShape[0]*3+1,3))
	sfLable = [chr(alph) for alph in range(ord('a'),ord('a')+rtcShape[0])]
	x = np.arange(nnCount)
	for spIndex in range(rtcShape[0]) :
		for i in range(rtcShape[1]) :
			axes[spIndex].bar(x+i*barWidth, rtCycles[spIndex][i], color =barColor[i], width = barWidth, zorder=3)

		axes[spIndex].grid(True, axis='y', zorder=0)
		# axes[spIndex].set_title('Cycles for array of size 128*128')
		axes[spIndex].set_xlabel(sfLable[spIndex])
		# axes[spIndex].set_ylabel('Runtime in million cycles')
		axes[spIndex].set_xticks([x1+barWidth for x1 in x])
		axes[spIndex].set_xticklabels(xLabel)
	axes[0].set_ylabel('Runtime in million cycles')
	pyplot.legend(labels = dfList, loc = (1,0.7))
	pyplot.tight_layout()
	pyplot.savefig(figName, transparent = True, format='png', orientation = 'landscape', dpi=300)
	if debug:
		pyplot.show()

gBarGraph(rtCycles, xLabel, figName)