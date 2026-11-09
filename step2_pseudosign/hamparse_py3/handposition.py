# -*- coding: UTF-8 -*-

import re

## Bsp.:  ;  ;  ; 

def getHandposition(string, between, repetitions, contact, alternating, speeds):

	fingerdirections = u"(?:|||||||||||||||||)"
	palmorientations = u"(?:|||||||)"
	wave = u"(?:)" # kann unter fingerdirections oder palmorientations stehen
	fingerdirection = u"(?:%s%s*(?:%s%s%s*)?)" %(fingerdirections, wave, between, fingerdirections, wave)
	palmorientation = u"(?:%s%s*(?:%s%s%s*)?)" %(palmorientations, wave, between, palmorientations, wave)
	
	finalHandposition = u"(?:(?:%s|%s)(?:%s|%s)?%s*%s*%s*%s*)" %(fingerdirection, palmorientation, fingerdirection, palmorientation, contact, speeds, repetitions, alternating)
	patternHandposition = re.compile(finalHandposition) 
	
	return patternHandposition.findall(string)


# 
# HANDPOSITION
# -	fingerdirection geht palmorientation immer voraus
# -	fingerdirection und palmorientation sind obligatorisch
	
