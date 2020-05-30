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
		# wod_dict = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}} # write out dictionary
		wod_dict = [{}, {}, {}, {}, {}] # write out dictionary
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

	# TODO: Find the best config
	with open(analysis_folder + 'run_summary.csv', mode = 'r') as summary_file :
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
root_dir = './outputs/'
exp_folder_name = 'bigLittleArch_outputs_short_pm'
# Analysis file location
analysis_folder = root_dir + "analysis/" + exp_folder_name + '/'
exp_dir = root_dir + exp_folder_name + '/'
dir_content = listdir(exp_dir)

best_config = create_layer_wise_summary(	analysis_folder=analysis_folder,
								exp_dir=exp_dir,
								dir_content=dir_content
								)