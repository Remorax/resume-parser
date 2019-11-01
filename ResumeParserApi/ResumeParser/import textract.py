import textract,os
import csv

BASE = os.path.dirname(os.path.abspath(__file__))
path = '/FaultyResumes/'
fullpath =  BASE+path
files = os.listdir(fullpath)
myfiles = [i for i in files if i.endswith('.docx')]
file = open('rawtext.txt','w')
for i in range(0,len(myfiles)):
	testDocument = textract.process(fullpath+ myfiles[i])
	file.write(str(testDocument) + "\n\n\n\n\n\n\n\n\n")
file.close()	