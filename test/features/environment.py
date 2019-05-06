import os
from six.moves import urllib
from scipy.io import loadmat
from behave import *
import logging

def before_all(context):
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	logging.getLogger('').addHandler(console)
	print('Initialize environment')
	# Get the mnist data for testing
	mnist_path = 'mnist-original.mat'
	if not os.path.isfile(mnist_path):
		mnist_alternative_url = 'https://github.com/amplab/datascience-sp14/raw/master/lab7/mldata/mnist-original.mat'
		response = urllib.request.urlopen(mnist_alternative_url)
		with open(mnist_path, 'wb') as f:
			content = response.read()
			f.write(content)
	mnist_raw = loadmat(mnist_path)
	context.mnist = {
		'data': mnist_raw['data'].T,
		'target': mnist_raw['label'][0],
		'COL_NAMES': ['label', 'data']
	}