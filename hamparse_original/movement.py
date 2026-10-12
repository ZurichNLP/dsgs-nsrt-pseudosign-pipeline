# -*- coding: UTF-8 -*-

import re, location

## Bsp.:  ;  ; 
	

def getMovement(string, between, sizes, speeds, repetitions, contact):

	movementsizes = u"(?:|)"
	intensities = u"(?:||)"
	modalities = u"(?:%s|%s|%s|%s)" %(sizes, speeds, movementsizes, intensities)
	
	arrows = u"(?:(?:|||||||||||||||||)%s*)" %(modalities) # movement arrows (chords)
	directions = u"(?:(?:|||)%s*)" %(modalities) 
	arcs = u"(?:(?:|||)%s*)" %(modalities) 
	circles = u"(?:(?:|||||||||||||||||)%s*)" %(modalities)
	startingendingpoints = u"(?:||||||||)"
	wristforearmComponents = u"(?:||||)"
	crossComponents = u"(?:|)"
	replace = u"(?:)" # replacement of handshape and/or orientation
	wiggle = u"(?:(?:)%s*)" %(modalities)
	waveComponent = u"(?:(?:)%s*)" %(modalities)
	zigzagComponent = u"(?:(?:)%s*)" %(modalities)
	brushingComponent = u"(?:)"
	headComponent = u"(?:)"
	
	# movements
	curved = u"(?:%s+%s+)" %(arrows, directions)
	wavy = u"(?:%s+%s+%s*)" %(arrows, waveComponent, arcs)
	zigzag = u"(?:%s+%s+%s*)" %(arrows, zigzagComponent, arcs)
	circular = u"(?:%s+%s*)" %(circles, startingendingpoints)
	spiral = u"(?:%s+%s+)" %(circles, movementsizes) 
	elliptic = u"(?:%s+%s+)" %(circles, arcs)
	inplace = u"(?:%s+)" %(replace)
	fingerwigglingcrubling = u"(?:%s*%s)" %(arrows, wiggle)
	wristforearm = u"(?:%s+)" %(wristforearmComponents)
	cross = u"(?:%s+)" %(crossComponents)
	straight = u"(?:%s+)" %(arrows)
	none = u"(?:)"
	brushing = u"(?:%s)" %(brushingComponent) # Location hinzufügen
	head = u"(?:%s%s+)" %(headComponent, arrows)
# 	bouncing = u"(?:)"
	
	movement = u"(?:(?:%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s)+%s*%s*)" %(curved, wavy, zigzag, circular, spiral, elliptic, fingerwigglingcrubling, wristforearm, none, cross, brushing, straight, contact, repetitions)
	
	finalMovement = u"(?:%s(?:%s%s)?)" %(movement, between, movement)
	patternMovement = re.compile(finalMovement)# straight muss am Schluss stehen
	# inplace weggelassen
	
	return patternMovement.findall(string)

# MOVEMENT
# -	Bewegungsarten: ......
# -	arcs können zusammen mit ... auftreten, stehen nach ...
# -	Bewegung ist optional (z.B. "Ohr")
# -	spiral movement: movementsize muss vorhanden sein
# -	 allein weggelassen
# repetitions, movementsitzes und intensities ist optional (?)
# Nur circularmovements haben (optionale) startingendingpoints

