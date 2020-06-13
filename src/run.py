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

if scaleOut:
	array_dim_list = [[8,8], [16,16], [32,32], [64,64], [128,128]]
	

def main(argv):
	'''
	Generate config files
	'''
	origin_dir = "."
	config_dir = origin_dir + "/configs/scale_up_rectangle_SA/"

	dataflow_list = ["os", "ws", "is"]

	array_dim_list=[]
	array_dim_list	= [[8,2048], [16,1024], [32,512], [64,256], [128,128], \
						[256,64], [512,32], [1024,16], [2048,8]]

	div_base = 1

	## config gen function calling
	parallel_runs.gen_config_files_single_SA(dataflow_list=dataflow_list,
							array_dim_list=array_dim_list,
							config_dir=config_dir,
							div_base=div_base)


	'''
	Run parallel SCALE-Sim runs
	'''
	origin_dir = "./"
	topology_dir 	= origin_dir + "/topologies/mlperf/"
	config_dir = origin_dir + "/configs/scale_up_rectangle_SA/"
	output_dir = 'outputs/scale_up_rectangle_SA/'
	max_parallel_processes = min((os.cpu_count()- 2),30)  # Maximum number of Parallel processes
	# Copy all config file names
	config_files_list = []
	config_dir_content = listdir(config_dir)
	config_files_list = [(config_dir + "/./" + x) for x in config_dir_content]

	# Copy all topology file names
	topology_files	= ["AlphaGoZero.csv", "DeepSpeech2.csv",\
						"FasterRCNN.csv", "NCF_recommendation_short.csv",\
						"Resnet50.csv", "Sentimental_seqCNN.csv",\
						"Transformer_short.csv"]

	toplogy_file_list = [(topology_dir + "/./" + x) for x in topology_files]

	print(config_dir_content)
	parallel_runs.parallel_runs(config_files_list=config_files_list,\
								topology_files_list=toplogy_file_list,\
								output_dir=output_dir,\
								max_parallel_runs=max_parallel_processes)
if __name__ == "__main__":
	app.run(main)