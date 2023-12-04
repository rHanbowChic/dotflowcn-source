#!/usr/bin/python2

####################################################################

from wikidot import WikidotToMarkdown

from io import open

from os import listdir

converter=WikidotToMarkdown()

########################

def convertAndSave(PATHNAME):

	umifile=open(PATHNAME,"r",encoding="utf-8")
	
	umi=umifile.read()
	
	umifile.close()
	
	############################################################

	umii=converter.convert(umi)

	############################################################
	
	umiifile=open("MediawikiConverted\\"+PATHNAME,"w",encoding="utf-8")
	
	umiifile.write(umii)

	umiifile.close()

########################

for path in listdir(".\\"):
	
	if ".txt" in path:
		
		convertAndSave(path)
		
		print (path+" is converted")

####################################################################

#2nohtyp\nib\rsu\!