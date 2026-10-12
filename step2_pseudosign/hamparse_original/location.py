# -*- coding: UTF-8 -*-

import re

## Bsp.:  ;  ;  ;  ;  

global locations
global besides
global location
global finalLocation
global patternLocation

locations = u"(?:||||||||||||||||||||||||||||||||||||||)"
locationspecifiers = u"(?:||||||)"
besides = u"(?:|)" # können vor oder nach locations stehen



def getLocation(string, between, contact, repetitions):
	location = u"(?:%s*(?:%s%s*)*%s%s*%s*%s*)" %(locationspecifiers, besides, contact, locations, locationspecifiers, besides, contact) # %s+: locations mehrmals hintereinander möglich (wahrscheinlichster Fall: 2x)

	finalLocation = u"%s+(?:%s%s+%s*)?%s*" %(location, between, location, repetitions, repetitions)
	patternLocation = re.compile(finalLocation) 

	return patternLocation.findall(string)


# def getFinalLocation(contact, between, repetitions):
# 	location = u"(?:%s*%s*%s%s*%s*)" %(besides, contact, locations, besides, contact) # %s+: locations mehrmals hintereinander möglich (wahrscheinlichster Fall: 2x)
# 
# 	finalLocation = u"%s+(?:%s%s+%s*)?%s*" %(location, between, location, repetitions, repetitions)
# 
# 	return finalLocation



# Location-Angabe ist nicht obligatorisch (?)
# besides hat eine andere Semantik, je nachdem, ob es vor oder nach der Location steht => ...
# -	||||  auch hier

