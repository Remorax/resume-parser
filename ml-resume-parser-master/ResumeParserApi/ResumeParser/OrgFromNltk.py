# -*- coding: utf-8 -*-
# import nltk
# from nltk import word_tokenize
def Extract_Org(text):
	y = nltk.word_tokenize(text)
	# w = nltk.ne_chunk(y)
	# print w
	k = nltk.pos_tag(y)
	grammar="""PER: {(<NNP>)*}"""
	cp = nltk.RegexpParser(grammar)
	m=cp.parse(k)
	m = nltk.ne_chunk(k)
	# m.draw()
	k=[]
	for i in m.subtrees(filter=lambda x: x.label()=='ORGANIZATION'):
		k.append(i)
	OrgList =  []
	for l in k:
		myorg = ""
		for j in l:
			myorg += j[0]+" "
		OrgList.append(myorg.strip())
	return OrgList



# print Extract_Org(""" 
# PROFESSIONAL EXPERIENCE
# US IT Solutions
# Project Manager/ Product Consultant– Dallas, Texas, Jan 2016 – May 2016
# Client: PEA - Patient Engagement Advisors
# 	Managed project activities across all project phases, including initiation, planning, execution, monitoring, control and closure for large and small scale projects.
# 	Performed project management functions like planning, defining short and long term goals and objectives, forecasting & budgeting, scheduling, work-break down structure, developing Gantt chart.
# 		Worked on data modeling, slicing and dicing of data, data clean up and data massaging activities for reports and operational activities.


# """)


















strDocumemtText  = """ PMAM Smart Select.
A complete recruitment and staffing solution that allows recruiters to design tests for candidates applying for specialized skills required for the job.
Worked with a team of 4 developed using pure HTML with JQuery, JSON, Ajax with Web API C# & SQL Server 2014.
Primarily designed Certification and Job Posting module of the application.

SYSCON Infotech Pvt. Ltd.										Mumbai Software Programmer								  February 2011 – December 2013
Logistic Software Solution.
YSCON Info Private Ltd.
Responsibility included en
"""

# import re,os
# regex = re.compile(".{1,200}(?=pvt. ltd.|private ltd.|pvt. limited|private limited)", re.IGNORECASE)
# dmatch = re.findall(regex,strDocumemtText)
# print dmatch


testDocument = ""
def BaseEducation(a,b):
	import textract
	import re
	global testDocument
	testDocument = textract.process("ResumeForPilotCheck/"+a)
	regex = re.compile(b)
	dmatch=re.findall(regex,testDocument)
	if(len(dmatch)>0):
		position = [(m.start(0), m.end(0)) for m in re.finditer(regex, testDocument)]
		# print  testDocument[position[0][0]:position[-1][0]+150]
		return position[0][0]
	else:
		return testDocument[0:-1]

def GetAllTags(a):
	import xml.etree.ElementTree as ET
	headerstree = ET.parse('headers.tnset')
	headersroot = headerstree.getroot()
	for educationHeader in headersroot.findall('educationHeader'):
		educationHeaderText = educationHeader.text
	RegEducationHeads = educationHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").strip()
	
	for employmentHeader in headersroot.findall('employmentHeader'):
		employmentHeaderText = employmentHeader.text
		RegEmploymentHeads = employmentHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").strip()

	educationStart = BaseEducation(a,RegEducationHeads)
	employementStart = BaseEducation(a,RegEmploymentHeads)
	print employementStart,educationStart
	if(educationStart<employementStart):
		print "Education Block"
		# print testDocument
		return [{"education":testDocument[educationStart:employementStart],"employement":testDocument[employementStart:]}]
	else:
		print "Employee Block"
		return [{"education":testDocument[educationStart:],"employement":testDocument[employementStart:educationStart]}]

# path = 'ResumeForPilotCheck/' 
# files = os.listdir(path)
# myfiles = [i for i in files if i.endswith('.docx')]
# print myfiles[6]

# print GetAllTags(myfiles[6])





import re
sss = '''Email: asmita.godse@gmail.com cknd njjnfdfd
					Loc ation : Mumbai lob (fhh) thingamabob skmf'''

# regex = re.compile("(?<!\S)(" + 'dfjhf|sd|Mumbai|Loc ation|godse|njjn' + ")(?!\S)", re.I|re.M)
regex = re.compile("[\(]?(fhh)[\)]?", re.I|re.M)

dmatch = re.findall(regex,sss)
print dmatch