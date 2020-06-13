# Name 			: run.py
# Description	: Runs SCALE-Sim for various configurations and topologies and stores the output results.
# Author		: K Jithendra

#Import Libraries
import os
from os import listdir
import glob # Unix style pathname  pattern expansion
import fnmatch # Unix file name pattern matching
import subprocess
import time
from absl import app

import parallel_runs as parallel_runs

'''
'''

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