# -*- coding: UTF-8 -*-

import re

## Bsp.:  ;  ; 

def getSymmetry(string, between, speeds, sizes):

	symmetryoperators = u"(?:|)"  
	symmetryalternating = u"(?:)" 
	fingerstraight = u"(?:)" 
	modalitiesSym = u"(?:%s|%s|%s|%s)" %(speeds, sizes, symmetryalternating, fingerstraight)
	
	finalSymmetry = u"%s+%s*" %(symmetryoperators, modalitiesSym)
	patternSymmetry = re.compile(finalSymmetry)  
	

	############################# NON-SYMMETRY (TWO-HANDED SIGNS) ###########################
	nonsymmetry = u"(?:)*"
	nomirroring = u"(?:)*"
	
	## Bsp.:  ;  ;  ; 
	
	
	

	return patternSymmetry.findall(string)



# (u"(?:(|)?()?()?()?)") bzw. Non-Symmetry () einbauen
# Wann kann  allein stehen (z.B. in Münzen)?
# non-symmetry: nomirroring () einbeziehen
# symmetry: KLAMMERN nach  berücksichtigen (evtl. als Ganzes erfassen)
# Wo genau steht ?
# Es gibt innerhalb der Symmetrie ein Symbol hamfingerstraightmod
# Wozu dient hamfingerstraightmod?
# symmetryalternating, fingerstraight, speeds und sizes sind im Kontext der Symmetrie allesamt optional.
# Die Symmetrieoperatoren symmetryoperators sind optional.  bedeutet, dass die Hände stets spiegelbildlich zueinander angeordnet; , dass die Hände stets parallel, aber nicht notwendigerweise spiegelbildlich zueinander angeordnet sind
# Bei Alternativbewegung von Symmetriegebärden muss am Ende der Bewegung das Symbol  gesetzt werden (vgl. GEBÄRDEN)
# Wie werden nonsymmetry und nomirroring verwendet?
