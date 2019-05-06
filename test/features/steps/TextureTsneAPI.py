from behave import *
from nose.tools import *
import nptsne
import logging

@given('A TextureTsne instance')
def step_impl(context):
	context.tsne = nptsne.TextureTsne(False)
	
@when('fit_transform is run')
def step_impl(context):
	context.embedding = context.tsne.fit_transform(context.mnist['data'])
	
@then('the resulting embedding is of the correct size and content')
def step_impl(context):
	# logging.info(f'Max {context.embedding.max()} Min {context.embedding.min()}')
	eq_(context.embedding.shape[0], 140000, f'Expected 140000 floats in embedding found {context.embedding.shape[0]}')
	ok_(context.embedding.max() < 40, 'Expect the embedding tsne max value to be < 40 with standard settings')
	ok_(context.embedding.min() > -40, 'Expect the embedding tsne min value to be > -40 with standard settings')
