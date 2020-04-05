import os
import shutil
rootFolder	= 'outputs/output_summary/'
outFolderName	= 'outputs'
dirContent	= os.listdir(rootFolder)

for folder in dirContent :
	folderContent = os.listdir(rootFolder+folder)
	#Storing all csv files in outputs folder
	folderName = rootFolder + folder + '/' + outFolderName
	if not os.path.exists(folderName) :
		os.makedirs(folderName)
		os.makedirs(folderName + '/' + folder)
		for file in folderContent :
			shutil.move(rootFolder + folder + '/' + file, folderName + '/' + folder + '/')
	if len(folderContent)!= 1 :
		for file in folderContent :
			if (file != outFolderName) :
				shutil.move(rootFolder + folder + '/' + file, folderName + '/' + folder + '/')