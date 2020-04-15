import numpy as np
import csv

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

ad 		= 128
dfIndex	= 0 # Index for dataflow loop
nnIndex	= 0 # Index for NN loop

rootFolder	= 'outputs/output_summary/'
typeOfData	= "cycles" # e.x. cycles, bandwidth etc.
for dfIndex, df in enumerate(dfList) :
	for nnIndex, nn in enumerate(nnList) :
		runFolder	= nn + "_" + str(ad) + "_" + df + "/"
		fileName = rootFolder +  runFolder + "outputs/" + runFolder + nn + "_" + typeOfData + ".csv"
		if (debug) :
			print(f'File Name\t: {fileName}')
		#File Parsing and data Processing
		#fileName	= 'outputs/output_summary/AlphaGoZero_128_is/outputs/AlphaGoZero_128_is/AlphaGoZero_cycles.csv'
		with open(fileName, mode = 'r') as file :
			fileContent	= csv.DictReader(file)
			lineCount	= 0
			totalCycles	= 0

			# if debug :
			# 	print(f'fileContent dataType\t: {type(fileContent)}')

			for line in fileContent:
				if (lineCount == 0) :
					if (debug) :
						print('Reading CSV file')
					lineCount += 1 #Added due to dictReader

				totalCycles	+= int(line["	Cycles"])
				lineCount	+= 1
			if (lineCount == 0) :
				mdfList.append(fileName)
			if (debug) :
				print(f'Total Cycles\t: {totalCycles}')
				print(f'Lines read\t: {lineCount}')
			rtCycles[dfIndex][nnIndex] = totalCycles/scaleFac
		if debug:
			print(f'rtCycles[{dfIndex}][{nnIndex}]\t: {rtCycles[dfIndex][nnIndex]}')
print(f'{rtCycles}')
print(f'{mdfList}')
