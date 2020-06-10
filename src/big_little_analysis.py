# Name: Big little systolic array analysis
# Author: K Jithendra
# Description: 	1. Read output summary csv files of runs correspnding to different configs. 
#				2. Create new csv summary files corresponding to each conv layer 

# Import libraries
import numpy as np
import csv
import matplotlib.pyplot as pyplot
import torch
import torch.nn as nn
import os
from os import listdir
import statistics
from absl import app

def create_layer_wise_summary(	analysis_folder='',
								exp_dir='',
								dir_content=[]
								):
	if not os.path.exists(analysis_folder):
		print("mkdir -p " + analysis_folder)
		os.system("mkdir -p " + analysis_folder)

	# Open all output files
	conv_summary = []
	conv_summary.append(open(analysis_folder+'conv1_summary.csv', 'w+'))
	conv_summary.append(open(analysis_folder+'conv2_summary.csv', 'w+'))
	conv_summary.append(open(analysis_folder+'conv3_summary.csv', 'w+'))
	conv_summary.append(open(analysis_folder+'conv4_summary.csv', 'w+'))
	conv_summary.append(open(analysis_folder+'conv5_summary.csv', 'w+'))
	for file in conv_summary:
		file.write('run, Average utilization, Cycles for compute, ' +
			'Power consumed, DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW\n') 
	# Run Summary
	run_summary = open(analysis_folder + 'run_summary.csv', 'w+')
	run_summary.write('run, Average utilization, Cycles for compute, ' +
		'Power consumed, DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW\n') 
	
	# Find all runs
	for run in dir_content:
		out_dir = exp_dir + run + '/outputs/' + run + '/' 
		out_dir_content = listdir(out_dir)
		out_dir_content.sort()
		# wod_dict = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}} # write out dictionary
		wod_dict = [{}, {}, {}, {}, {}] # write out dictionary
		out_file_name = out_dir + out_dir_content[1]
		with open(out_file_name, mode = 'r') as out_file :
			fileContent	= csv.DictReader(out_file)
			for ind, line in enumerate(fileContent):
				wod_dict[ind]['run'] = run
				wod_dict[ind]['au'] = line['\t% Utilization'].strip()
				wod_dict[ind]['cycles'] = line['\tCycles'].strip()
		out_file_name = out_dir + out_dir_content[4]
		with open(out_file_name, mode = 'r') as out_file :
			fileContent	= csv.DictReader(out_file)
			for ind, line in enumerate(fileContent):
				wod_dict[ind]['pm'] = line['\tPower metric(Mega units)'].strip()
		out_file_name = out_dir + out_dir_content[0]
		with open(out_file_name, mode = 'r') as out_file :
			fileContent	= csv.DictReader(out_file)
			for ind, line in enumerate(fileContent):
				wod_dict[ind]['dIFR'] = line['\tDRAM IFMAP Read BW'].strip()
				wod_dict[ind]['dFR'] = line['\tDRAM Filter Read BW'].strip()
				wod_dict[ind]['dOFR'] = line['\tDRAM OFMAP Write BW'].strip()
				dOFR_str = wod_dict[ind]['dOFR']
				if(dOFR_str[len(dOFR_str)-4:]=='\tN/A'):
					wod_dict[ind]['dOFR'] = dOFR_str[:(len(dOFR_str)-4)]

		for ind, file in enumerate(conv_summary):
			wo_string = wod_dict[ind]['run'] + ', ' + wod_dict[ind]['au'] + ', '\
				+ wod_dict[ind]['cycles'] + ', ' + wod_dict[ind]['pm'] + ', '\
				+ wod_dict[ind]['dIFR'] + ', ' + wod_dict[ind]['dFR'] + ', '\
				+ wod_dict[ind]['dOFR'] + '\n'
			file.write(wo_string)
		# Write summary of each run into a folder
		run_dict={}
		run_dict['run'] = run
		run_dict['au'] = str(statistics.mean([float(x['au']) for x in wod_dict]))
		run_dict['cycles'] = str(sum([float(x['cycles']) for x in wod_dict]))
		run_dict['pm'] = str(sum([float(x['pm']) for x in wod_dict]))
		run_dict['dIFR'] = str(max([float(x['dIFR']) for x in wod_dict]))
		run_dict['dFR'] = str(max([float(x['dFR']) for x in wod_dict]))
		run_dict['dOFR'] = str(max([float(x['dOFR']) for x in wod_dict]))
		rs_string = run_dict['run'] + ', ' + run_dict['au'] + ', '\
			+ run_dict['cycles'] + ', ' + run_dict['pm'] + ', '\
			+ run_dict['dIFR'] + ', ' + run_dict['dFR'] + ', '\
			+ run_dict['dOFR'] + '\n'
		run_summary.write(rs_string)
	# Close all output files
	for file in conv_summary:
		file.close()
	run_summary.close()


