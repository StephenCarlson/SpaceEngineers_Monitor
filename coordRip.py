#!/usr/bin/env python2.6

import xml.etree.ElementTree as ET
import sys, os.path

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3

# User Parameters
xsiSchema = '{http://www.w3.org/2001/XMLSchema-instance}type'

# Application Definitions and Constants
saveFile = 'SANDBOX_0_0_0_.sbs'
configFile = 'Sandbox.sbc'

# Script Globals and Data Structures
homePath = os.getcwd()

def checkSaveFile(fileName):
	#data = [] #np.empty((2,1))
	#data = np.array([[0,1,2],[3,4,5]])#np.zeros((1,3))
	# data = np.zeros((1,3))
	data = []
	data.append([-3500.0,-7000.0,5000.0,'#FF7F00','s','Home',0])
	
	#print data.shape
	# x = []
	# y = []
	# z = []
	
	tree = ET.parse(fileName)
	root = tree.getroot()
	sectorObjects = root.find('SectorObjects')
	
	for e in sectorObjects.findall("./*[PositionAndOrientation]"):
		#string += e.get('x')+','+e.get('y')+','+e.get('z')+'\n'
		type = ['r','s'] #str(e.find('..').get())
		# print e.get(xsiSchema)
		if e.get(xsiSchema) == "MyObjectBuilder_VoxelMap": type = ['k','D'] # Black Diamond
		elif e.get(xsiSchema) == "MyObjectBuilder_CubeGrid": type = ['b','s'] # Blue Square
		elif e.get(xsiSchema) == "MyObjectBuilder_FloatingObject": type = ['y','o'] # Yellow Circle
		
		
		name = ''
		blocks = 0
		try:
			if e.find('./IsStatic') != None:
				if e.find('./IsStatic').text == 'true': #Discover if Station
					#print 'Station'
					type = ['c','s']
			if e.find('./GridSizeEnum') != None:
				if e.find('./GridSizeEnum').text =='Small':
					type = ['b','^']
			if e.find('./DisplayName') != None:
				name = e.find('./DisplayName').text
			if e.find('./CubeBlocks') != None:
				#print len(list(e.find('./CubeBlocks')))
				blocks = len(list(e.find('./CubeBlocks')))
		except e:
			print 'error'
		
		entry = [float(e.find('.//Position').get('x')),float(e.find('.//Position').get('y')),float(e.find('.//Position').get('z')),] #type]
		entry += type
		entry += [name,blocks]
		#print entry
		#if entry[4] != 'o' and entry[4] != 'D': data.append(entry)
		if int(entry[6]) >= 20: data.append(entry)
		#data = np.append(data,[entry],axis=0)
		# x.append(e.get('x'))
		# y.append(e.get('y'))
		# z.append(e.get('z'))
	#return [x,y,z]
	return data

	
# print checkSaveFile(saveFile)
data = checkSaveFile(saveFile)

# print data

	

fig = plt.figure()
ax = p3.Axes3D(fig)
#ax.scatter(data[:,0],data[:,1],data[:,2],data[:,3])
for x,y,z,c,m,n,b in data:
	# print x,y,z,c,m
	#ax.scatter(float(l[0]),float(l[1]),float(l[2]),c=l[3],marker=l[4])
	#print n
	ax.scatter(x,y,z,c=c,marker=m)
	ax.text(x,y,z,n)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xbound(-50000.0,50000.0)
ax.set_ybound(-50000.0,50000.0)
ax.set_zbound(-50000.0,50000.0)

plt.show()

