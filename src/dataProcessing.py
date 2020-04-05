import numpy as np
import csv
import matplotlib.pyplot as pyplot

#Conditional Debugging
debug = False

nnCount		= 7 # Number of neural networks
dfCount		= 3 # Number of dataflows
rtCycles	= np.zeros((dfCount, nnCount)) # Array of runtime cycles for each execution.
scaleFac 	= 10**6 # scaling factor

adList	= [[8,8], [16,16], [32,32], [64,64], [128,128]] #list of systolic array dimensions
dfList	= ["os", "ws", "is"]
nnList 	= ["AlphaGoZero", "DeepSpeech2", "FasterRCNN", "NCF_recommendation", "Resnet50", "Sentimental_seqCNN", "Transformer"]
mdfList	= [] # List of Missing data files
layerCount	= [8, 6, 46, 8, 54, 4, 891]

ad 		= 128
dfIndex	= 0 # Index for dataflow loop
nnIndex	= 0 # Index for NN loop

rootFolder	= 'outputs/output_summary/'
typeOfData	= "cycles" # e.x. cycles, bandwidth etc.
for dfIndex, df in enumerate(dfList) :
	for nnIndex, nn in enumerate(nnList) :
		runFolder	= nn + "_" + str(ad) + "_" + df + "/"
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
			rtCycles[dfIndex][nnIndex] = totalCycles/scaleFac
		if debug:
			print(f'rtCycles[{dfIndex}][{nnIndex}]\t: {rtCycles[dfIndex][nnIndex]}\n')
if debug:
	print(f'{rtCycles}')
with open('outputs/missingDataFileList.txt', mode='w') as msFile :
	msFile.writelines('%s\n' % element for element in mdfList)
#print(f'{mdfList}')

xLabel	= ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']
x 		= np.arange(nnCount)
fig 	= pyplot.axes()
axes	= fig#fig.add_axes([0,0,1,1])
barWidth= 0.25
barColor= ['#4F81BD', '#9F4C7C', '#9BBB59']

for i in range(dfCount) :
	axes.bar(x+i*barWidth, rtCycles[i], color =barColor[i], width = barWidth, zorder=3)

axes.grid(True, axis='y', zorder=0)
axes.set_title('Cycles for array of size 128*128')
axes.set_xlabel('Workload')
axes.set_ylabel('Runtime in million cycles')
axes.set_xticks([x1+barWidth for x1 in x])
axes.set_xticklabels(xLabel)
axes.legend(labels = dfList)
figName = 'outputs/figures/cycles.png'
pyplot.savefig(figName, transparent =True, format='png')
if debug:
	pyplot.show()