'''
Find the best configuration:
	1. Use normalization to normalize all the metrics
	2. multiply normalized metrics with corresponding weights and sum the results. 
		xNorm = (x-xMin)/(xMax-xMin)
	3. The configuration with minimum value of the result from step 2 is  chosen as the best one
'''

def norm_func(metric_data=[]):
	minVal = min(metric_data, default=0)
	maxVal = max(metric_data, default=0)
	norm_data = [0] * len(metric_data)
	for ind, data in enumerate(metric_data):
		norm_value = (data - minVal)/(maxVal - minVal)
		# norm_data.append(norm_value)
		norm_data[ind] = norm_value
	return norm_data

def find_best_config_norm(file_name='', 
			metric_weights={'cycles':0.25, 'au':0.25, 'power':0.25, 'maxBW':0.25},
			output_file_name='outputs/analysis/norm_data.csv'):
	# TODO: Find the best config by using multiple metrics
	with open(file_name, mode = 'r') as summary_file :
		fileContent	= csv.DictReader(summary_file)
		metric_dict = {'cycles':[], 'au':[], 'power':[], 'maxBW':[], 'run_id':[]}
		norm_dict = {'cycles':[], 'au':[], 'power':[], 'maxBW':[], 'run_id':[],\
		 'weighed_value':[]}
		for data in fileContent:
			metric_dict['run_id'].append(data['run'])
			metric_dict['cycles'].append(float(data[' Cycles for compute'].strip()))
			metric_dict['au'].append(float(data[' Average utilization'].strip()))
			metric_dict['power'].append(float(data[' Power consumed'].strip()))
			maxBW = max([float(data[' DRAM IFMAP Read BW'].strip()),\
						float(data[' DRAM Filter Read BW'].strip()),\
						float(data[' DRAM OFMAP Write BW'].strip())])
			metric_dict['maxBW'].append(maxBW)
		norm_dict['run_id'].extend(metric_dict['run_id'])
		norm_dict['cycles'] = norm_func(metric_dict['cycles'])
		norm_dict['au'] = norm_func(metric_dict['au'])
		norm_dict['power'] = norm_func(metric_dict['power'])
		norm_dict['maxBW'] = norm_func(metric_dict['maxBW'])
		# print(norm_dict)
		with open(output_file_name, mode = 'w+') as out_file:
			out_file.write('run, Average utilization, Cycles for compute,' +
			# ' Power consumed, DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW,' +\
			' Power consumed,' +\
			' max_BW, norm_au, norm_cycles, norm_power, norm_maxBW, weighed_metric\n')
			for ind in range(len(norm_dict['run_id'])):
				weighed_metric = (norm_dict['cycles'][ind] * metric_weights['cycles']) +\
									(norm_dict['au'][ind] * metric_weights['au']) +\
									(norm_dict['power'][ind] * metric_weights['power']) +\
									(norm_dict['maxBW'][ind] * metric_weights['maxBW'])

				norm_dict['weighed_value'].append(weighed_metric)
				# print(norm_dict['run_id'][ind], weighed_metric)
				rs_string = norm_dict['run_id'][ind] + ', ' + str(metric_dict['au'][ind]) + ', '\
					+ str(metric_dict['cycles'][ind]) + ', ' + str(metric_dict['power'][ind]) + ', '\
					+ str(metric_dict['maxBW'][ind]) + ', ' + str(norm_dict['au'][ind]) + ', '\
					+ str(norm_dict['cycles'][ind]) + ', '  + str(norm_dict['power'][ind]) + ', '\
					+ str(norm_dict['maxBW'][ind]) + ', ' + str(weighed_metric) + ' \n '
				out_file.write(rs_string)
		# best_config= str(min([float(x[' Cycles for compute'].strip()) for x in fileContent]))
		best_config= min(norm_dict['weighed_value'], default=0)
		bc_index = norm_dict['weighed_value'].index(best_config)
		print(best_config, bc_index, norm_dict['run_id'][bc_index])
		print("Best config_details using norm:\n" +
			"Run_name\t\t\t:  " + metric_dict['run_id'][bc_index] + "\n" +
			"Average Utilization(%)\t\t: " + str(metric_dict['au'][bc_index]) + "\n" +
			"Total Cycles for compute\t: " + str(metric_dict['cycles'][bc_index]) + "\n" +
			"Power consumed\t\t\t: " + str(metric_dict['power'][bc_index]) + "\n" +
			"Max BW\t\t\t\t: " + str(metric_dict['maxBW'][bc_index]) + "\n"
			# "DRAM IFMAP Read BW\t\t: " + best_config[' DRAM IFMAP Read BW'] + "\n" +
			# "DRAM Filter Read BW\t\t: " + best_config[' DRAM Filter Read BW'] + "\n" +
			# "DRAM OFMAP Write BW\t\t: " + best_config[' DRAM OFMAP Write BW'] + "\n"
			)
	return best_config 

