# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re
from nerForCompany import OrgNER
import glob, os, json
BASE = os.path.dirname(os.path.abspath(__file__))
class GenericResumeParser(object):
	"""
	Resume parser: It gives education details,
	Employement history, Skills

	"""
	def __init__(self,restext):
		self.headersroot = ET.parse(BASE+'/ListData2/headers.zhrset').getroot()
		self.degreesroot = ET.parse(BASE+'/ListData2/degrees.zhrset').getroot()
		self.functionalroot = ET.parse(BASE+'/ListData2/functionalareas.zhrset').getroot()
		self.designationroot = ET.parse(BASE+'/ListData2/designation.zhrset').getroot()
		self.employerroot = ET.parse(BASE+'/ListData2/employer.zhrset').getroot()
		self.institutionroot = ET.parse(BASE+'/ListData2/institution.zhrset').getroot()
		self.skillsetroot = ET.parse(BASE+'/ListData2/skillset.zhrset').getroot()
		self.ResumeText = restext		
	

	def BaseSections(self,headRegex):
		testDocument = self.ResumeText
		# print re.escape(headRegex)
		regex = re.compile(headRegex,re.I|re.M)
		# print regex
		dmatch=re.findall(regex,testDocument)
		# print dmatch
		if(len(dmatch)>0):
			position = [(m.start(0), m.end(0)) for m in re.finditer(regex, testDocument)]
			if(len(position)==1):
				# print testDocument[position[0][0]:]
				return testDocument[position[0][0]:]
			# print testDocument[position[0][0]:position[-1][0]+250]
			return testDocument[position[0][0]:position[-1][0]+300]
		else:
			return testDocument[0:]

	def CompanyBaseSections(self,headRegex):
		testDocument = self.ResumeText
		# print re.escape(headRegex)
		regex = re.compile(headRegex,re.I|re.M)
		# print regex
		dmatch=re.findall(regex,testDocument)
		# print dmatch
		if(len(dmatch)>0):
			position = [(m.start(0), m.end(0)) for m in re.finditer(regex, testDocument)]
			return testDocument[position[0][0]:]
		else:
			return testDocument[0:]
	
	def EducationParser(self):
		# get specific heders 
		for educationHeader in self.headersroot.findall('educationHeader'):
			educationHeaderText = educationHeader.text
		RegEducationHeads = educationHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").strip()
		# print RegEducationHeads
		# get specific lists
		degreesElement = self.degreesroot.findall('d')
		instituteElement = self.institutionroot.findall('i')		
		# get document section from headers
		strDocumemtText = self.BaseSections(RegEducationHeads)
		degreeList = []
		institutionList = []
		passingYearList = []
		instindexP = 0
		instindexN = 0
		for degrees in degreesElement:
			isDegreefound = False
			for variant in degrees.findall('v'):
				if(isDegreefound):
					break
				regex = re.compile("[\s\n\r\t\)\(,\-]" + re.escape(variant.text.replace("&amp;", "&")) + "[\s\n\r\t\)\(\.,\-]", re.I|re.M)
				m = regex.search(strDocumemtText)
				if(m):
					isDegreefound = True
					degreeList.append(degrees.attrib["key"])
					instindexP = 0 if m.span()[0]-50 < 0 else m.span()[0]-50 
					instindexN = len(strDocumemtText) if m.span()[0]+50 > len(strDocumemtText) else m.span()[0]+50
					probebalyear = strDocumemtText[instindexP:instindexN]
					print variant.text.replace("&amp;", "&")
					probebalyear2 =  [line for line in strDocumemtText.split('\n') if variant.text.replace("&amp;", "&").lower() in line.lower()]
					# print probebalyear2
					if(len(probebalyear2)>0):
						probebalyear = probebalyear2[0].strip()
						if(len(probebalyear)<len(variant.text.replace("&amp;", "&"))+10):
							probebalyear = strDocumemtText[m.span()[0]:instindexN]
					print probebalyear
					regex = re.compile("([\d]{4})\s*\-*[to|till|upto]*\s*([\d]{4}|\-[\d]{2})*", re.IGNORECASE)
					passingYearList.append(re.findall(regex,probebalyear))
					isInsitutefound = False
					inStituteFoundName = "None"
					for institutions in instituteElement:
						if(isInsitutefound):
							break
						for instivariant in institutions.findall('v'):
							regex = re.compile("[\s\n\r\t\)\(\.,\-]" + re.escape(instivariant.text.replace("&amp;", "&").strip()) + "[\s\n\r\t\)\(\.,\-]", re.I|re.M)
							if(regex.search(probebalyear)):
								inStituteFoundName = institutions.attrib["key"]
								isInsitutefound = True  
								break
					institutionList.append(inStituteFoundName)  

		data = []
		# print passingYearList
		# print degreeList
		# print institutionList
		if(len(degreeList)==0):
			data.append("None")
			data.append("None")
			data.append("None")
			data.append("None")
		for d in range(len(degreeList)):
			if(degreeList[d]!=""):
				data.append(degreeList[d])
			else:
				data.append("None")
			if(d<len(institutionList)):
				if(institutionList[d]):
					data.append(institutionList[d])
				else:
					data.append("None")
			else:
				data.append("None")
			if(d<len(passingYearList)):
				if(passingYearList[d] and passingYearList[d][0][0]!=""):
					data.append(passingYearList[d][0][0])
				else:
					data.append("None")	
				if(passingYearList[d] and passingYearList[d][0][1]!=""):
					data.append(passingYearList[d][0][1])
				else:
					data.append("None")	
			else:
				data.append("None")
				data.append("None")
		data.append(strDocumemtText)
		return data


	def check_data(self,data,AlEmpList):
		mycomp=[]
		for k in AlEmpList:
			if k.lower() in data:
				mycomp.append(k)
		return mycomp
	
	def CompanyNamesFromNER(self,docSection):
		OrgfromNer = OrgNER(docSection.lower())
		OrgLists = [[x[1].encode('utf-8'),int(x[2].encode('utf-8'))] for x in OrgfromNer ]
		OrgCompleteList = []
		for Org in OrgLists:
			instindexP = Org[1]
			instindexN = len(docSection) if Org[1]+100> len(docSection) else Org[1]+100
			probebalExp = docSection
			regex = re.compile(re.escape(Org[0][:6])+"[\s\r\t\n]*.*?(Duration|Since|From|Working For|Workingfrom)?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{1,4})\s*(\-{1,3}|/|\s|to|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?\s*((\s|\n|\-{1,3}|\.|,|’|'|‘|/|\d{1,4})*\\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)*\\b(\s|\n|\-{1,3}|\.|,|’|'|‘|)*\d{1,4}|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?", re.IGNORECASE)		
			res = re.findall(regex,probebalExp)		
			if(len(res)>0):
				# print res[0][1]
				try:
					# print Org[0], res[0][1]
					# print res
					OrgCompleteList.append(Org[0])
					if res[0][1].strip() !="":
						OrgCompleteList.append(res[0][1].strip())
					else:
						OrgCompleteList.append("None")
					
					if res[0][5].strip() !="":
						OrgCompleteList.append(res[0][5].strip())
					else:
						OrgCompleteList.append("None")
				except UnicodeEncodeError:
					print i, "Failed"
		return OrgCompleteList

	def ExperienceParser(self):
		# get specific heders
		for employmentHeader in self.headersroot.findall('employmentHeader'):
			employmentHeaderText = employmentHeader.text
		RegEmploymentHeads = employmentHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").strip()
		
		# get specific lists
		empdesigroot = ET.parse(BASE+'/ListData2/employer.zhrset').getroot()
		empElement = empdesigroot.findall('emp')
		AlEmpList = []
		for i in empElement:
			AlEmpList.append(i.text.replace("&amp;", "&"))
		strDocumemtText = self.CompanyBaseSections(RegEmploymentHeads)
		# Extract_Org(strDocumemtText)
		EmplList = []
		ExpList = []
		instindexP = 0
		instindexN = 0
		OrgCompleteList = []
		OrgCompleteList.extend(self.CompanyNamesFromNER(strDocumemtText))
		# print OrgCompleteList
		emplists = self.check_data(strDocumemtText.lower(),AlEmpList)
		for emp in emplists:
				regex = re.compile("[\s\n\r\t\)\(\.,\-]" + re.escape(emp.replace("&amp;", "&")) + "[\s\n\r\t\)\(\.,\-]", re.IGNORECASE)
				m = regex.search(strDocumemtText)
				if(m):
					EmplList.append(emp)
					instindexP = 0 if m.span()[0]-50 < 0 else m.span()[0]-50 
					instindexN = len(strDocumemtText) if m.span()[0]+50 > len(strDocumemtText) else m.span()[0]+50
					probebalExp = strDocumemtText[instindexP:instindexN]
					regex = re.compile("[\s\r\t\n]*.*?(Duration|Since|From|Working For|Workingfrom)?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{1,4})\s*(\-{1,3}|/|\s|to|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?\s*((\s|\n|\-{1,3}|\.|,|’|'|‘|/|\d{1,4})*\\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)*\\b(\s|\n|\-{1,3}|\.|,|’|'|‘|)*\d{1,4}|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?", re.IGNORECASE)
					ExpList.append(re.findall(regex,probebalExp))
		data = []
		# print EmplList

		for d in range(len(EmplList)):
			if(EmplList[d]!=""):
				data.append(EmplList[d])
			else:
				data.append("None")
			if(d<len(ExpList)):
				if(ExpList[d]):
					if(ExpList[d][0][0]!=""):
						data.append(ExpList[d][0][0])
					else:
						data.append("None")
				else:
					data.append("None")	
				if(ExpList[d]):
					if(ExpList[d][0][1]!=""):
						data.append(ExpList[d][0][1])
					else:
						data.append("None")
				else:
					data.append("None")	
			else:	
				data.append("None")
				data.append("None")
		OrgCompleteList.extend(data)
		if(len(OrgCompleteList)==0):
			OrgCompleteList.append("None")
			OrgCompleteList.append("None")
			OrgCompleteList.append("None")

		OrgCompleteList.append(strDocumemtText)
		return OrgCompleteList

		

	def compSkills(self, list1, list2):
		from CommonClassObject import SkillsDetails
		SkillSetDataList = []
		for val in list1:
			if val.lower() in list2:
				skillfreq = str(list2.count(val.lower()))				
				skillobj = SkillsDetails()
				skillobj.skillname = val.lower()
				skillobj.frequency = skillfreq 
				SkillSetDataList.append(skillobj)
		return SkillSetDataList
	
	def SkillsParser(self):
		# get specific lists
		SkillsElementRegex = '|'.join(re.escape(x.strip()) for x in str(self.skillsetroot.find('./itskills').text).split(','))
		regex = re.compile(SkillsElementRegex, re.IGNORECASE)
		dmatch = re.findall(regex,self.ResumeText)
		# print SkillsElementRegex
		return dmatch


	def ToJSON(self,skills):
		mySkillList = [x.strip() for x in str(self.skillsetroot.find('./itskills').text).split(',')]
		mySkillVector = self.compSkills(mySkillList,[y.lower() for y in skills])
		return mySkillVector
	
	def GetPhoneNumber(self):
		from phoneParser import GetMaxTwoPhoneNumbers
		print GetMaxTwoPhoneNumbers(self.ResumeText)

	def AllParsersCall(self):
		ParsedDetails = {}
		# ParsedDetails["Education"] = self.EducationParser()
		ParsedDetails["Experience"] = self.ExperienceParser()
		# ParsedDetails["Skills"] = self.SkillsParser()
		ParsedDetails["Education"] = []
		# ParsedDetails["Experience"] = []
		ParsedDetails["Skills"] = []
		# self.GetPhoneNumber()

		# print ParsedDetails["Skills"]
		# myskillsjson = self.ToJSON(ParsedDetails["Skills"])
		# print json.dumps([ob.__dict__ for ob in myskillsjson])
		return ParsedDetails
		
	





