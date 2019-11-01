# -*- coding: utf-8 -*-


def comp(list1, list2):
	allcounts = []
	for val in list1:
		if val.lower() in list2:
			allcounts.append(str(list2.count(val)))
		else:
			allcounts.append("0")
	return allcounts

def comp2(list1, list2):
	allcounts = []
	for val in list1:
		if val.lower() in list2:
			allcounts.append(val)
	return allcounts

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

def BulkParsing(uid):
	import textract,os
	from GenericParserClass2 import GenericResumeParser
	BASE = os.path.dirname(os.path.abspath(__file__))
	path = '/BulkUploadResumes/'
	fullpath =  BASE+path+uid+"/"
	files = os.listdir(fullpath)
	myfiles = [i for i in files if i.endswith('.docx')]
	csvList = []
	# for i in myfiles:
	# 	print i
	# 	testDocument = textract.process(fullpath+i)
	# 	b = GenericResumeParser(testDocument)
	# 	csvList.append([i,b.AllParsersCall()])
	for i in xrange(4,5):
		print myfiles[i]
		testDocument = textract.process(fullpath+ myfiles[i])
		b = GenericResumeParser(testDocument)
		csvList.append([myfiles[i],b.AllParsersCall()])
	return csvList

def getAllResumeDetails(rawtext,uid,isBulk):
	import csv
	import glob, os
	BASE = os.path.dirname(os.path.abspath(__file__))
	# import textract
	# import thread
	csvList = []
	if(int(isBulk)==1):
		csvList = BulkParsing(uid)
		return csvList
	else:
		if(rawtext.strip() !=""):
			from GenericParserClass2 import GenericResumeParser
			b = GenericResumeParser(rawtext)
			return b.AllParsersCall()
			# csvList.append([uid,b.AllParsersCall()])

	# BASE = os.path.dirname(os.path.abspath(__file__))
	# from GenericParserClass import GenericResumeParser
	# path = '/BulkUploadResumes/'
	# fullpath =  BASE+path
	# files = os.listdir(fullpath)
	# myfiles = [i for i in files if i.endswith('.docx')]	
	# for i in myfiles:
	# 	print i
	# 	testDocument = textract.process(fullpath+i)
	# 	b = GenericResumeParser(testDocument)
	# 	csvList.append([i,b.AllParsersCall()])
	

	# code for writing to csv file 
	import xml.etree.ElementTree as ET
	degreesroot = ET.parse(BASE+'/lists.tnset').getroot()
	mySkillList = [x.strip() for x in str(degreesroot.find('./itskills').text).split(',')]
	# print csvList	
	MakeHeaders(mySkillList)
	

	for x in csvList:
		i= x[0]
		# print i
		# print x[1]
		s = [i]
		b = x[1]['Skills']
		mySkillVector = comp2(mySkillList,[y.lower() for y in b])
		s.extend(mySkillVector)
		with open(BASE+'/ParsedResumeCSV/data_dump_skills.csv', 'ab') as fp:
			a = csv.writer(fp, delimiter=',')
			a.writerows([s])
		ed = [i]
		d = x[1]['Education']
		ed.extend(d)
		with open(BASE+'/ParsedResumeCSV/data_dump_education.csv', 'ab') as fp:
			a = csv.writer(fp, delimiter=',')
			a.writerows([ed])
		ex = [i]
		c = x[1]['Experience']
		ex.extend(c)
		with open(BASE+'/ParsedResumeCSV/data_dump_exp.csv', 'ab') as fp:
			a = csv.writer(fp, delimiter=',')
			a.writerows([ex])


	return csvList