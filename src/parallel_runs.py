# Name: parallel_runs.py
# Author: K Jithendra
# Description: 	1. Run multiple SCALE-Sim commands parellelly. 


# Import libraries
import os
from os import listdir
from absl import app
import time
import subprocess

# Executing Paralle scale.py runs
def parallel_runs(	config_files_list=[],
					topology_files_list=[],
					output_dir='./outputs/parallel_runs/',
					max_parallel_runs = 3):
	r'''
	Executes multiple SCALE-Sim commands parallely in multiple threads

	Args:
		config_files_list: List of all config files(along with directory path) for which SCALE-Sim needs to be executed.
		topology_files_list: List of all topoly files(along with directory path) for which SCALE-Sim needs to be executed.
		output_dir: The Directory path where all the SCALE-Sim runs needs to be stored.
		max_parallel_runs: Maximum number of parallel SCALE-Sim runs to be executed
	Examples:
		parallel_runs(	config_files_list=['list','of','config_files'],\
						topology_files_list=['list','of','topology_files'],\
						output_dir='full_name_of_output_folder',\
						max_parallel_runs= 2)

	'''
	run_count = 1
	processes = set() # Parallel processes
	for topology_file in topology_files_list:
		for config_file in config_files_list:
			top_dir ="../../../"
			arch_config = "-arch_config=" + top_dir + config_file
			arch_network = "-network=" + top_dir + topology_file
			scale_sim_command = ["python", top_dir+"scale.py", arch_config, arch_network]
			print("INFO:: run_count:" + str(run_count))

			topology_file_name = topology_file.split('/')[-1][:-4]
			config_file_name = config_file.split('/')[-1][:-4]

			config_file_name = topology_file_name + "_" + config_file_name
			output_file_dir = output_dir + "/./" + config_file_name
			if not os.path.exists(output_file_dir):
				os.system("mkdir -p " + output_file_dir)
			else:
				t = time.time()
				new_output_file_dir= output_file_dir + "_" + str(t)
				os.system("mv " + output_file_dir + " " + new_output_file_dir)
				os.system("mkdir " + output_file_dir)
			os.system("cd " + output_file_dir)
			std_out_file = open(output_file_dir + '/' + config_file_name +'.txt', mode='w+')
			# print(scale_sim_command)
			processes.add(subprocess.Popen(scale_sim_command, cwd=output_file_dir, stdout=std_out_file))
			std_out_file.close()
			if(len(processes) >= max_parallel_runs):
				os.wait()
				processes.difference_update([\
					p for p in processes if p.poll() is not None])
			os.system("cd ../../../")

			run_count = run_count +1;
	for p in processes:
		if p.poll() is None:
			p.wait()

