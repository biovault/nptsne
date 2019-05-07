from behave import *
from nose.tools import *
import nptsne
import logging

use_step_matcher("cfparse") # enable cardinality matching

@given('A TextureTsneExtended instance')
def step_impl(context):
	context.tsne = nptsne.TextureTsneExtended(False)
	
@when('init_transform is run')
def step_impl(context):
	context.tsne.init_transform(context.mnist['data'])
	
@then('decay started is "{start_iter:Number}"')	
def step_impl(context, start_iter):
	eq_(context.tsne.decay_started_at, start_iter, 'Expect decay started to have the "not started value"-1')
	
@then('the iteration count is 0')
def step_impl(context):
	eq_(context.tsne.iteration_count, 0, 'Expect iteration count to still be at 0')

@when(u'init_transform and run_transform is run for "{num_iters:Number}" iterations')
def step_impl(context, num_iters):
	context.tsne.init_transform(context.mnist['data'])
	context.embedding = context.tsne.run_transform(iterations=num_iters)
	 
@then(u'the iteration count is "{num_iters:Number}"')
def step_impl(context, num_iters):
	eq_(context.tsne.iteration_count, num_iters, f'Expect iteration count to still be at {num_iters}')	 
	
@then(u'the embedding is within "{max_range:Float+}" and "{min_range:Float+}"')
def step_impl(context, max_range, min_range):
	#logging.info(f'Max {max_range} Min {min_range}')
	logging.info(f'Embed max {context.embedding.max()} Embed min {context.embedding.min()}')
	# This is a minimal check on the embedding result content
	ok_(max_range[0] < context.embedding.max() < max_range[1], f'Expect the embedding tsne max value to be in the range {max_range[0]} - {max_range[1]} with standard settings')
	ok_(min_range[0] > context.embedding.min() > min_range[1], f'Expect the embedding tsne min value to be in the range {min_range[0]} - {min_range[1]} with standard settings')	
	
@when(u'run_transform for an additional "{num_iters:Number}" iterations')
def step_impl(context, num_iters):
	context.embedding = context.tsne.run_transform(iterations=num_iters)	
	
@when(u'set exaggeration decay on')
def step_impl(context):
	context.tsne.start_exaggeration_decay()