##   Structure of output

# {
# 	"CandidateData": [{
# 		"SrNo": "1",
# 		"PersonnelDetails": [{
# 			"CandidateName": "DharaK Pratap Mehta",
# 			"Contact1": "9998999989",
# 			"Contact2": "9998999989",
# 			"EmailId1": "dharak@gmail.com",
# 			"EmailId2": "dharak@gmail.com",
# 			"DateOfBirth": "14 Oct 1976",
# 			"Gender": "Male",
# 			"Address": "",
# 			"City": "",
# 			"State": "",
# 			"Country": "",
# 			"PanNo": "",
# 			"PassportNo": "",
# 			"ResumeInBase64String": "UEsDBBQABgAIAAAAIQDTEdb",
# 			"ResumeFileType": ".docx",
# 			"ResumeInPlainText": "this is a sample resume text",
# 			"SourcingDetails": "LinkedIn"
# 		}],
# 		"SkillSetDetails": [
#			{
# 				"SkillName": "JavaScript",
# 				"Frequency": 4
# 			}, 
#			{
# 				"SkillName": "SQLScript",
# 				"Frequency": 5
# 			}
# 		],
# 		"QualificationsDetails": [{
# 			"HighestQualificationDegree": "MCA",
# 			"QualificationData": [{
# 				"InstitutionName": "Ahmedabad Management Association",
# 				"DegreeName": null,
# 				"YearOfPassing": null
# 			}, {
# 				"InstitutionName": "Ahmedabad Management Association",
# 				"DegreeName": null,
# 				"YearOfPassing": null
# 			}]
# 		}],
# 		"EmploymentsHistoryDetails": [{
# 			"ExperianceInMonth": "35",
# 			"EmploymentHistoryData": [{
# 				"Organization": "Gateway TechnoLabs Pvt. Ltd. (Gateway Group of Companies)",
# 				"FromPeriod": null,
# 				"ToPeriod": null,
# 				"Designation": "Asst. Manager-HR"
# 			}, {
# 				"Organization": "Gateway TechnoLabs Pvt. Ltd. (Gateway Group of Companies)",
# 				"FromPeriod": null,
# 				"ToPeriod": null,
# 				"Designation": "Asst. Manager-HR"
# 			}]
# 		}]
# 	}]
# }		


###