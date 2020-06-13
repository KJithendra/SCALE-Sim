# Name 			: top_runs.py
# Description	: Performs different experiments of SCALE-Sim Testing
# Author		: K Jithendra

r'''
Collection of various testing functions to rund different experiments
A particular experiment is chosen based on the "type_of_run" flag value

FLAGS:
	type_of_run: A String used to run a particular experiment. Possible values:
		1. scale_up_square_sa : Executes an experiment of SCALE-Sim runs for various neural networks(NN) on various scaled-up systolic arrays(SA)
		2. rectangular_sa : Executes an experiment of SCALE-Sim runs for various neural networks(NN) on various reactangular shaped systolic arrays(SA)
		3. scale_out_square_sa: Executes an experiment of SCALE-Sim runs for various neural networks(NN) on various scaled-out systolic arrays(SA)
		4. bl_best_config: Executes an experiment of SCALE-Sim runs to find a best big-little SA for a particular neural networks(NN).
		5. bl_effect_of_scaling: Executes an experiment of SCALE-Sim runs to find the effect of scaling down the neural network(NN) size on the performance.
'''
import os
from os import listdir
from absl import flags
from absl import app

import parallel_runs as parallel_runs

FLAGS = flags.FLAGS
flags.DEFINE_string('type_of_run', 'bl_effect_of_scaling', 'The testing function that needs to be executed')


def single_sa_scale_up_square_sa():
	r'''
		Perform SCALE-Sim with Systolic arrays(SA) in Square dimensions. The dimesions are increased in scale-up method
		``This is a testing function ``
		Consists only one SA
		Examples:
			>>> single_sa_scale_up_square_sa() 
	'''

	'''
	Generate config files
	'''
	origin_dir = "."
	config_dir = origin_dir + "/configs/scale_up_square_SA/"

	dataflow_list = ["os", "ws", "is"]

	array_dim_list=[]
	array_dim_list = [[8,8], [16,16], [32,32], [64,64], [128,128]]

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
	config_dir = origin_dir + "/configs/scale_up_square_SA/"
	output_dir = 'outputs/scale_up_square_SA/'
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

def single_sa_reactangle_sa():
	r'''
		Perform SCALE-Sim with Systolic arrays(SA) in Rectangular dimensions
		``This is a testing function ``
		Consists only one SA
		Examples:
			>>> single_sa_reactangle_sa() 
	'''
	'''
	Generate config files
	'''
	origin_dir = "."
	config_dir = origin_dir + "/configs/scale_up_rectangle_SA/"

	dataflow_list = ["os", "ws", "is"]

	array_dim_list=[]
	array_dim_list = [[8,2048], [16,1024], [32,512], [64,256], [128,128], \
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
	topology_files = ["AlphaGoZero.csv", "DeepSpeech2.csv",\
						"FasterRCNN.csv", "NCF_recommendation_short.csv",\
						"Resnet50.csv", "Sentimental_seqCNN.csv",\
						"Transformer_short.csv"]

	toplogy_file_list = [(topology_dir + "/./" + x) for x in topology_files]

	print(config_dir_content)
	parallel_runs.parallel_runs(config_files_list=config_files_list,\
								topology_files_list=toplogy_file_list,\
								output_dir=output_dir,\
								max_parallel_runs=max_parallel_processes)

def single_sa_scale_out_square_sa():
	r'''
		Perform SCALE-Sim with Systolic arrays(SA) in Square dimensions. The dimesions are increased in scale-out method
		``This is a testing function ``
		Consists only one SA

		Examples:
			>>> single_sa_reactangle_sa() 
	'''
	import run_scaleOut as scale_out


def big_little_sa():
	r'''
		Perform SCALE-Sim runs with big little Systolic arrays(SA).
		``This is a testing function ``
		Consists only two systolic arrays
		Used for experimenting to find the best bigLittle configuratio for a neural Network, given a fixed number of processing elements
		
		Examples:
			>>> big_little_sa() 
	'''

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

def big_little_sa_effect_of_scaling_nn():
	r'''
		Perform SCALE-Sim runs with big little Systolic arrays(SA).
		``This is a testing function ``
		Consists only two systolic arrays
		Used for experimenting to find the effect of scaling the Network on performance
		
		Examples:
			>>> big_little_sa() 
	'''

	'''
	Generate config files
	'''
	origin_dir = "."
	config_dir = origin_dir + "/configs/big_little_SA_effect_of_scaling/"

	dataflow_list = ["ws"]

	array_dim_list=[[], []]
	array_dim_list[0] = [[32,32]]
	array_dim_list[1] = [[16,4]]

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
	config_dir = origin_dir + "/configs/big_little_SA_effect_of_scaling/"
	output_dir = 'outputs/big_little_SA_effect_of_scaling_alexnet/'
	max_parallel_processes = min((os.cpu_count()- 2),30)  # Maximum number of Parallel processes
	# Copy all config file names
	config_files_list = []
	config_dir_content = listdir(config_dir)
	config_files_list = [(config_dir + "/./" + x) for x in config_dir_content]

	# Copy all topology file names
	topology_files	= []
	file = ['alexnet_short_8times.csv', 'alexnet_short_10times.csv', \
			'alexnet_short_6times.csv', 'alexnet_short_4times.csv', \
			'alexnet_short_1times.csv','alexnet_short_2times.csv', 'alexnet_short_12times.csv']
	topology_files.extend(file)
	toplogy_file_list = [(topology_dir + "/./" + x) for x in topology_files]

	parallel_runs.parallel_runs(config_files_list=config_files_list,\
								topology_files_list=toplogy_file_list,\
								output_dir=output_dir,\
								max_parallel_runs=max_parallel_processes)

def experiment_to_be_executed():
	r'''
	Run one of the available experiments using the "type_of_run" flag value
	'''
	type_of_run = FLAGS.type_of_run
	if (type_of_run == 'scale_up_square_sa'):
		single_sa_scale_up_square_sa()
	elif (type_of_run == 'rectangular_sa'):
		single_sa_reactangle_sa()
	elif (type_of_run == 'scale_out_square_sa'):
		single_sa_scale_out_square_sa()
	elif (type_of_run == 'bl_best_config'):
		big_little_sa()
	elif (type_of_run == 'bl_effect_of_scaling') :
		big_little_sa_effect_of_scaling_nn()
	else:
		print('Incorrect flag value. Please enter a correct value for type_of_run flag from one of the following:')
		print("\t 1. scale_up_square_sa")
		print("\t 1. rectangular_sa")
		print("\t 1. scale_out_square_sa")
		print("\t 1. bl_best_config")
		print("\t 1. bl_effect_of_scaling")

def main(argv):
	experiment_to_be_executed()

if __name__ == '__main__':
	app.run(main)