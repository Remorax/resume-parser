import csv
import glob, os
BASE = os.path.dirname(os.path.abspath(__file__))

myfiles = []
csvList= []

def MakeHeaders(mySkillList):
	import glob, os, csv
	
	BASE = os.path.dirname(os.path.abspath(__file__))
	
	if(os.path.isfile(BASE+'/ParsedResumeCSV/data_dump_skills.csv')):
		return True
	
	mySkillListHead = list(mySkillList)
	mySkillListHead.insert(0,"Candidate Name")
	# mySkillListHead.insert(1,"Skills Block")
	with open(BASE+'/ParsedResumeCSV/data_dump_skills.csv', 'ab') as fp:
			a = csv.writer(fp, delimiter=',')
			a.writerows([mySkillListHead])
	with open(BASE+'/ParsedResumeCSV/data_dump_education.csv', 'ab') as fp:
			a = csv.writer(fp, delimiter=',')
			a.writerows([['Candidate Name','Degree','Institute','Start year','End year','Education Block']])
	with open(BASE+'/ParsedResumeCSV/data_dump_exp.csv', 'ab') as fp:
			a = csv.writer(fp, delimiter=',')
			a.writerows([['Candidate Name','Company Name','Start year','End year','Company Block']])

with open('nameList.txt') as file:
	for line in file:
		myfiles.append(line.replace('\n',''))

with open('csvList.txt') as file:
	for (index,line) in enumerate(file):
		allWords = line.split('\'')
		allWords = list(filter(None, allWords))
		while ',' in allWords: allWords.remove(',')
		while ', ' in allWords: allWords.remove(', ')
		while '\\n' in allWords: allWords.remove('\\n')
		for (i,word) in enumerate(allWords):
			allWords[i] = allWords[i].strip()
			while ',' in allWords[i]:
				allWords[i] = allWords[i].replace(',','')
			while '\\n' in allWords[i]:
				allWords[i] = allWords[i].replace('\\n','')
			allWords[i] = allWords[i].strip()
		allWords = list(filter(None, allWords))
		csvList.append([myfiles[index],allWords])
import xml.etree.ElementTree as ET
degreesroot = ET.parse(BASE+'/lists.tnset').getroot()
mySkillList = [x.strip() for x in str(degreesroot.find('./itskills').text).split(',')]
MakeHeaders(mySkillList)
for x in csvList:
	i= x[0]
	ex = [i]
	print (ex)
	print (x[1])
	c = x[1]
	ex.extend(c)
	with open(BASE+'/ParsedResumeCSV/data_dump_exp.csv', 'a') as fp:
		a = csv.writer(fp, delimiter=',')
		a.writerows([ex])
