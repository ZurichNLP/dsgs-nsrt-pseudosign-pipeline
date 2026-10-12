# -*- coding: UTF-8 -*-
import re, os, handform, handposition, location, movement, symmetry, getBrackets, germanet, graphviz, codecs

def hamparse():	
	listOut = []
	dictComp = {}
	dictGermanet = {}
	dictTemp = {}
	dictRelations = {}
	dictNodesSublex = {}
	dictConnectionsSublex = {}
	dictNodesEntire = {}
	dictConnectionsEntire = {}
	dictNodesPartial = {}
	dictConnectionsPartial = {}
	dictConnectionsSublexTemp = {}

	fileInRelations = open(fileGermanet)
	contentRelations = fileInRelations.readlines()
	fileInRelations.close()
	
	for lineRelations in contentRelations:
		lineTT = lineRelations.split("\t")
		fromItem = lineTT[0].strip()	
		fromID = lineTT[1].strip()
		toItem = lineTT[2].strip()
		toID = lineTT[3].strip()
		relation = lineTT[4].strip()
		dictRelations.setdefault(fromItem, {}).setdefault(relation, {}).setdefault(toItem, []).append((fromID, toID))


	writeHamnosys(fileHamnosys, entireTXT, partialTXT, sublexTXT)
	
	getGermanet(entireTXT, partialTXT, sublexTXT, dictRelations)
	

	# ALLE (NICHT NUR FORMGLEICHE)
	dictOut1 = {} # direct
	dictOut2 = {} # indirect
	for lineHamnosys in getHamnosysAll(fileHamnosys):
		print lineHamnosys
		(dictOut1, dictOut2) = germanet.compareRelationsAll(dictRelations, lineHamnosys, dictOut1, dictOut2)	
	graphviz.writeGraphvizInGermanetAll(dictOut1, dictOut2, allAllInGermanetDOT, allAllInGermanetPDF)
	


def writeHamnosys(fileHamnosys, entireTXT, partialTXT, sublexTXT):
	counter = 0
	dictEntire = {}
	dictPartial = {}
	dictSublex = {}
	dictTempSublex = {}

	fileIn = open(fileHamnosys)
	content = fileIn.readlines()
	fileIn.close()	

	for line in content:
		lineTT = line.split("\t")
		lemma = lineTT[0].strip().decode("utf8")
		hamnosys = "".join(list(lineTT[1].strip().decode("utf8")))
		dictTempSublex = getSublex(hamnosys, lemma, dictTempSublex)

	for i in xrange(len(content)):
		line = content[i]
		lineTT = line.split("\t")
		lemma = lineTT[0].strip().decode("utf8")
		#print lemma
		hamnosys = "".join(list(lineTT[1].strip().decode("utf8")))
		
		for j in xrange(len(content)):
			line2 = content[j]
			lineTT2 = line2.split("\t")
			lemma2 = lineTT2[0].strip().decode("utf8")
			hamnosys2 = "".join(list(lineTT2[1].strip().decode("utf8")))
			
			if not lemma == lemma2:			
				# ENTIRE
				if hamnosys == hamnosys2 and not (lemma2, lemma) in dictEntire:
					dictEntire[(lemma, lemma2)] = "%s\t%s\t%s\t%s" %(lemma, hamnosys, lemma2, hamnosys2)
				# PARTIAL
				elif hamnosys in hamnosys2 and not hamnosys == hamnosys2 and not (lemma2, lemma) in dictPartial:
					dictPartial[(lemma, lemma2)] = "%s\t%s\t%s\t%s" %(lemma, hamnosys, lemma2, hamnosys2)
				# SUBLEX
				elif not hamnosys in hamnosys2 and not hamnosys == hamnosys2 and not (lemma2, lemma) in dictSublex:
					sublexComps = dictTempSublex[lemma]
 					sublexComps2 = dictTempSublex[lemma2]
					for sublex in sublexComps:
						hamComps = sublexComps[sublex]
						for hamComp in hamComps:
							for sublex2 in sublexComps2:
								hamComps2 = sublexComps2[sublex2]
								for hamComp2 in hamComps2:
									if hamComp == hamComp2 and not (lemma2, lemma) in dictSublex:
										counter += 1
								if counter > 1: # mind. 2 gemeinsame sublex. Komp.
									dictSublex[(lemma, lemma2)] = "%s\t%s\t%s\t%s" %(lemma, hamnosys, lemma2, hamnosys2)
								counter = 0

	print "writing..."
	
	#entire
	fileOut = open(entireTXT, "w+")
	fileOut.write("\n".join(sorted(set([dictEntire[el] for el in dictEntire]))).encode("utf8"))
	fileOut.close()
	dictEntire = {}
	#partial
	fileOut = open(partialTXT, "w+")
	fileOut.write("\n".join(sorted(set([dictPartial[el] for el in dictPartial]))).encode("utf8"))
	fileOut.close()
	dictPartial = {}
	#sublex
	fileOut = open(sublexTXT, "w+")
	fileOut.write("\n".join(sorted(set([dictSublex[el] for el in dictSublex]))).encode("utf8"))
	fileOut.close()
	dictSublex = {}
	

