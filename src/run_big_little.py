# Name 			: run.py
# Description	: Runs SCALE-Sim for various configurations and topologies and stores the output results.
# Author		: K Jithendra

debug = True # Make debug mode active

#Import Libraries
import os
from os import listdir
import glob # Unix style pathname  pattern expansion
import fnmatch # Unix file name pattern matching
import subprocess
import time
from absl import app

import parallel_runs as parallel_runs

scaleOut = False
if scaleOut:
	topo_sub_folder = ['./', 'div4q/', 'div16q/', 'div64q/', 'div256q/']
	div_base = 2
else:
	topo_sub_folder = ['./', './', './', './', './', './', './', './', './']
	div_base = 1

origin_dir = ".";
topology_files	= []
type_of_run="short_model_scaling"
# Create config files
if type_of_run=="short_model":
	file = 'alexnet_short.csv'
	topology_files.extend(file)
	dataflow_list	= ["os", "ws", "is"]
	array_dim_list	= [[16,64], [8,128], [4,256], [32,32], [256,4], [128,8], [64,16]]
	second_array_dim_list =[[4,16], [8,8], [16,4]]
if type_of_run=="short_model_scaling":
	file = ['alexnet_short_8times.csv', 'alexnet_short_10times.csv', \
	'alexnet_short_6times.csv', 'alexnet_short_4times.csv', \
	'alexnet_short_1times.csv','alexnet_short_2times.csv', 'alexnet_short_12times.csv']
	topology_files.extend(file)
	dataflow_list	= ["ws"]
	array_dim_list	= [[32,32]]
	second_array_dim_list =[[16,4]]
# if scaleOut:
# 	array_dim_list	= [[8,8], [16,16], [32,32], [64,64], [128,128]]
# else:
# 	array_dim_list	= [[8,2048], [16,1024], [32,512], [64,256], [128,128], [256,64], [512,32], [1024,16], [2048,8]]
config_dir		= origin_dir + "/configs/"
for file in topology_files:
	for dataflow in dataflow_list:
		for second_ad_index, second_array_dim in enumerate(second_array_dim_list):
			for ad_index, array_dim in enumerate(array_dim_list):
				config_file_name = file[0:len(file)-4] + "_" + str(array_dim[0]) + "_" + str(array_dim[1]) + "_" + str(second_array_dim[0]) + "_" + str(second_array_dim[1]) + "_" + dataflow
				config_file_full_name = config_dir + config_file_name + ".cfg"
				# if debug == True :
				# 	print(config_file_name)
				config_file = open(config_file_full_name, "w")
				lines = ["[general]" + "\n",\
				"run_name = " + "\"" +config_file_name + "\"" +"\n\n",\
				"[architecture_presets]\n",\
				"ArrayHeight:    " + str(int(array_dim[0]/(div_base**ad_index))) + "," + str(int(second_array_dim[0]/(div_base**second_ad_index))) + "\n",\
				"ArrayWidth:     " + str(int(array_dim[1]/(div_base**ad_index))) + "," + str(int(second_array_dim[1]/(div_base**second_ad_index))) + "\n",\
				"IfmapSramSz:    512,512" + "\n",\
				"FilterSramSz:   512,512" + "\n",\
				"OfmapSramSz:    256,256" + "\n",\
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

def main(argv):
	'''
	Generate config files
	'''
	origin_dir = "."
	config_dir = origin_dir + "/configs/big_little_SA/"

	topology_files	= []
	file = 'alexnet_short_8times.csv'
	topology_files.append(file)

	dataflow_list = ["os", "ws", "is"]

	array_dim_list=[[], []]
	array_dim_list[0] = [[16,64], [8,128], [4,256], [32,32], [256,4], [128,8], [64,16]]
	array_dim_list[1] = [[4,16], [8,8], [16,4]]

	div_base = 1

	## config gen function calling
	parallel_runs.gen_config_files(dataflow_list=dataflow_list,
							array_dim_list=array_dim_list,
							config_dir=config_dir,
							div_base=div_base)


	'''
	Run parallel SCALE-Sim runs
	'''
	origin_dir = "./"
	topology_dir = origin_dir + "/topologies/conv_nets/"
	config_dir = origin_dir + "/configs/big_little_SA/"
	output_dir = 'outputs/big_little_SA_alexnet_sd_by_8_times/'
	max_parallel_processes = min((os.cpu_count()- 2),30)  # Maximum number of Parallel processes
	# Copy all config file names
	config_files_list = []
	config_dir_content = listdir(config_dir)
	config_files_list = [(config_dir + "/./" + x) for x in config_dir_content]

	# Copy all topology file names
	topology_files	= []
	file = 'alexnet_short_8times.csv'
	topology_files.append(file)
	toplogy_file_list = [(topology_dir + "/./" + x) for x in topology_files]

	parallel_runs.parallel_runs(config_files_list=config_files_list,\
								topology_files_list=toplogy_file_list,\
								output_dir=output_dir,\
								max_parallel_runs=max_parallel_processes)
if __name__ == "__main__":
	app.run(main)