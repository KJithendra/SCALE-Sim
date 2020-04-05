import numpy as np
import csv

#Conditional Debugging
debug = True

nnCount		= 7 # Number of neural networks
dfCount		= 3 # Number of dataflows
rtCycles	= np.zeros((dfCount, nnCount)) # Array of runtime cycles for each execution.
scaleFac 	= 10**6 # scaling factor

dfIndex	= 0 # Index for dataflow loop
nnIndex	= 0 # Index for NN loop

#File Parsing and data Processing
fileName	= 'outputs/output_summary/AlphaGoZero_128_is/outputs/AlphaGoZero_128_is/AlphaGoZero_cycles.csv'
with open(fileName, mode = 'r') as file :
	fileContent	= csv.DictReader(file)
	lineCount	= 0
	totalCycles	= 0

	for line in fileContent:
		if (lineCount == 0) :
			if (debug) :
				print('Reading CSV file')
			lineCount += 1 #Added due to dictReader

		totalCycles	+= int(line["	Cycles"])
		lineCount	+= 1
	if (debug) :
		print(f'Total Cycles\t: {totalCycles}')
		print(f'Lines read\t: {lineCount}')
	rtCycles[dfIndex][nnIndex] = totalCycles/scaleFac
if debug:
	print(f'rtCycles[{dfIndex}][{nnIndex}]\t: {rtCycles[dfIndex][nnIndex]}')
