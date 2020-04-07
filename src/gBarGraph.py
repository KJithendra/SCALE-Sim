import numpy as np
import csv
import matplotlib.pyplot as pyplot

def gBarGraph(rtCycles=[],
				xLabel=['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7'],
				figName='outputs/figures/cycles.png',
				dfList=["os", "ws", "is"],
				debug=False):
	rtcShape = rtCycles.shape
	barWidth = 0.25
	barColor = ['#4F81BD', '#9F4C7C', '#9BBB59']
	fig, axes = pyplot.subplots(1,rtcShape[0], figsize=(rtcShape[0]*3+1,3))
	sfLable = [chr(alph) for alph in range(ord('a'),ord('a')+rtcShape[0])]
	x = np.arange(rtcShape[2])
	for spIndex in range(rtcShape[0]) :
		for i in range(rtcShape[1]) :
			axes[spIndex].bar(x+i*barWidth, rtCycles[spIndex][i], color =barColor[i], width = barWidth, zorder=3)

		axes[spIndex].grid(True, axis='y', zorder=0)
		# axes[spIndex].set_title('Cycles for array of size 128*128')
		axes[spIndex].set_xlabel(sfLable[spIndex])
		# axes[spIndex].set_ylabel('Runtime in million cycles')
		axes[spIndex].set_xticks([x1+barWidth for x1 in x])
		axes[spIndex].set_xticklabels(xLabel)
	axes[0].set_ylabel('Runtime in million cycles')
	pyplot.legend(labels = dfList, loc = (1,0.7))
	pyplot.tight_layout()
	pyplot.savefig(figName, transparent = True, format='png', orientation = 'landscape', dpi=300)
	if debug:
		pyplot.show()