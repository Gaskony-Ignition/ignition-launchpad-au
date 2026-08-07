def onStartup(session):
	lineFolderPath = exchange.launchpad.oee.BASE_TAG_FOLDER
	session.custom.exchange.launchpad.oee.lineTagFolder = lineFolderPath 
	lines = exchange.launchpad.oee.getLineNames(lineFolderPath) 

	session.custom.exchange.launchpad.oee.lines = lines
	session.custom.exchange.launchpad.oee.selectedLine = ""
	if len(lines)>0:
		session.custom.exchange.launchpad.oee.selectedLine = lines[0]
		