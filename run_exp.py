# Name 			: run_exp.py
# Description	: run one of the experiments of SCALE-Sim Testing
# Author		: K Jithendra

r'''
Run a particular experiment from top_runs, based on the "type_of_run" flag value

FLAGS:
	type_of_run: A String used to run a particular experiment. Possible values:
		1. scale_up_square_sa : Executes an experiment of SCALE-Sim runs for various neural networks(NN) on various scaled-up systolic arrays(SA)
		2. rectangular_sa : Executes an experiment of SCALE-Sim runs for various neural networks(NN) on various reactangular shaped systolic arrays(SA)
		3. scale_out_square_sa: Executes an experiment of SCALE-Sim runs for various neural networks(NN) on various scaled-out systolic arrays(SA)
		4. bl_best_config: Executes an experiment of SCALE-Sim runs to find a best big-little SA for a particular neural networks(NN).
		5. bl_effect_of_scaling: Executes an experiment of SCALE-Sim runs to find the effect of scaling down the neural network(NN) size on the performance.
'''

from absl import app
import sys
sys.path.insert(1, './src/')

import top_runs as top_runs

def main(argv):
	top_runs.experiment_to_be_executed()

if __name__ == '__main__':
	app.run(main)