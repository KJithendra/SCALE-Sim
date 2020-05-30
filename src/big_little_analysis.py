# Name: Big little systolic array analysis
# Author: K Jithendra
# Description: 	1. Reads a pickle file. 
#				2. Finds the dimensions of each layer 
#				3. Computes the number of flops for inference of an image

# Import libraries
import numpy as np
import csv
import matplotlib.pyplot as pyplot
import torch
import torch.nn as nn
import os
from os import listdir

root_dir = './outputs/'
exp_folder_name = 'bigLittleArch_outputs_short_pm'
# Analysis file location
analysis_folder = root_dir + "analysis/" + exp_folder_name + '/'
if not os.path.exists(analysis_folder):
	print("mkdir -p " + analysis_folder)
	os.system("mkdir -p " + analysis_folder)

# Open all output files
conv1_summary = open(analysis_folder+'conv1_summary.csv', 'w+')
conv2_summary = open(analysis_folder+'conv2_summary.csv', 'w+')
conv3_summary = open(analysis_folder+'conv3_summary.csv', 'w+')
conv4_summary = open(analysis_folder+'conv4_summary.csv', 'w+')
conv5_summary = open(analysis_folder+'conv5_summary.csv', 'w+')

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

# Find all runs
exp_dir = root_dir + exp_folder_name + '/'
dir_content = listdir(exp_dir)
for run in dir_content:
	# print(f'{run}')
	out_dir = exp_dir + run + '/outputs/' + run + '/' 
	out_dir_content = listdir(out_dir)
	# for out_file in out_dir_content:
	# 	print(f'{out_file}')
	wo_dict = {} # write out dictionary
	wod_dict = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}
	out_file_name = out_dir + 'alexnet_short_cycles.csv'
	with open(out_file_name, mode = 'r') as out_file :
		fileContent	= csv.DictReader(out_file)
		for ind, line in enumerate(fileContent):
			wod_dict[ind]['run'] = run
			wod_dict[ind]['au'] = line['\t% Utilization'].strip()
			wod_dict[ind]['cycles'] = line['\tCycles'].strip()
	out_file_name = out_dir + 'alexnet_short_power_metric.csv'
	with open(out_file_name, mode = 'r') as out_file :
		fileContent	= csv.DictReader(out_file)
		for ind, line in enumerate(fileContent):
			wod_dict[ind]['pm'] = line['\tPower metric(Mega units)'].strip()
	out_file_name = out_dir + 'alexnet_short_avg_bw.csv'
	with open(out_file_name, mode = 'r') as out_file :
		fileContent	= csv.DictReader(out_file)
		for ind, line in enumerate(fileContent):
			wod_dict[ind]['dIFR'] = line['\tDRAM IFMAP Read BW'].strip()
			wod_dict[ind]['dFR'] = line['\tDRAM Filter Read BW'].strip()
			wod_dict[ind]['dOFR'] = line['\tDRAM OFMAP Write BW'].strip()
	for ind, file in enumerate(conv_summary):
		wo_string = wod_dict[ind]['run'] + ', ' + wod_dict[ind]['au'] + ', '\
			+ wod_dict[ind]['cycles'] + ', ' + wod_dict[ind]['pm'] + ', '\
			+ wod_dict[ind]['dIFR'] + ', ' + wod_dict[ind]['dFR'] + ', '\
			+ wod_dict[ind]['dOFR'] + '\n'
		file.write(wo_string)


# Close all output files
for file in conv_summary:
	file.close()