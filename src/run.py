# Name 			: run.py
# Description	: Runs SCALE-Sim for various configurations and topologies and stores the output results.
# Author		: K Jithendra

debug = False # Make debug mode active

#Import Libraries
import os
from os import listdir
import glob # Unix style pathname  pattern expansion
import fnmatch # Unix file name pattern matching

origin_dir = ".";
# Copy all topology filenames into a list
topology_files	= []
topology_dir 	= origin_dir + "/topologies/mlperf/"
topology_dir_content 	= listdir(topology_dir)
for file in topology_dir_content:
	if fnmatch.fnmatch(file, "*.csv"):
		if (fnmatch.fnmatch(file, "*short.csv") \
			| fnmatch.fnmatch(file, "*LSTM.csv") \
			| fnmatch.fnmatch(file, "test.csv") \
			| fnmatch.fnmatch(file, "MLPERF.csv")) == False: # To avoid csv files not used in SCALE-Sim paper
			topology_files.append(file)
#topology_files = glob.glob(origin_dir + "/topologies/mlperf/*.csv")

# if debug == True :
# 	print(topology_files)


# Create config files
dataflow_list	= ["os", "ws", "is"]
array_dim_list	= [8, 16, 32, 64, 128]
config_dir		= origin_dir + "/configs/"
for file in topology_files:
	for dataflow in dataflow_list:
		for array_dim in array_dim_list:
			config_file_name = file[0:len(file)-4] + "_" + str(array_dim) + "_" + dataflow
			config_file_full_name = config_dir + config_file_name + ".cfg"
			# if debug == True :
			# 	print(config_file_name)
			config_file = open(config_file_full_name, "w")
			lines = ["[general]" + "\n",\
			"run_name = " + "\"" +config_file_name + "\"" +"\n\n",\
			"[architecture_presets]\n",\
			"ArrayHeight:    " + str(array_dim) + "\n",\
			"ArrayWidth:     " + str(array_dim) + "\n",\
			"IfmapSramSz:    512" + "\n",\
			"FilterSramSz:   512" + "\n",\
			"OfmapSramSz:    256" + "\n",\
			"IfmapOffset:    0" + "\n",\
			"FilterOffset:   10000000" + "\n",\
			"OfmapOffset:    20000000" + "\n",\
			"Dataflow:       " + dataflow + "\n"]
			config_file.writelines(lines)
			config_file.close()

# Copy all config file names
config_files		= []
config_dir_content 	= listdir(config_dir)
for file in config_dir_content:
	if fnmatch.fnmatch(file, "*.cfg"):
		if (fnmatch.fnmatch(file, "*eyeriss.cfg") \
			| fnmatch.fnmatch(file, "google.cfg") \
			| fnmatch.fnmatch(file, "scale.cfg")) == False: # To avoid csv files not used in SCALE-Sim paper
			config_files.append(file)

# if debug == True :
# 	print(config_files)

# run scale sim for different conmbinations.
# topology_files and config_files are the lists that contain names of the topology and config_files respectively.
topology_dir 	= origin_dir + "/topologies/mlperf/"
config_dir		= origin_dir + "/configs/"
run_count 		= 1
for file in topology_files:
	for dataflow in dataflow_list:
		for array_dim in array_dim_list:
			config_file_name = file[0:len(file)-4] + "_" + str(array_dim) + "_" + dataflow
			config_file_full_name = config_dir + config_file_name + ".cfg"
			topology_file_name	= origin_dir + "/topologies/mlperf/"
			topology_file_full_name	= topology_file_name + file 
			scale_sim_command = "python ./scale.py -arch_config=" + config_file_full_name + " -network=" + topology_file_full_name;
			if debug == True:
				print(scale_sim_command)
			print("INFO:: run_count:" + str(run_count))
			os.system(scale_sim_command)
			run_count = run_count +1;