def find_best_config(file_name=''):
	# TODO: Find the best config by using multiple metrics
	with open(file_name, mode = 'r') as summary_file :
		fileContent	= csv.DictReader(summary_file)
		# best_config= str(min([float(x[' Cycles for compute'].strip()) for x in fileContent]))
		best_config= min(fileContent, default=0, key = lambda k: float(k[' Cycles for compute'].strip()))
		print("Best config_details:\n" +
			"Run_name\t\t\t:  " + best_config['run'] + "\n" +
			"Average Utilization(%)\t\t: " + best_config[' Average utilization'] + "\n" +
			"Total Cycles for compute\t: " + best_config[' Cycles for compute'] + "\n" +
			"Power consumed\t\t\t: " + best_config[' Power consumed'] + "\n" +
			"DRAM IFMAP Read BW\t\t: " + best_config[' DRAM IFMAP Read BW'] + "\n" +
			"DRAM Filter Read BW\t\t: " + best_config[' DRAM Filter Read BW'] + "\n" +
			"DRAM OFMAP Write BW\t\t: " + best_config[' DRAM OFMAP Write BW'] + "\n"
			)
	return best_config 


def effect_of_scaling_net(file_name='', field_y_axis=' Cycles for compute'):
	with open(file_name, mode = 'r') as summary_file :
		fileContent	= csv.DictReader(summary_file)
		cycles = []
		run_names = []
		for line in fileContent:
			cycles.append(float(line[field_y_axis].strip()))
			run_id = line['run'].split('_')[2]
			if(run_id=='32'):
				run_id = '1times'
			run_names.append(int(run_id[:-5]))
		# print(cycles)
		# print(run_names)
		run_names, cycles = zip(*sorted(zip(run_names,cycles)))
	return run_names, cycles

def get_compute_cycles_list(file_name='', field_y_axis=' Cycles for compute',\
						filed_x_axis = 'run'):
	with open(file_name, mode = 'r') as summary_file :
		fileContent	= csv.DictReader(summary_file)
		cycles = []
		run_names = []
		for line in fileContent:
			# print(line)
			if(line[field_y_axis] != None):
				cycles.append(float(line[field_y_axis].strip()))
				run_names.append(line[filed_x_axis][14:])
		# print(cycles)
		# print(run_names)
		run_names, cycles = zip(*sorted(zip(run_names,cycles)))
	return run_names, cycles


def calc_flops(topology_file='./topologies/conv_nets/alexnet.csv'):
	flops = 0
	with open(topology_file, mode = 'r') as net:
		netContent = csv.DictReader(net)
		for layer in netContent:
			c = int(layer[' Channels'].strip())
			h = int(layer[' IFMAP Height'].strip())
			w = int(layer[' IFMAP Width'].strip())
			m = int(layer[' Num Filter'].strip())
			r = int(layer[' Filter Height'].strip())
			s = int(layer[' Filter Width'].strip())
			sx = int(layer[' Strides'].strip())
			flops_for_layer = (m)*((h-r)/sx + 1)*((w-s)/sx +1)*(2*c*r*s-1)
			flops = flops + flops_for_layer
	return flops


