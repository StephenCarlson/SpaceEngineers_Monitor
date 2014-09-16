#!/usr/bin/env python2.6

# A Space Engineers Server Script, by Steve "AceNepets" Carlson, Sept 2014
# Written with Notepad++ with tab=4

# What does this thing do? Here is the description of how this works and why it is cool:
# If you host a Public Dedicated Space Engineers Server, you likely have an interest in knowing what is happening in the world it runs.
# Specifically, if you have some of your own creations in there, you might like to know if someone is trying to get around your security.
# Also, you may just want to know when your friends log into it, or strangers for that matter.
# To solve these problems, this script monitors the three (3) files that pretty much make up the world the server maintains:
# 		SANDBOX_0_0_0_.sbs
# 		Sandbox.sbc
# 		SpaceEngineersDedicated[optional-date-here].log

# The SANDBOX_0_0_0_.sbs file contains all the objects and their locations and ownerships. This is only saved/modified when the server autosaves.
# The Sandbox.sbc file is the server definition file, and also contains the players list and faction definitions.
# The above two files live in the world folder, usually named "Created Some Date yada yada"
# Two folders down from that folder should be the SpaceEngineersDedicated folder, which contains the server log files.
# The SpaceEngineersDedicated.log file(s) are created one each new start of the server. I am assuming is saved on each new line.
# If my assumption is correct, that the server saves the log file ever instant it writes a line to it, we can have real-time status on players.
# Unless the auto-save mechanism is active, I do not believe it is possible to discover the world's object states.
# Anyhow, with these three files, we can monitor for events we deem interesting. In my case: If turrets have fired/been destroyed, and new players.
# New Players are easy to discover in real-time, as the server spits out a line whenever someone joins. Turret ammo loss and damage requires XML Parsing.

# The Ultimate result of all this: You can have a text message or email sent to you the moment any of these events take place.

# To use this script, place it in the folder where the Sandbox.sbc and SANDBOX_0_0_0_.sbs files reside for the world you are running.
# Fill in the four (4) entires under # User Parameters, about 12 lines down.
# It is possible to change the email service you use, but you'll have to dig around for the SMTP settings/port and fill those in accordingly.
# Same goes for your mobile carrier. You need to find the SMS gateway address to send SMS messages to your phone via an email address.
# Some providers make this hard or unavailable, but the mechanism is email, so you can resort to that form of notification.
# To be safe in copying this around, never hard-code your password to your email account. This script requests your email password as a result.
# Fill in your Clan/Faction Tag, the three letters you create in the game, to have you and all your factions member's turrets added to the watch list.
# Any turret that loses (or gains) ammo will trip an event and send a message. Same for if a turret disappears. Adding turrets does not do anything.
# Obviously, you may want to exit the script when you or clan members are playing on the server, to avoid being text messaged the obvious.
# To exit the script, press CTRL+C on the console.
# On every auto-save that server does, the Guns and Faction Players should be updated in the script. 
# The script will display all turrets and factions members on each auto-save, or whenever the SANDBOX_0_0_0_.sbs is modified.

# Finally, to actually run the script, having placed it correctly as mentioned, type "python SE_Monitor.py" in the console viewing the world folder.

# Future work:
# 		Make it so that the script will not push updates when a member of the faction is in the game
# 		Export this as an executable so people don't have to have Python installed on their server
# 		Extend this to include all objects or blocks of interest in a faction
# 		Add a GUI, make it so users can select objects groups and actions for each
# 		Have the script monitor for updates to the SE Dedicated Server program (and force Steam to apply updated?) and restart the server if necessary


import smtplib
import xml.etree.ElementTree as ET
import time
import sys, os.path
import getpass
import re

# User Parameters
clanTag = 'ABC'
gmailAccount = 'YourGmailAccount@gmail.com'
password = getpass.getpass() #'0000' #
emailList = {'8015551234@txt.att.net'} #,"yourFriendsAddress@hotmail.com"}

# Application Definitions and Constants
saveFile = 'SANDBOX_0_0_0_.sbs'
configFile = 'Sandbox.sbc'
interiorTurretTag = 'MyObjectBuilder_InteriorTurret'
gatlingTurretTag = 'MyObjectBuilder_LargeGatlingTurret'
missileTurretTag = 'MyObjectBuilder_LargeMissileTurret'
turretList = {interiorTurretTag,gatlingTurretTag,missileTurretTag}

# Script Globals and Data Structures
logFile = '' 		# Auto selected by modification date
homePath = os.getcwd()
timestamp = 0.0
prevTell = 0
gunList = {}
gunListPrev = {} 	# Dictionary with keys:values
ownersList = [] 	# A mere list, beware the square verses curly brackets

def sendTextMsg(msgText):
	global gmailAccount, password, emailList
	server = smtplib.SMTP( "smtp.gmail.com", 587 )
	server.starttls()
	server.login( gmailAccount, password )
	for address in emailList: server.sendmail( gmailAccount, address, msgText)
	server.quit()
	return