def getHamnosysAll(fileHamnosys):
	dictAll = {}
	
	fileIn = open(fileHamnosys)
	content = fileIn.readlines()#[:50] # <= HERE
	fileIn.close()	

	for i in xrange(len(content)):
		line = content[i]
		lineTT = line.split("\t")
		lemma = lineTT[0].strip().decode("utf8")
		#print lemma
		hamnosys = "".join(list(lineTT[1].strip().decode("utf8")))
		
		for j in xrange(len(content)):
			line2 = content[j]
			lineTT2 = line2.split("\t")
			lemma2 = lineTT2[0].strip().decode("utf8")
			hamnosys2 = "".join(list(lineTT2[1].strip().decode("utf8")))
			
			if not lemma == lemma2 and not (lemma2, lemma) in dictAll:
				yield "%s\t%s\t%s\t%s" %(lemma, hamnosys, lemma2, hamnosys2)
				dictAll[(lemma2, lemma)] = ""


def getGermanet(entireTXT, partialTXT, sublexTXT, dictRelations):
	listConnectionsEntireInGermanet = []
	listConnectionsPartialInGermanet = []
	listConnectionsSublexInGermanet = []
	listNodesEntireInGermanet = []
	listNodesPartialInGermanet = []
	listNodesSublexInGermanet = []
	listConnectionsEntireNotInGermanet = []
	listConnectionsPartialNotInGermanet = []
	listConnectionsSublexNotInGermanet = []
	listNodesEntireNotInGermanet = []
	listNodesPartialNotInGermanet = []
	listNodesSublexNotInGermanet = []	

	# GERMANET

	#entire
	(listConnectionsEntireInGermanet, listNodesEntireInGermanet, listConnectionsEntireNotInGermanet, listNodesEntireNotInGermanet) = germanet.compareRelations(dictRelations, entireTXT, entireInGermanetDOT, entireInGermanetPDF, entireNotInGermanetDOT, entireNotInGermanetPDF)
	graphviz.produceGraphviz(listConnectionsEntireInGermanet + listConnectionsEntireNotInGermanet, listNodesEntireInGermanet + listNodesEntireNotInGermanet, entireDOT, entirePDF)
	print "ENTIRE done\n"
	#partial
	(listConnectionsPartialInGermanet, listNodesPartialInGermanet, listConnectionsPartialNotInGermanet, listNodesPartialNotInGermanet) = germanet.compareRelations(dictRelations, partialTXT, partialInGermanetDOT, partialInGermanetPDF, partialNotInGermanetDOT, partialNotInGermanetPDF)
	graphviz.produceGraphviz(listConnectionsPartialInGermanet + listConnectionsPartialNotInGermanet, listNodesPartialInGermanet + listNodesPartialNotInGermanet, partialDOT, partialPDF)
	print "PARTIAL done\n"	
	#sublex
	(listConnectionsSublexInGermanet, listNodesSublexInGermanet, listConnectionsSublexNotInGermanet, listNodesSublexNotInGermanet) = germanet.compareRelations(dictRelations, sublexTXT, sublexInGermanetDOT, sublexInGermanetPDF, sublexNotInGermanetDOT, sublexNotInGermanetPDF)
