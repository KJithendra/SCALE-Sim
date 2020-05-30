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

scaleOut = False
if scaleOut:
	topo_sub_folder = ['./', 'div4q/', 'div16q/', 'div64q/', 'div256q/']
	div_base = 2
else:
	topo_sub_folder = ['./', './', './', './', './', './', './', './', './']
	div_base = 1

origin_dir = ".";
# Copy all topology filenames into a list
topology_files	= []
# topology_dir 	= origin_dir + "/topologies/mlperf/"
# topology_dir_content 	= listdir(topology_dir)
# for file in topology_dir_content:
# 	if (fnmatch.fnmatch(file, "AlphaGoZero.csv") \
# 		| fnmatch.fnmatch(file, "DeepSpeech2.csv") \
# 		| fnmatch.fnmatch(file, "FasterRCNN.csv") \
# 		| fnmatch.fnmatch(file, "NCF_recommendation_short.csv") \
# 		| fnmatch.fnmatch(file, "Resnet50.csv") \
# 		| fnmatch.fnmatch(file, "Sentimental_seqCNN.csv") \
# 		| fnmatch.fnmatch(file, "Transformer_short.csv") ) == True: 
# 		topology_files.append(file)



file = 'alexnet_short.csv'
topology_files.append(file)
#topology_files = glob.glob(origin_dir + "/topologies/mlperf/*.csv")

# if debug == True :
# 	print(topology_files)


# Create config files
# dataflow_list	= ["os", "ws", "is"]
dataflow_list	= ["ws"]
# array_dim_list	= [[8,8], [16,16], [32,32], [64,64], [128,128]]
# second_array_dim_list =[[8,8], [16,16]] 
# array_dim_list	= [[8,8], [16,16], [32,32], [64,64], [128,128]]
# second_array_dim_list =[[16,16]]
array_dim_list	= [[16,64], [8,128], [4,256], [256,4], [128,8], [64,16]]
second_array_dim_list =[[4,16], [8,8], [16,4]]
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

# if debug == True :
# 	print(config_files)

# run scale sim for different conmbinations.
# topology_files and config_files are the lists that contain names of the topology and config_files respectively.
topology_dir 	= origin_dir + "/topologies/conv_nets/"
config_dir		= origin_dir + "/configs/"
run_count 		= 1
processes = set() # Parallel processes
max_parallel_processes = min((os.cpu_count()-4),30)  # Maximum number of Parallel processes
for file in topology_files:
	for second_ad_index, second_array_dim in enumerate(second_array_dim_list):
		for dataflow in dataflow_list:
			for ad_index, array_dim in enumerate(array_dim_list):
				config_file_name = file[0:len(file)-4] + "_" + str(array_dim[0]) + "_" + str(array_dim[1]) + "_" + str(second_array_dim[0]) + "_" + str(second_array_dim[1]) + "_" + dataflow
				config_file_full_name = config_dir + config_file_name + ".cfg"
				topology_file_name	= topology_dir + topo_sub_folder[ad_index]
				topology_file_full_name	= topology_file_name + file 
				# scale_sim_command = "python ./scale.py -arch_config=" + config_file_full_name + " -network=" + topology_file_full_name;
				#scale_sim_command = ["df", "-h", "/home"]
				all_outputs_dir = "../../../"
				arch_config = "-arch_config=../../../" + config_file_full_name
				arch_network = "-network=../../../" + topology_file_full_name
				scale_sim_command = ["python", "../../../scale.py", arch_config, arch_network] 
				if debug == True:
					print(scale_sim_command)
				print("INFO:: run_count:" + str(run_count))

				# os.system(scale_sim_command)
				output_top_folder = 'bigLittleArch_outputs_short_pm/'
				if not os.path.exists(origin_dir + "/outputs/" + output_top_folder):
					os.system("mkdir " + origin_dir + "/outputs/" + output_top_folder)
				output_file_dir = origin_dir + "/outputs/" + output_top_folder + config_file_name
				if not os.path.exists(output_file_dir):
					os.system("mkdir " + output_file_dir)
				else:
					t = time.time()
					new_output_file_dir= output_file_dir + "_" + str(t)
					os.system("mv " + output_file_dir + " " + new_output_file_dir)
					os.system("mkdir " + output_file_dir)
				os.system("cd " + output_file_dir)
				print(os.system("pwd"))
				std_out_file = open(output_file_dir + '/' + config_file_name +'.txt', mode='w+')
				processes.add(subprocess.Popen(scale_sim_command, cwd=output_file_dir, stdout=std_out_file))
				std_out_file.close()
				if(len(processes) >= max_parallel_processes ):
					os.wait()
					processes.difference_update([\
						p for p in processes if p.poll() is not None])
				os.system("cd ../../../")

				run_count = run_count +1;

for p in processes:
	if p.poll() is None:
		p.wait()