def checkSaveFile(fileName):
	global gunList
	global ownersList
	global turretList
	gunList.clear()
	#os.chdir(homePath)
	
	tree = ET.parse(fileName)
	root = tree.getroot()
	sectorObjects = root.find('SectorObjects')
	
	print "Registered Guns and Launchers:"
	
	#for element in sectorObjects.findall(".//MyObjectBuilder_CubeBlock[@{http://www.w3.org/2001/XMLSchema-instance}type='MyObjectBuilder_InteriorTurret']"):
	for element in sectorObjects.findall(".//MyObjectBuilder_CubeBlock"):
		#if (element.find('SubtypeName').text == 'LargeInteriorTurret') or (element.find('SubtypeName').text == 'LargeGattlingGun'):
		xsiTag = '{http://www.w3.org/2001/XMLSchema-instance}type'
		# searchTerm = ".[@"+xsiTag+"='"+interiorTurretTag+"']"
		# print searchTerm
		for turretType in turretList:
			try:
				if(element.findall(".[@"+xsiTag+"='"+turretType+"']")):
					try:
						if element.find('Owner').text in ownersList:
							valueEntityId = element.find('EntityId').text
							valueAmmoAmount = element.find('./Inventory/Items//Amount').text
							valueCustomName = ''
							try: valueCustomName = element.find('CustomName').text
							except AttributeError: valueCustomName = turretType # Not all turrets have a custom name given
							gunList[valueEntityId] = valueCustomName,valueAmmoAmount
							
							print "\t",valueCustomName,valueAmmoAmount
					except AttributeError: continue # For no owner, such as Cargo Ships
			except AttributeError: continue # For no object matches, like a clean world
	print ''
	return

def initSaveFile(fileName):
	global clanTag
	global ownersList
	
	parser = ET.XMLParser(encoding="ISO 8859-1") 	# Beware special characters in user names!
	tree = ET.parse(fileName, parser=parser) 		#ET.XMLParser(encoding="utf-8"))
	root = tree.getroot()
	
	for faction in root.findall(".//Factions/Factions/MyObjectBuilder_Faction"):
		if clanTag in faction.find('Tag').text:
			for member in faction.findall("./Members/MyObjectBuilder_FactionMember"):
				ownersList.append(member.find("PlayerId").text)
	
	print "Detected Faction Members:"
	for player in root.findall(".//AllPlayers/PlayerItem"):
		# print player.findtext("PlayerId")
		if player.findtext("PlayerId") in ownersList: #if ownersList in player.find("PlayerId"):
			print '\t',player.findtext("Name")
	# print ownersList
	print ''
	return
	
def checkLogFile(fileName):
	file = open("../../"+fileName)
	#print file
	playerName = ''
	term = "World request received: "
	global prevTell
	currentTell = 0
	for line in file:
		if term in line:
			#print file.tell()
			currentTell = file.tell()
			playerName = re.search("World request received: (\w+)",line).group(1)
	
	if(currentTell > prevTell):
		prevTell = currentTell
		return playerName
	else: return False

def initLogFile():
	# Log file is a .log file, just named "SpaceEngineersDedicated.log" or ".._20141231_235959.log"
	# 2014-09-13 19:45:23.375 - Thread:   1 ->  World request received: Auston
	file_name = ''
	os.chdir("../..")
	mostRecent = 0.0
	#for file in os.listdir("../.."): #os.getcwd()): #
	for file in os.listdir(os.getcwd()): #): #
		#print file
		if file.startswith("SpaceEngineersDedicated") and file.endswith(".log") and os.path.getmtime(file) > mostRecent:
			file_name = file
			mostRecent = os.path.getmtime(file)
			#print file, os.path.getmtime(file)
	#print "Using Log File:",file_name
	os.chdir(homePath)
	return file_name

timestamp = os.path.getmtime(saveFile)
initSaveFile(configFile)

checkSaveFile(saveFile)
gunListPrev = gunList.copy()
# print gunListPrev

logFile = initLogFile()
print "Using:",logFile,'\n'
print "--- Script Start"

while True:
	try:
		eventOccured = False
		synopsis = ''
		logResult = checkLogFile(logFile)
		if(logResult):
			eventOccured = True
			synopsis += "Player Joined: "+str(logResult)+'\n'
			
		if os.path.getmtime(saveFile) >= (timestamp+10.0):
			timestamp = os.path.getmtime(saveFile)
			checkSaveFile(saveFile)
			#print gunListPrev
			
			for key in gunListPrev:
				#if gunList.has_key(key):
				if key in gunList:
					#print key ,gunList[key]
					if gunList.get(key) != gunListPrev[key]:
						eventOccured = True
						synopsis += str(gunList[key][0]) + " - " + str(gunList[key][1]) + " from " + str(gunListPrev[key][1]) + '\n'
				else:
					eventOccured = True
					synopsis += str(gunListPrev[key][0]) + " - Missing\n"
			gunListPrev = gunList.copy()
			initSaveFile(configFile)
		if eventOccured:
			message = "\nServer Event:\n\n" + synopsis
			print message
			#sendTextMsg(message)
			# gunListPrev = gunList.copy()
			print '---'
	except e: # Catch All Exceptions
		print "Error: ",str(e)
		time.sleep(5)
	finally:
		time.sleep(3)
