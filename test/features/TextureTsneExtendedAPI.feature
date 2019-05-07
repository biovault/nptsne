Feature: nptsne TextureTsneExtended API

Scenario: init_transform
	Given A TextureTsneExtended instance
	 When init_transform is run
	 Then decay started is -1
	 Then the iteration count is 0
	 
Scenario Outline: run_transform
	Given A TextureTsneExtended instance 
	 When init_transform and run_transform is run for <num_iters> iterations		
	 Then decay started is -1
	 Then the iteration count is <num_iters>
	 Then the embedding is within <max_range> and <min_range>
	 
	Examples: Iteration settings
		| num_iters  | max_range  | min_range  |
		| 100		 | 1.5,2.5    | -1.5,-2.5  |  
		| 200        | 4.5,5.8    | -4.5,-5.8  |
		| 500        | 8.5,11.5   | -8.5,-11.5 |
		| 1000       | 9.5,13.0   | -9.5,-13.0 |