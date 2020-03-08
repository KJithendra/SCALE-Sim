# Name 			: run.py
# Description	: Runs SCALE-Sim for various configurations and topologies and stores the output results.
# Author		: K Jithendra

debug = True # Make debug mode active

#Import Libraries
from os import listdir
import glob # Unix style pathname  pattern expansion
import fnmatch # Unix file name pattern matching

# Copy all topology filenames into a list
topology_files	= []
topology_dir 	= "../topologies/mlperf/"
dir_content 	= listdir(topology_dir)
for file in dir_content:
	if fnmatch.fnmatch(file, "*.csv"):
		if (fnmatch.fnmatch(file, "*short.csv") \
			| fnmatch.fnmatch(file, "*LSTM.csv") \
			| fnmatch.fnmatch(file, "test.csv") \
			| fnmatch.fnmatch(file, "MLPERF.csv")) == False: # To avoid csv files not used in SCALE-Sim paper
			topology_files.append(file)
#topology_files = glob.glob("../topologies/mlperf/*.csv")

if debug == True :
	print(topology_files)


# Create config files
dataflow_list	= ["os", "ws", "is"]
array_dim_list	= [8, 16, 32, 64, 128]
for file in topology_files:
	for dataflow in dataflow_list:
		for array_dim in array_dim_list:
			config_file_name = file[0:len(file)-4] + "_" + str(array_dim) + "_" + dataflow + ".cfg"
			if debug == True :
				print(config_file_name)
			#config_file = open(config_file_name, "w")