def gen_config_files(   dataflow_list=[],\
						array_dim_list=[[],[]],\
						config_dir='',\
						div_base=1 ):
	r'''
	Generates config_files for all combinations of the values in the list parameters for bigLittle Systollic Array(SA)

	Args:
		dataflow_list: List of all dataflows. Possible entries-'os', 'ws' and 'is'
		array_dim_list: List of 2 lists(first for big Array and the second for little SA). Each list consists more lists, each with height and width of systolic array as its elements
		config_dir: The directory path where config files need to be stored
		div_base: Used for imply the effect of Scale-out opeartion. Array dimensions are scaled down by a factor of (div_base^x)
			1. div_base = 1 for scale-Up
			2. div_base = 2 for scale-Out	
	Examples:
		>>> gen_config_files(dataflow_list=['os','is'],\
						array_dim_list=[[[16,16],[32,16]],[[8,8],[16,4]]],\
						config_dir='output_directory',\
						div_base=1 )

	'''
	if not os.path.exists(config_dir):
		os.system("mkdir -p " + config_dir)
	for dataflow in dataflow_list:
		for second_ad_index, second_array_dim in enumerate(array_dim_list[1]):
			for ad_index, array_dim in enumerate(array_dim_list[0]):
				config_file_name = str(array_dim[0])\
					+ "_" + str(array_dim[1]) + "_" + str(second_array_dim[0])\
					+ "_" + str(second_array_dim[1]) + "_" + dataflow
				config_file_full_name = config_dir + '/./'+ config_file_name + ".cfg"
				# if debug == True :
				# 	print(config_file_name)
				config_file = open(config_file_full_name, "w")
				lines = ["[general]" + "\n",\
				"run_name = " + "\"" +config_file_name + "\"" +"\n\n",\
				"[architecture_presets]\n",\
				"ArrayHeight:    " + str(int(array_dim[0]/(div_base**ad_index))) + "," \
					+ str(int(second_array_dim[0]/(div_base**second_ad_index))) + "\n",\
				"ArrayWidth:     " + str(int(array_dim[1]/(div_base**ad_index))) + "," \
					+ str(int(second_array_dim[1]/(div_base**second_ad_index))) + "\n",\
				"IfmapSramSz:    512,512" + "\n",\
				"FilterSramSz:   512,512" + "\n",\
				"OfmapSramSz:    256,256" + "\n",\
				"IfmapOffset:    0" + "\n",\
				"FilterOffset:   10000000" + "\n",\
				"OfmapOffset:    20000000" + "\n",\
				"Dataflow:       " + dataflow + "\n"]
				config_file.writelines(lines)
				config_file.close()


def gen_config_files_single_SA(   dataflow_list=[],\
						array_dim_list=[],\
						config_dir='',\
						div_base=1 ):
	r'''
	Generates config_files for all combinations of the values in the list parameters for Single Systollic Array(SA)

	Args:
		dataflow_list: List of all dataflows. Possible entries:'os', 'ws' and 'is'
		array_dim_list: List of lists, each list with height and width of systolic array as its elements
		config_dir: The directory path where config files need to be stored
		div_base: Used for imply the effect of Scale-out opeartion. Array dimensions are scaled down by a factor of (div_base^x)
			1. div_base = 1 for scale-Up
			2. div_base = 2 for scale-Out
	
	Examples:
		>>> gen_config_files(dataflow_list=['os','is'],\
						array_dim_list=[[16,16],[32,16]],\
						config_dir='name_of_output_directory',\
						div_base=1 )

	'''
	if not os.path.exists(config_dir):
		os.system("mkdir -p " + config_dir)
	for dataflow in dataflow_list:
		for ad_index, array_dim in enumerate(array_dim_list):
			config_file_name = str(array_dim[0]) + "_" + str(array_dim[1]) + "_" + dataflow
			config_file_full_name = config_dir + '/./' + config_file_name + ".cfg"
			config_file = open(config_file_full_name, "w")
			lines = ["[general]" + "\n",\
			"run_name = " + "\"" +config_file_name + "\"" +"\n\n",\
			"[architecture_presets]\n",\
			"ArrayHeight:    " + str(int(array_dim[0]/(div_base**ad_index))) + "\n",\
			"ArrayWidth:     " + str(int(array_dim[1]/(div_base**ad_index))) + "\n",\
			"IfmapSramSz:    512" + "\n",\
			"FilterSramSz:   512" + "\n",\
			"OfmapSramSz:    256" + "\n",\
			"IfmapOffset:    0" + "\n",\
			"FilterOffset:   10000000" + "\n",\
			"OfmapOffset:    20000000" + "\n",\
			"Dataflow:       " + dataflow + "\n"]
			config_file.writelines(lines)
			config_file.close()

def main(argv):
	'''
	Run parallel SCALE-Sim runs
	'''
	origin_dir = './'
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

	parallel_runs(config_files_list=config_files_list,\
								topology_files_list=toplogy_file_list,\
								output_dir=output_dir,\
								max_parallel_runs=max_parallel_processes)
if __name__ == "__main__":
	app.run(main)