# 	graphviz.produceGraphvizSublex(listConnectionsSublexInGermanet + listConnectionsSublexNotInGermanet, listNodesSublexInGermanet + listNodesSublexNotInGermanet, sublexDOT, sublexPDF)
	print "SUBLEX done\n"

	graphviz.produceGraphviz(listConnectionsEntireInGermanet + listConnectionsPartialInGermanet + listConnectionsSublexInGermanet, listNodesEntireInGermanet + listNodesPartialInGermanet + listNodesSublexInGermanet, allInGermanetDOT, allInGermanetPDF)

	graphviz.produceGraphviz(listConnectionsEntireNotInGermanet + listConnectionsPartialNotInGermanet + listConnectionsSublexNotInGermanet, listNodesEntireNotInGermanet + listNodesPartialNotInGermanet + listNodesSublexNotInGermanet, allNotInGermanetDOT, allNotInGermanetPDF)

	graphviz.produceGraphviz(listConnectionsEntireInGermanet + listConnectionsEntireNotInGermanet + listConnectionsPartialInGermanet + listConnectionsPartialNotInGermanet + listConnectionsSublexInGermanet + listConnectionsSublexNotInGermanet, listNodesEntireInGermanet + listNodesEntireNotInGermanet + listNodesPartialInGermanet + listNodesPartialNotInGermanet + listNodesSublexInGermanet + listNodesSublexNotInGermanet, allDOT, allPDF)
	


def getSublex(hamnosys, lemma, dictTemp):
	hamnosysSplit = getBrackets.getBrackets(hamnosys, repetitions)
	for stringSplit in hamnosysSplit:
		if u"" in stringSplit or u"" in stringSplit or u"" in stringSplit or u"" in stringSplit or u"" in stringSplit or u"" in stringSplit:
			entity = stringSplit.strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"").strip(u"")
			
			if len(entity) > 0:
				if u"" in entity:
					dictTemp.setdefault(lemma, {}).setdefault("MOV", []).append(entity.strip())
				else:
					dictTemp.setdefault(lemma, {}).setdefault("ENT", []).append(entity.strip())
		else:
			dictTemp = processLine(stringSplit, lemma, hamnosys, dictTemp)
		
	return dictTemp



def processLine(string, lemma, hamnosys, dictTemp):

	symmetries = symmetry.getSymmetry(string, between, speeds, sizes)
	
	handforms = handform.getHandform(string, between, repetitions)
	for hf in handforms:
		if len(hf) > 0:
			dictTemp.setdefault(lemma, {}).setdefault("HF", []).append(hf.strip())

	handpositions = handposition.getHandposition(string, between, repetitions, contact, alternating, speeds)
	for hp in handpositions:
		if len(hp) > 0:
			dictTemp.setdefault(lemma, {}).setdefault("HP", []).append(hp.strip())
		
	locations = location.getLocation(string, between, contact, repetitions)
	for lc in locations:
		if len(lc) > 0:
			dictTemp.setdefault(lemma, {}).setdefault("LOC", []).append(lc.strip())
		
	movements = movement.getMovement(string, between, sizes, speeds, repetitions, contact)
	for mv in movements:
		if len(mv) > 0:
			dictTemp.setdefault(lemma, {}).setdefault("MOV", []).append(mv.strip())

	return dictTemp
	

