Feature: nptsne TextureTsne API

Scenario: fit_transform
	Given A TextureTsne instance
	 When fit_transform is run
	 Then the resulting embedding is of the correct size and content 