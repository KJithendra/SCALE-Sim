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

def main(argv):
	'''
	Generate config files
	'''
	origin_dir = "."
	# Inputs
	topology_files	= []
	file = 'alexnet_short_8times.csv'
	topology_files.append(file)

	dataflow_list = ["os", "ws", "is"]

	array_dim_list=[[], []]
	array_dim_list[0] = [[16,64], [8,128], [4,256], [32,32], [256,4], [128,8], [64,16]]
	array_dim_list[1] = [[4,16], [8,8], [16,4]]

	config_dir = origin_dir + "/configs/temp2/"
	div_base = 1
	## config gen function calling
	parallel_runs.gen_config_files(		dataflow_list=dataflow_list,
							array_dim_list=array_dim_list,
							config_dir=config_dir,
							div_base=div_base)

	'''
	Run parallel SCALE-Sim runs
	'''
	origin_dir = "."
	topology_dir = origin_dir + "/topologies/conv_nets/"
	config_dir = origin_dir + "/configs/temp2/"
	output_dir = 'outputs/temp_4/'
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