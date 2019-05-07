Feature: nptsne TextureTsneExtended API

# Note: in the tables everything is forced to string - this enables reuse 
# of steps between tables and passed values

Scenario: init_transform
	Given A TextureTsneExtended instance
	 When init_transform is run
	 Then decay started is "-1"
	 Then the iteration count is 0
	 
Scenario Outline: run_transform
	Given A TextureTsneExtended instance 
	 When init_transform and run_transform is run for <num_iters> iterations		
	 Then decay started is "-1"
	 Then the iteration count is <num_iters>
	 Then the embedding is within <max_range> and <min_range>
	 
	Examples: Iteration settings
		| num_iters  | max_range  | min_range    |
		| "100"	     | "1.5,2.5"  | "-1.5,-2.5"  |  
		| "200"      | "4.5,6.1"  | "-4.5,-6.1"  |
		| "500"      | "7.5,11.5" | "-7.5,-11.5" |
		| "1000"     | "9.5,13.0" | "-9.5,-13.0" |
		
Scenario: run transform and enable decay 	
	Given A TextureTsneExtended instance 
	 When init_transform and run_transform is run for "200" iterations
	 Then decay started is "-1"
	 Then the iteration count is "200"
	 Then the embedding is within "4.5,5.8" and "-4.5,-5.8"	
	 When run_transform for an additional "200" iterations
	 Then decay started is "-1"
	 Then the iteration count is "400"
	 Then the embedding is within "13.0,17.0" and "-13.0,-17.0"
	 When set exaggeration decay on
	  And run_transform for an additional "200" iterations
	 Then decay started is "400" 
	 Then the iteration count is "600"
	 Then the embedding is within "40,50" and "-40,-50"	 