if __name__=="__main__":
	dictTemp = {}
	dictFinal = {}
	
	between = u"(?:)"
	sizes = u"(?:|)"
	speeds = u"(?:|)"
	repetitions = u"(?:||||)"
	alternating = u"(?:)"
	contact = u"(?:|||||)" # können vor oder nach locations stehen
	patternNonSymmetry = re.compile(u"(?:)") ## Bsp.:  ;  ;  ; 
	patternNoMirroring = re.compile(u"(?:)")

	dataDir = "/Users/sarahebling/Documents/ifi/SL/Hamnosys/Experimente/src/data/"
	outputDir = "/Users/sarahebling/Documents/ifi/SL/Hamnosys/Experimente/src/output/"
	germanetDir = "%sGermaNet6.0/" %dataDir
	
	fileHamnosys = "%shamnosys.txt" %dataDir
	fileGermanet = "%sgermanet.txt" %dataDir

# 	allAllTXT = "%sallall.txt" %outputDir
# 	allAllDOT = "%sallall.dot" %outputDir
# 	allAllPDF = "%sallall.pdf" %outputDir
	allAllInGermanetDOT = "%sall_all_in_germanet.dot" %outputDir
	allAllInGermanetPDF = "%sall_all_in_germanet.pdf" %outputDir
	allAllNotInGermanetDOT = "%sall_all_not_in_germanet.dot" %outputDir
	allAllNotInGermanetPDF = "%sall_all_not_in_germanet.pdf" %outputDir

	allTXT = "%sall.txt" %outputDir
	allDOT = "%sall.dot" %outputDir
	allPDF = "%sall.pdf" %outputDir
	allInGermanetDOT = "%sall_in_germanet.dot" %outputDir
	allInGermanetPDF = "%sall_in_germanet.pdf" %outputDir
	allNotInGermanetDOT = "%sall_not_in_germanet.dot" %outputDir
	allNotInGermanetPDF = "%sall_not_in_germanet.pdf" %outputDir

	entireTXT = "%sentire.txt" %dataDir
	entireDOT = "%sentire.dot" %outputDir
	entirePDF = "%sentire.pdf" %outputDir
	entireInGermanetDOT = "%sentire_in_germanet.dot" %outputDir
	entireInGermanetPDF = "%sentire_in_germanet.pdf" %outputDir
	entireNotInGermanetDOT = "%sentire_not_in_germanet.dot" %outputDir
	entireNotInGermanetPDF = "%sentire_not_in_germanet.pdf" %outputDir

	partialTXT = "%spartial.txt" %dataDir
	partialDOT = "%spartial.dot" %outputDir
	partialPDF = "%spartial.pdf" %outputDir
	partialInGermanetDOT = "%spartial_in_germanet.dot" %outputDir
	partialInGermanetPDF = "%spartial_in_germanet.pdf" %outputDir
	partialNotInGermanetDOT = "%spartial_not_in_germanet.dot" %outputDir
	partialNotInGermanetPDF = "%spartial_not_in_germanet.pdf" %outputDir

	sublexTXT = "%ssublex.txt" %dataDir
	sublexDOT = "%ssublex.dot" %outputDir
	sublexPDF = "%ssublex.pdf" %outputDir
	sublexInGermanetDOT = "%ssublex_in_germanet.dot" %outputDir
	sublexInGermanetPDF = "%ssublex_in_germanet.pdf" %outputDir
	sublexNotInGermanetDOT = "%ssublex_not_in_germanet.dot" %outputDir
	sublexNotInGermanetPDF = "%ssublex_not_in_germanet.pdf" %outputDir


	#germanet.writeGermanet(fileGermanet, germanetDir) # einmal laufen lassen

	hamparse()
	



# ALLGEMEIN
# -	Es gibt zwei verschiedene Grössenangaben (sizes).  
# -	Es gibt zwei verschiedene Geschwindigkeitsangaben (speeds).
#-	between-Symbol kann immer vorkommen, auch zwischen numbers in Handform (markiert dann z.B. thumb inbetween fingers: ; auch so: )
# contact specifier zu movement (nicht location)
# underspecification    einbauen (kann bei allen vier Komponenten vorkommen)	