def main(argv):
	root_dir = './outputs/'
	exp_folder_name = 'bigLittleArch_outputs_short_pm_ws'
	# Analysis file location
	analysis_folder = root_dir + "analysis/" + exp_folder_name + '/'
	exp_dir = root_dir + exp_folder_name + '/'
	dir_content = listdir(exp_dir)
	# print(dir_content)
	# Create summary files
	create_layer_wise_summary(	analysis_folder=analysis_folder,
									exp_dir=exp_dir,
									dir_content=dir_content
									)

	# Find Best configuration
	file_name = analysis_folder + 'run_summary.csv'
	best_config = find_best_config(file_name=file_name)

	# Find best configuration using norm method
	file_name = analysis_folder + 'run_summary.csv'
	best_config_norm = find_best_config_norm(file_name=file_name,\
			 metric_weights={'cycles':0.5, 'au':0.25, 'power':0.125, 'maxBW':0.125})

	root_dir = './outputs/'
	exp_folder_name = 'bigLittleArch_outputs_short_pm_ws_scaling'
	# Analysis file location
	analysis_folder = root_dir + "analysis/" + exp_folder_name + '/'
	exp_dir = root_dir + exp_folder_name + '/'
	dir_content = listdir(exp_dir)
	# print(dir_content)
	# Create summary files
	create_layer_wise_summary(	analysis_folder=analysis_folder,
									exp_dir=exp_dir,
									dir_content=dir_content
									)

	'''
	Generate a plot for effect of scaling
	'''
	figName = 'outputs/figures/effect_of_scaling_net_comb_ws.png'
	file_name = analysis_folder + 'run_summary.csv'
	run_names, cycles = effect_of_scaling_net(file_name=file_name,\
								field_y_axis=' Cycles for compute')
	
	fig, axes = pyplot.subplots()
	color = '#4F81BD'
	axes.plot(run_names, cycles, marker='o', color=color)
	axes.set_xlabel('Scale down factor')
	axes.set_ylabel('Clock cycles', color=color)
	axes.set_title('Effect of scaling net')
	axes.tick_params(axis='y', labelcolor=color)


	# Calculate FLOPS for different networks
	topology_files = ['alexnet_short_8times.csv', 'alexnet_short_10times.csv', \
	'alexnet_short_6times.csv', 'alexnet_short_4times.csv', \
	'alexnet_short_1times.csv','alexnet_short_2times.csv', 'alexnet_short_12times.csv']
	topology_files.sort()
	topology_dir = './topologies/conv_nets/'
	flops =[]
	run_names =[]
	for ind, file in enumerate(topology_files):
		topology_file = topology_dir + file
		flops_run = calc_flops(topology_file=topology_file)
		flops.append(flops_run)
		run_names.append(int(file[:-4].split('_')[2][:-5]))
		print(run_names[ind],":", flops[ind])

	run_names, flops = zip(*sorted(zip(run_names,flops)))

	axes2 = axes.twinx()
	color = '#9F4C7C'
	axes2.plot(run_names, flops, marker='*', color=color)
	axes2.set_ylabel('FLOPs', color = color)
	axes2.tick_params(axis='y', labelcolor=color)
	axes2.grid(True)
	fig.tight_layout()
	pyplot.savefig(figName, transparent = False, \
		format= 'png', orientation = "landscape", dpi= 300)
	pyplot.close(fig=None)


	'''
	Draw a scatter plot of computational cycles for the experiment
	'''
	exp_folder_name = 'bigLittleArch_outputs_short_pm_ws'
	analysis_folder = root_dir + "analysis/" + exp_folder_name + '/'
	file_name = analysis_folder + 'run_summary.csv'

	run_ids, cycles_list = get_compute_cycles_list(file_name=file_name)

	fig, axes = pyplot.subplots()
	figName = 'outputs/figures/scatter_plot_exp_ws.png'
	color = '#4F81BD'
	axes.scatter(run_ids, cycles_list, marker='o', color=color)
	axes.set_xlabel('Run name')
	axes.set_ylabel('Clock cycles', color=color)
	axes.set_title('Scatter plot of compute cycles')
	axes.tick_params(axis='y', labelcolor=color)
	axes.tick_params(axis='x', rotation=90, labelsize=6)
	axes.grid(True)
	fig.tight_layout()
	pyplot.savefig(figName, transparent = False, \
		format= 'png', orientation = "landscape", dpi= 300)
	pyplot.close(fig=None)

	'''
	Draw a scatter plot of weighed metric  for the experiment
	'''
	exp_folder_name = '.'
	analysis_folder = root_dir + "analysis/" + '/'
	file_name = analysis_folder + 'norm_data.csv'
	print(file_name)	
	run_ids, wm_list = get_compute_cycles_list(file_name=file_name, field_y_axis=' weighed_metric')

	fig, axes = pyplot.subplots()
	figName = 'outputs/figures/scatter_plot_exp_ws_weighed_metric_2.png'
	color = '#4F81BD'
	axes.scatter(run_ids, wm_list, marker='o', color=color)
	axes.set_xlabel('Run name')
	axes.set_ylabel('Weighed metric', color=color)
	axes.set_title('Weighed metric vs run name')
	axes.tick_params(axis='y', labelcolor=color)
	axes.tick_params(axis='x', rotation=90, labelsize=6)
	axes.grid(True)
	fig.tight_layout()
	pyplot.savefig(figName, transparent = False, \
		format= 'png', orientation = "landscape", dpi= 300)
	pyplot.close(fig=None)

if __name__ == '__main__':
  app.run(main)