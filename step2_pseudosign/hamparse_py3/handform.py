# -*- coding: UTF-8 -*-

import re

## Bsp.:  ;  ;  ; ; ;  ;  ; 
	

def getHandform(string, between, repetitions):

	handforms = u"(?:|||||||||||)"
	handformdiacritics = u"(?:|||||||)"
	fingerparts = u"(?:|||||)"
	
	fingers = u"(?:||||)"
	finger = u"(?:%s%s?%s?)" %(fingers, between, fingers) 
	
	modalitiesHandform = u"(?:%s|%s|%s|%s)" %(handformdiacritics, finger, fingerparts, repetitions)
	
	handform = u"%s+%s*" %(handforms, modalitiesHandform)
	finalHandform = u"%s(?:%s%s)?" %(handform, between, handform)
	
	patternHandform = re.compile(finalHandform) 
	
	return patternHandform.findall(string)
	

# HANDFORM
# -	Eine Handformangabe ist obligatorisch
# -	handformdiacritics, finger und fingerparts sind optional.
#-	mehrere fingers können hintereinander auftreten: 
#-	crossing fingers berücksichtigt: 
