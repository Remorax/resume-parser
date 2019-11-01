import xml.etree.ElementTree as ET
import re, datetime
import glob, os, json
import csv
from nerForCompany import OrgNER
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
class GenericResumeParser(object):
	"""
	Resume parser: It gives education details,
	Employement history, Skills

	"""

	def __init__(self,restext):
		self.headersroot = ET.parse(BASE+'/ListData2/headers.zhrset').getroot()
		self.headersroot2 = ET.parse(BASE+'/ListData2/headers2.zhrset').getroot()
		self.degreesroot = ET.parse(BASE+'/ListData2/degrees.zhrset').getroot()
		self.functionalroot = ET.parse(BASE+'/ListData2/functionalareas.zhrset').getroot()
		self.designationroot = ET.parse(BASE+'/ListData2/designation.zhrset').getroot()
		self.employerroot = ET.parse(BASE+'/ListData2/employer.zhrset').getroot()
		self.employerroot3 = ET.parse(BASE+'/ListData2/employerNew.zhrset').getroot()
		self.institutionroot = ET.parse(BASE+'/ListData2/institution.zhrset').getroot()
		self.skillsetroot = ET.parse(BASE+'/ListData2/skillset.zhrset').getroot()		
		self.ResumeText = restext
		self.DurationRegex = r"[\s\\r\\t\\n]*.*?(Duration|Since|From|Working For|Workingfrom)?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{1,4})\s*(\-{1,3}|/|\s|to|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?\s*((\s|\\n|\-{1,3}|\.|,|’|'|‘|/|\d{1,2}|\d{1,4})*.*\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)*\b(\s|\\n|\-{1,3}|\.|,|’|'|‘|)*\d{1,4}|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?"		
		self.dateStringRegex = r"(\,)?(\()?( |\(|\)|\,|\.|\:|\-|\:\-|\-\:|\;|\&|^)((((Since|From|Working from)?( )?((((\d{1,2}(rd|st|nd|th)?( )?( |\/|\\|\.|\-|\–)( )?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b|((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?(\d{1,2}(th|rd|st|nd)?( )?( |\/|\\|\.|\-|\–)( )?)?))( )?( |\-{1,3}|\–{1,3}|\.|,|’|'|‘)+( )?\d{2}(\d{2})?(\'|\’)?( )?)|((\d{1,2}(rd|st|nd|th)?( )?( |\/|\\|\.|\-)( )?)?\d{1,2}( )?(\/|\\|\-|\–)( )?\d{2}(\d{2})?)|((\d{2}(\d{2})?)( )?(\/|\\|\-|\–)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?)))(( )?(\-{1,3}|\/| |\–{1,3}|to|till|to till)*( )?((((((\d{1,2}(rd|st|th|nd)?( )?( |\/|\\|\.|\-|\–)( )?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December))|((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?(\d{1,2}(th|rd|st|nd)?( )?( |\/|\\|\.|\-|\–)( )?)?))( )?( |\-{1,3}|\–{1,3}|\.|,|’|'|‘|\/|\\)+( )?\d{2}(\d{2})?(\'|\’)?( )?))|(date|now|the date|present|present date|the present date|to till date|till date|today|current)|((\d{1,2}(rs|st|nd)?( )?( |\/|\\|\.|\-|\–)( )?)?\d{1,2}( )?( |\/|\\|\.|\-|\–)( )?\d{2}(\d{2})?)|((\d{2}(\d{2})?)( )?(\/|\\|\.|\-|\–)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?)))?)|((\d{2}(\d{2})?( )?(\-{1,3}|\/| |\–{1,3}|to|till|to till)+( )?((date|now|the date|present|present date|the present date|to till date|till date|t til date|today|current)|(\d{2}(\d{2})?))))|((Since|From|Working from|Currently working)(\d{2}(\d{2})?))|((for|from|for a duration of|since|till|to till)\d{1,2}( )(months))|(\d{1,2}( )(months|month|year|years)( )(work|as)))(\))?( |\(|\)|\,|\.|\:|\-|\:\-|\-\:|\;|$)"
		self.dateRegex = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\–{1,3}|\.|,|’|'|‘)*\d{2}(\d{2})?)|\b(\d{1,2}(\s|\/|\\|\.|\-|\–)\d{2}(\d{2})?)( |\))"
		self.dateRegex2 = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)( )\b\d{1,2}( )?(\s|\-{1,3}|\–{1,3}|\.|\,|’|'|‘)*( )?\d{2}(\d{2})?)\b"
		self.dateRegex3 = r"\b(\d{2}(\d{2})?)( )?(\/|\\|\.|\-|\–)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b"
		self.designationRegex = r"(Job Title|Designation|Position|Role|Working\s*as\s*a|Working\s*as\s*an|Worked\s*as\s*an|Worked\s*as\s*a|Promoted\s*to\s*a|Promoted\s*to\s*an|Promoted\s*to|Worked\s*as|Working\s*as|Work\s*as|Work\s*as\s*a|Work\s*as\s*an)\s*\d{0,2}\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.designationRegex2 =r"\s*(as|as\s*a|as\s*an|Profile|Profile\s*\&\s*Product)\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.bodyDesignationRegex = r"^(?!.*(Reporting to|Reporting|Submitting|Publishing the errors for|Leading a team of|Directing a|Meeting with|Profitable Champ|Key Responsibilities as an|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?(and)?\b"	
		self.articles = ['a', 'an', 'of', 'the', 'is', 'in', 'and']

	def writeToCompanyMaster(self, CompanyList):
		myfile = open("companyMaster.txt", "a")
		for company in CompanyList:
			myfile.write("%s\n" % company)
		myfile.close()

	def writeToDesignationMaster(self, DesgList):
		myfile = open("designationMaster.txt", "a")
		for desg in DesgList:
			myfile.write("%s\n" % desg)
		myfile.close()	
		
	def rreplace(self, s, old, new, occurrence):
		li = s.rsplit(old, occurrence)
		return new.join(li)
	
	def FormatDate(self,date):
		if(date!="None" or date!="" ):
			if(date.lower() in ['onwards','till date','till now','till the date','till present','present','till today','till','date','continue']):
				date = datetime.date.today().strftime("%b-%Y")
				return date.capitalize()
			date = re.sub("(\s|\-{1,3}|\–{1,3}|\.|,|’|'|‘)", '$', date)
			y = date.split("$")
			y = [x for x in y if x.strip()!=""]
			if(len(y)==3):
				if(int(y[0].replace("th","").replace("rd","").replace("st","").replace("nd","")) in range(1,32)):
					y.pop(0)
				else:
					y.pop(1)
			if(len(y)>1):
				year = y[1].strip()			
			else:
				return date.capitalize()
			if(len(year)==2):
				if(int(year)<60):
					year = "20"+year
				else:
					year = "19"+year
			if(len(y[0])>3):
				y[0] = y[0][0:3]
			date = y[0].strip()+'-'+year.strip()
			return date.capitalize()

	def title_except(self, s, exceptions):
		word_list = re.split(' ', s)
		final = [word_list[0].capitalize()]
		for word in word_list[1:]:
			final.append(word if word in exceptions else word.capitalize())
		return " ".join(final)

	def returnListforCSV(self, finalList):
		CSVList = []
		for finalListElem in finalList:
			Company = finalListElem['Organization']
			for expDictElem in finalListElem['WorkExperience']:
				FromPeriod = expDictElem['FromPeriod']
				FromDate = FromPeriod['Date']
				ToPeriod = expDictElem['ToPeriod']
				ToDate = ToPeriod['Date']
				ExpMonths = expDictElem['totalMonthsOfExperience']
				desgString = ','.join(expDictElem['DesignationList'])
				CSVList.extend((Company,FromDate,ToDate,desgString,ExpMonths))
		return CSVList		

	def CompanyBaseSections(self,headRegex):
		testDocument = self.ResumeText
		#regex = re.escape("(\r|\n|\t)( )*("+headRegex+")( )*( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\r|\n|\t)")
		regex = re.compile(r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\\r|\\n|\\t)",re.M)
		headRegex2List = []
		headRegex3List = []
		for header in headRegex:
			headRegex2List.append(header.upper())
			headRegex3List.append(self.title_except(header, (self.articles)))
		headRegex2List = list(set(headRegex2List))
		headRegex2 = '|'.join(headRegex2List)
		headRegex3List = list(set(headRegex3List))
		headRegex3 = '|'.join(headRegex3List)	
		regex2 = re.compile(r"("+headRegex2+r")( )*( |\:|\-|\-( )*\:|\:( )*\-|\>|\-\>)?( )*",re.M)
		regex3 = re.compile(r"("+headRegex3+r")( )*( |\:|\-|\-( )*\:|\:( )*\-|\>|\-\>)?( )*",re.M)
		dmatch=re.findall(regex,testDocument)
		if(len(dmatch)>0):
			position = [(m.start(0), m.end(0), m.group()) for m in re.finditer(regex, testDocument)]
			position = sorted(position, key=lambda x: x[0])
			ans = position[0][0]
			ansTitle = position[0][2]
			for tupleelem in position:
				restext = self.ResumeText[tupleelem[0]:(tupleelem[1]+1)]
				upperRestext = restext.upper()
				if (restext == upperRestext):
					ans = tupleelem[0]
					ansTitle = tupleelem[2]
					break		
			return (ans,3,ansTitle)
		else:
			position = [(m.start(0), m.end(0), m.group()) for m in re.finditer(regex2, testDocument)]
			position = sorted(position, key=lambda x: x[0])
			if(position):
				return (position[0][0],2,position[0][2])
			else:
				position = [(m.start(0), m.end(0),m.group()) for m in re.finditer(regex3, testDocument)]
				position = sorted(position, key=lambda x: x[0])
				if(position):
					return (position[0][0],1,position[0][2])
			return (0,0,"")

	def RemoveLowerCase(self, RegEmploymentHeads):
		returnList = []
		RegList = RegEmploymentHeads.split('|')
		for (n,i) in enumerate(RegList):
			returnList.append(i.upper())
			returnList.append(self.title_except(i, (self.articles)))
			returnList.append(i.capitalize())	
		returnList = list(set(returnList))
		RegEmploymentHeads = '|'.join(returnList)
		return (RegEmploymentHeads)

	def getHeader(self, headerString):
		for employmentHeader in self.headersroot2.findall(headerString):
			employmentHeaderText = employmentHeader.text
		RegEmploymentHeads = employmentHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").replace("&amp;","&").replace("/","\/").strip()
		RegEmploymentHeads = self.RemoveLowerCase(RegEmploymentHeads)
		return RegEmploymentHeads	

	def removeSpecialChars(self, string):
		RegexObj = re.compile(r"\b.*\b",re.I|re.M)
		RegexList = [(m.group()) for m in re.finditer(RegexObj,string.strip())]
		return RegexList[0]

	def designationTenureParser(self):
		allBlocksList = []
		result = self.CompanyBaseSections(self.getHeader('educationHeader'))
		allBlocksList.append({'BlockName':"Education",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('accomplishmentsHeader'))
		allBlocksList.append({'BlockName':"Accomplishments",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('awardsHeader'))
		allBlocksList.append({'BlockName':"Awards",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('extracurricularHeader'))
		allBlocksList.append({'BlockName':"ExtraCurricular Activities",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('miscHeader'))
		allBlocksList.append({'BlockName':"Miscellaneous",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('summaryHeader'))
		allBlocksList.append({'BlockName':"Summary",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('skillsHeader'))
		allBlocksList.append({'BlockName':"Skills",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('employmentHeader'))
		allBlocksList.append({'BlockName':"Employment",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('credibilityHeader'))
		allBlocksList.append({'BlockName':"Credibility",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
		for (i,Block) in enumerate(allBlocksList):
			if(Block['StartingIndex'] == 0):
				Block['EndingIndex']=(len(self.ResumeText)-1)
				Block['BlockText']=self.ResumeText
			else:
				if(i!=8):
					nextBlock = allBlocksList[i+1]
					Block['EndingIndex']=nextBlock['StartingIndex']
				else:
					Block['EndingIndex']=len(self.ResumeText)-1
				Block['BlockText']=self.ResumeText[int(Block['StartingIndex']):int(Block['EndingIndex'])]
		for (i,Block) in enumerate(allBlocksList):
			if(Block['StartingIndex']!=0):
				if(Block['BlockName']=='Employment'):
		 			employmentBlock = Block['BlockText']
		 			employmentBloc = Block
		 			employmentBlockIndex = i
		if ('employmentBlock' not in locals()):
			employmentBlockRegexObj = re.compile(r"(\\r|\\n)\s*(\u2022|\u2023|\u25E6|\u2043|\u2219)?("+self.getHeader('employmentHeader')+r")\s*(\d{1,2})( |\:|\-|\-(\s)?\:|\:(\s)?\-|>|\-\s*\>|\d{1,2})?( )?\s*(\\r|\\n)",re.M)
			employmentBlockL = [(m.group(),m.start(),m.end()) for m in re.finditer(employmentBlockRegexObj,self.ResumeText)]
			employmentBlock = employmentBlockL[0][0]
			for (i,Block) in enumerate(allBlocksList):
				if(Block['StartingIndex']==0):
					if(Block['BlockName']=='Employment'):
						numberToFind = employmentBlockL[0][1]
						for (j,Bock) in enumerate(allBlocksList):
							if(j!=len(allBlocksList)-1):
								if((allBlocksList[j]['StartingIndex']<=numberToFind) and (allBlocksList[j+1]['StartingIndex']>=numberToFind)):
									ans = allBlocksList[j+1]['StartingIndex']
									ansIndex = j
									break
							else:
								ans = -1
						Block['StartingIndex'] = numberToFind
						if(ans!=-1):
							Block['BlockText']=self.ResumeText[int(Block['StartingIndex']):int(ans)]
							Block['EndingIndex']=ans
						else:
							Block['BlockText']=self.ResumeText[int(Block['StartingIndex']):]
							Block['EndingIndex']=len(self.ResumeText)-1	
						Block['BlockText']=self.ResumeText[int(Block['StartingIndex']):int(Block['EndingIndex'])]
						employmentBlock = Block['BlockText']
						employmentBloc = Block
						employmentBlockIndex = j
			allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
		Titles = []
		with open('designationMaster.txt') as file:
			for line in file: 
				line = line.strip()
				Titles.append(line)
		Titles = list(set(Titles))
		Titles = sorted(Titles, key=len, reverse=True)
		for (i,title) in enumerate(Titles):
			titleWords = title.split()
			Titles[i] = ' '.join(titleWords)
		Companies = [] 
		#self.writeToCompanyMaster(['Zodiac Clothing Company Ltd','Live Wire Call Centre','ATS Services Pvt\. Ltd'])
		#self.writeToDesignationMaster(['Article','Van Sales Representative'])
		with open('companyMaster.txt') as file:
			for line in file: 
				line = line.strip()
				Companies.append(line)
		justTrying = re.sub(r'\\x\w{1,2}','',employmentBlock)
		justTrying = justTrying.replace('\\n','\n').replace('\\t','\t').replace('\\r','\r')
		originalEmpBlock = justTrying
		employmentBlock = re.split(r'\\n|\\r|\\t|\s|\\x\w{1,2}',employmentBlock)
		employmentBlock = list(filter(None, employmentBlock))
		tempEmpBlock = ' '.join(employmentBlock)
		NERCompanyList = OrgNER(tempEmpBlock)	
		Companies = sorted(list(set(Companies)), key=len, reverse=True)	
		CompanyRegex = r"(\,|M\/S)?( |\-|\.|\–|\()(" + '|'.join(Companies) + r")( |\.|\,|\;|\(|\)|\.\:)"
		TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
		TitlesRegex = r"( )?( |\,|\;|\-|\"|\-|\:|\.|\()( )?(" + TitlesRegex + r")(\,|\;|\-)?\b"
		compRegexObj = re.compile(CompanyRegex, re.I|re.M)
		companyList = [{"Company": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(compRegexObj, tempEmpBlock)]
		companyList.sort(key=lambda x: x["StartIndex"])
		for (cmpindex,company) in enumerate(companyList):
			CompanyName = company["Company"]
			start = 0
			while not CompanyName[start].isalpha():
				start+=1
			companyList[cmpindex]["StartIndex"] += start	
			end = len(CompanyName) - 1
			while not CompanyName[end].isalpha():
				end-=1
			companyList[cmpindex]["EndingIndex"] -= (len(CompanyName)-1-end)
			companyList[cmpindex]["Company"] = self.removeSpecialChars(company["Company"])
		#print (companyList)	
		companyStEndTuple = [(company["StartIndex"],company["EndingIndex"]) for company in companyList]
		companyStEndTuple.sort(key=lambda x: x[0])
		#print (NERCompanyList)
		#print ("*****\n\n\n\n",companyList,"\n\n\n\n*****")
		nerCompany = []
		#companyList = []
		if (not companyList):
			print ("NOOOO")
			companyList = [{"Company": m[1], "StartIndex": int(m[2]), "EndingIndex": int(m[2]) + int(m[3]) - 1} for m in NERCompanyList]
			nerCompany = [m[1] for m in NERCompanyList]
			#print (companyList,nerCompany)
		else:
			for nerComp in NERCompanyList:
				print (nerComp)
				start = 0
				nerCompName = nerComp[1]
				nerCompStart = int(nerComp[2]) #110
				nerCompEnd = nerCompStart + int(nerComp[3]) - 1 #123
				CompMasterList = [item for item in companyStEndTuple if item[0] == nerCompStart]
				if(CompMasterList):
					compTuple = CompMasterList[0]
					compTupleIndex = companyStEndTuple.index(compTuple)
					compTupleEndingIndex = compTuple[1]
					if(compTupleEndingIndex<nerCompEnd):
						companyList[compTupleIndex] = {"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd}
						print ("1")
						nerCompany.append(nerCompName)
				else:
					flag=0
					for (i,stEndTuple) in enumerate(companyStEndTuple):
						#print (stEndTuple)
						if(i!=(len(companyStEndTuple)-1)):
							if nerCompStart>companyStEndTuple[i][1] and nerCompEnd<companyStEndTuple[i+1][0]:								
								flag=1
								#print (nerCompName)
								companyList.insert((i+1),{"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd})
								print ("2")
								nerCompany.append(nerCompName)
								break
					if(flag==0):
						for (i,stEndTuple) in enumerate(companyStEndTuple):
							if nerCompStart>=companyStEndTuple[i][0] and nerCompStart<companyStEndTuple[i][1] and nerCompEnd>companyStEndTuple[i][1]:								
								flag=1
								companyList[i] = {"Company":tempEmpBlock[companyStEndTuple[i][0]:(nerCompEnd+1)],"StartIndex":companyStEndTuple[i][0],"EndingIndex":nerCompEnd}
								print("3")
								nerCompany.append(tempEmpBlock[companyStEndTuple[i][0]:(nerCompEnd+1)])
								break
		print (companyList,"\n\n\n",nerCompany,"\n\n\n\n")
		Companies.extend(nerCompany)
		self.writeToCompanyMaster(nerCompany)
		Companies = sorted(list(set(Companies)), key=len, reverse=True)	
		companyList.sort(key=lambda x: x["StartIndex"])					
		firstCompany = companyList[0]["Company"]
		firstCompanyStart = companyList[0]["StartIndex"]
		TitleLength = len(employmentBloc["BlockTitle"].strip())
		textBeforeCompany = tempEmpBlock[TitleLength:firstCompanyStart]
		finalList= []
		isRubbish = 0
		companySubBlocks = []
		if textBeforeCompany:
			DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
			DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
			if (not textBeforeCompany.startswith(' ')):
				textBeforeCompany = ' ' + textBeforeCompany
			if (not textBeforeCompany.endswith(' ')):
				textBeforeCompany = textBeforeCompany + ' '
			DateList = [{"Date": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, textBeforeCompany)]
			DesgList = [{"Designation": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textBeforeCompany)]
			if (DateList or DesgList):
				if(DateList and DesgList):
					isRubbish = -1
				elif(DateList):
					isRubbish = 0
				else:
					isRubbish = 2		
			else:
				isRubbish = 1				
		if ((not textBeforeCompany) or (isRubbish==1)):
			curr = 0
			for (i,company) in enumerate(companyList):
				if (i!=(len(companyList)-1)):
					possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:companyList[i+1]["StartIndex"]]
				else:
					possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:]	
				DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
				DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
				DateList = [{"Date": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
				DesgList = [{"Designation": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
				if (DateList and DesgList):
					if(DateList[0]["StartIndex"]<DesgList[0]["StartIndex"]):
						for (j,date) in enumerate(DateList):
							if(j!=(len(DateList)-1)):
								areaToScan = possibleSubBlock[DateList[j]["EndingIndex"]:DateList[j+1]["StartIndex"]]
								if(not areaToScan.startswith(' ')):
									areaToScan = ' ' + areaToScan
								if(not areaToScan.endswith(' ')):
									areaToScan = areaToScan + ' '
								DateList[j]["AreaToScan"] = areaToScan	
								DateList[j]["AreaToScanFlag"] = 1			
							else:
								areaToScan = possibleSubBlock[DateList[j]["EndingIndex"]:]
								if(not areaToScan.startswith(' ')):
									areaToScan = ' ' + areaToScan
								if(not areaToScan.endswith(' ')):
									areaToScan = areaToScan + ' '
								TitlesRegex	= '|'.join(Titles)
								TitlesRegex = r"\b(" + TitlesRegex + r")\b"	
								areaToScanObj = re.compile(TitlesRegex, re.I|re.M)
								areaToScanList = re.findall(areaToScanObj,areaToScan)
								if(not areaToScanList):
									DateList[j-1]["AreaToScanFlag"] = 1
									DateList[j-1]["AreaToScan"] += areaToScan
									DateList.pop(j)
								else:
									DateList[j]["AreaToScanFlag"] = 1		
									DateList[j]["AreaToScan"] = areaToScan
					else:
						for (j,date) in enumerate(DateList):
							if(j!=0):
								areaToScan = possibleSubBlock[DateList[j-1]["EndingIndex"]:DateList[j]["StartIndex"]]
								if(not areaToScan.startswith(' ')):
									areaToScan = ' ' + areaToScan
								if(not areaToScan.endswith(' ')):
									areaToScan = areaToScan + ' '
							else:
								areaToScan = possibleSubBlock[:DateList[j]["StartIndex"]]
								if(not areaToScan.startswith(' ')):
									areaToScan = ' ' + areaToScan
								if(not areaToScan.endswith(' ')):
									areaToScan = areaToScan + ' '
							DateList[j]["AreaToScanFlag"] = 1		
							DateList[j]["AreaToScan"] = areaToScan								
					companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
					curr += 1
				else:
					if(curr!=0):
						companySubBlocks[curr-1]["Text"] += possibleSubBlock
						previousDateList = companySubBlocks[curr-1]["DateList"]	
						previousDateListLength = len(previousDateList)
						previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
						#print (previousDateList[previousDateListLength-1]["AreaToScan"])
									
		else:
			curr = 0
			if(isRubbish==-1):
				TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
				TitlesRegex = r"( )?( |\,|\-|\"|\“|\-|\:|\.|\(|\()( )?(" + TitlesRegex + r")\s*( )?( |\"|\”|\,|\-|\-|\:|\.|\)|\-|\()( )?"
				for (i,company) in enumerate(companyList):
					if (i!=(len(companyList)-1)):
						possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:companyList[i+1]["StartIndex"]]
					else:
						possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:]
					possibleSubBlock = textBeforeCompany + possibleSubBlock
					DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
					DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
					if((DateList[len(DateList)-1])["StartIndex"]<(DesgList[len(DesgList)-1])["StartIndex"]):
						textBeforeCompany = possibleSubBlock[(DateList[len(DateList)-1])["StartIndex"]:]				
					else:
						lastDesg = (DesgList[len(DesgList)-1])
						textBeforeCompany = possibleSubBlock[lastDesg["StartIndex"]:]
					if(i!=(len(companyList)-1)):
						possibleSubBlock = self.rreplace(possibleSubBlock, textBeforeCompany, '', 1)	
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]	
					if (DateList and DesgList):
						if(DateList[0]["StartIndex"]<DesgList[0]["StartIndex"]):
							for (j,date) in enumerate(DateList):
								if(j!=(len(DateList)-1)):
									areaToScan = possibleSubBlock[DateList[j]["EndingIndex"]:DateList[j+1]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									DateList[j]["AreaToScan"] = areaToScan	
									DateList[j]["AreaToScanFlag"] = 1			
								else:
									areaToScan = possibleSubBlock[DateList[j]["EndingIndex"]:]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									TitlesRegex	= '|'.join(Titles)
									TitlesRegex = r"\b(" + TitlesRegex + r")\b"	
									areaToScanObj = re.compile(TitlesRegex, re.I|re.M)
									areaToScanList = re.findall(areaToScanObj,areaToScan)
									if(not areaToScanList):
										DateList[j-1]["AreaToScanFlag"] = 1
										DateList[j-1]["AreaToScan"] += areaToScan
										DateList.pop(j)
									else:
										DateList[j]["AreaToScanFlag"] = 1		
										DateList[j]["AreaToScan"] = areaToScan
						else:
							for (j,date) in enumerate(DateList):
								if(j!=0):
									areaToScan = possibleSubBlock[DateList[j-1]["EndingIndex"]:DateList[j]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
								else:
									areaToScan = possibleSubBlock[:DateList[j]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
								DateList[j]["AreaToScanFlag"] = 1		
								DateList[j]["AreaToScan"] = areaToScan
						companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
						curr += 1
					else:
						if(curr!=0):
							companySubBlocks[curr-1]["Text"] += possibleSubBlock
							previousDateList = companySubBlocks[curr-1]["DateList"]	
							previousDateListLength = len(previousDateList)
							previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
			elif(isRubbish==0):
				TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
				TitlesRegex = r"( )?( |\,|\-|\"|\“|\-|\:|\.|\()( )?(" + TitlesRegex + r")\s*( )?( |\"|\”|\,|\-|\-|\:|\.|\)|\()( )?"
				for (j,company) in enumerate(companyList):
					if (j!=(len(companyList)-1)):
						possibleSubBlock = tempEmpBlock[companyList[j]["StartIndex"]:companyList[j+1]["StartIndex"]]
					else:
						possibleSubBlock = tempEmpBlock[companyList[j]["StartIndex"]:]	
					possibleSubBlock = textBeforeCompany + possibleSubBlock
					DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					if(j!=(len(companyList)-1)):
						textAfterLastDate = possibleSubBlock[(DateList[len(DateList)-1]["EndingIndex"]):]
						DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
						DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textAfterLastDate)]						
						if(not DesgList):
							textToReplace = possibleSubBlock[(DateList[len(DateList)-1]["StartIndex"]):]
							possibleSubBlock = self.rreplace(possibleSubBlock, textToReplace, '', 1)
							textBeforeCompany = textToReplace
						else:
							textBeforeCompany = ''
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
					if (DateList and DesgList):
						if(DateList[0]["StartIndex"]<DesgList[0]["StartIndex"]):
							for (i,date) in enumerate(DateList):
								if(i!=(len(DateList)-1)):
									areaToScan = possibleSubBlock[DateList[i]["EndingIndex"]:DateList[i+1]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									DateList[i]["AreaToScan"] = areaToScan	
									DateList[i]["AreaToScanFlag"] = 1			
								else:
									areaToScan = possibleSubBlock[DateList[i]["EndingIndex"]:]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									TitlesRegex	= '|'.join(Titles)
									TitlesRegex = r"\b(" + TitlesRegex + r")\b"	
									areaToScanObj = re.compile(TitlesRegex, re.I|re.M)
									areaToScanList = re.findall(areaToScanObj,areaToScan)
									if(not areaToScanList):
										DateList[i-1]["AreaToScanFlag"] = 1
										DateList[i-1]["AreaToScan"] += areaToScan
										DateList.pop(i)
									else:
										testList = []
										bodyDesignationRegex = r"^(?!.*(Reporting to|Backup of|Helping the|Reporting|Submitting|Key Responsibilities as an|Responsible for investigation of|Publishing the errors for|Profitable Champ|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?(and)?\b(" + '|'.join(Titles) + r")((?!\S)|((\()|(\/)))" 
										desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
										txt = originalEmpBlock
										wordList = areaToScan.split(' ') 
										while '.' in wordList: wordList.remove('.') 
										while ';' in wordList: wordList.remove(';')
										while ')' in wordList: wordList.remove(')')
										while '(' in wordList: wordList.remove('(')
										while ':' in wordList: wordList.remove(':')
										while '-' in wordList: wordList.remove('-')  
										wordList = list(filter(None, wordList))
										for (index,word) in enumerate(wordList):
											if ('(' in word):
												wordList[index] = wordList[index].replace('(','\(')
											if (')' in word):
												wordList[index] = wordList[index].replace(')','\)')
										orgRegex = ""
										if(len(wordList)<40):
											start = int(len(wordList)/2)
											end  = int(len(wordList) - start)		
										else:
											start = 20
											end = 20
										count = 0	
										while(count<start):
											if(count!=(start-1)):
												orgRegex += (wordList[int(count)] + r"\s*(\)|\.|\,|\-|\&|\:|\;| |\()*\s*")
											else:
												orgRegex += wordList[int(count)]	 
											count += 1
										orgRegex += r"[\d\D]*"
										count = end
										while(count>0):
											if(count!=1):
												orgRegex += (wordList[int(len(wordList)-count)] + r"\s*(\)|\.|\,|\-|\&|\:|\;| |\()*\s*")
											else:
												orgRegex += wordList[int(len(wordList)-count)]
											count -= 1
										orgRegex = orgRegex.strip()
										findOriginalObj = re.compile(orgRegex, re.I|re.M)
										tempSubBlockL = [(m.group()) for m in re.finditer(orgRegex,txt)]
										tempSubBlock = ""
										for whatever in tempSubBlockL:
											tempSubBlock += whatever	
										otherDesg = [(m.group().strip().lower().title()) for m in re.finditer(desgObject2,tempSubBlock)]
										TitlesRegex	= '|'.join(Titles)
										TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|((\()|\-|(\/)))"
										desgObject = re.compile(TitlesRegex, re.I|re.M)
										for desg in otherDesg:
											tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
											testList.extend(tempList)
										if(not testList):
											DateList[i-1]["AreaToScanFlag"] = 1
											DateList[i-1]["AreaToScan"] += areaToScan
											DateList.pop(i)	
										else:	
											DateList[i]["AreaToScanFlag"] = 1		
											DateList[i]["AreaToScan"] = areaToScan
						else:
							for (i,date) in enumerate(DateList):
								if(i!=0):
									areaToScan = possibleSubBlock[DateList[i-1]["EndingIndex"]:DateList[i]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
								else:
									areaToScan = possibleSubBlock[:DateList[i]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
								DateList[i]["AreaToScanFlag"] = 1		
								DateList[i]["AreaToScan"] = areaToScan								
						companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
						curr += 1
					else:
						if(curr!=0):
							companySubBlocks[curr-1]["Text"] += possibleSubBlock
							previousDateList = companySubBlocks[curr-1]["DateList"]	
							previousDateListLength = len(previousDateList)
							previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock

							
			else:
				TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
				TitlesRegex = r"( )?( |\,|\-|\"|\“|\-|\:|\.|\()( )?(" + TitlesRegex + r")\s*( )?( |\"|\”|\,|\-|\-|\:|\.|\)|\()( )?"
				for (j,company) in enumerate(companyList):
					if (j!=(len(companyList)-1)):
						possibleSubBlock = tempEmpBlock[companyList[j]["StartIndex"]:companyList[j+1]["StartIndex"]]
					else:
						possibleSubBlock = tempEmpBlock[companyList[j]["StartIndex"]:]
					possibleSubBlock = textBeforeCompany + possibleSubBlock
					DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					if(j!=(len(companyList)-1)):
						if (not DateList):
							DateRegexObj = re.compile(r"\d{1,2}( )(year|week|month|day)(s)?( )",re.I|re.M)
							DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
						textAfterLastDate = possibleSubBlock[(DateList[len(DateList)-1]["EndingIndex"]):]
						DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
						DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textAfterLastDate)]
						if(not DesgList):
							textBeforeCompany = ''
						else:
							textToReplace = textAfterLastDate[(DesgList[len(DesgList)-1]["StartIndex"]):]
							possibleSubBlock = self.rreplace(possibleSubBlock, textToReplace, '', 1)
							textBeforeCompany = textToReplace					
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
					if (DateList and DesgList):
						if(DateList[0]["StartIndex"]<DesgList[0]["StartIndex"]):
							for (i,date) in enumerate(DateList):
								if(i!=(len(DateList)-1)):
									areaToScan = possibleSubBlock[DateList[i]["EndingIndex"]:DateList[i+1]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									DateList[i]["AreaToScan"] = areaToScan	
									DateList[i]["AreaToScanFlag"] = 1			
								else:
									areaToScan = possibleSubBlock[DateList[i]["EndingIndex"]:]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									TitlesRegex	= '|'.join(Titles)
									TitlesRegex = r"\b(" + TitlesRegex + r")\b"	
									areaToScanObj = re.compile(TitlesRegex, re.I|re.M)
									areaToScanList = re.findall(areaToScanObj,areaToScan)
									if(not areaToScanList):
										DateList[i-1]["AreaToScanFlag"] = 1
										DateList[i-1]["AreaToScan"] += areaToScan
										DateList.pop(i)
									else:
										testList = []
										bodyDesignationRegex = r"^(?!.*(Reporting to|Backup of|Helping the|Reporting|Submitting|Key Responsibilities as an|Responsible for investigation of|Publishing the errors for|Profitable Champ|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?(and)?\b(" + '|'.join(Titles) + r")((?!\S)|((\()|(\/)))"
										desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
										txt = originalEmpBlock
										wordList = areaToScan.split(' ')  
										while '.' in wordList: wordList.remove('.')
										while ';' in wordList: wordList.remove(';')
										while ')' in wordList: wordList.remove(')')
										while '(' in wordList: wordList.remove('(')
										while ':' in wordList: wordList.remove(':')
										while '-' in wordList: wordList.remove('-')   
										wordList = list(filter(None, wordList))
										for (index,word) in enumerate(wordList):
											if ('(' in word):
												wordList[index] = wordList[index].replace('(','\(')
											if (')' in word):
												wordList[index] = wordList[index].replace(')','\)')
										orgRegex = ""
										if(len(wordList)<40):
											start = int(len(wordList)/2)
											end  = int(len(wordList) - start)
										else:
											start = 20
											end = 20
										count = 0	
										while(count<start):
											if(count!=(start-1)):
												orgRegex += (wordList[int(count)] + r"\s*(\)|\.|\,|\&|\:|\-|\;| |\()*\s*")
											else:
												orgRegex += wordList[int(count)]	 
											count += 1
										orgRegex += r"[\d\D]*"
										count = end
										while(count>0):
											if(count!=1):
												orgRegex += (wordList[int(len(wordList)-count)] + r"\s*(\)|\.|\&|\,|\:|\-|\;| |\()*\s*")
											else:
												orgRegex += wordList[int(len(wordList)-count)]
											count -= 1
										findOriginalObj = re.compile(orgRegex, re.I|re.M)
										tempSubBlockL = [(m.group()) for m in re.finditer(orgRegex,txt)]
										tempSubBlock = ""
										for whatever in tempSubBlockL:
											tempSubBlock += whatever	
										otherDesg = [(m.group().strip().lower().title()) for m in re.finditer(desgObject2,tempSubBlock)]
										TitlesRegex	= '|'.join(Titles)
										TitlesRegex = r"\b(" + TitlesRegex + r")((?!\S)|((\()|\-|(\/)))"
										desgObject = re.compile(TitlesRegex, re.I|re.M)
										for desg in otherDesg:
											tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
											testList.extend(tempList)
										if(not testList):
											DateList[i-1]["AreaToScanFlag"] = 1
											DateList[i-1]["AreaToScan"] += areaToScan
											DateList.pop(i)	
										else:	
											DateList[i]["AreaToScanFlag"] = 1		
											DateList[i]["AreaToScan"] = areaToScan
						else:
							for (i,date) in enumerate(DateList):
								if(i!=0):
									areaToScan = possibleSubBlock[DateList[i-1]["EndingIndex"]:DateList[i]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
								else:
									areaToScan = possibleSubBlock[:DateList[i]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
								DateList[i]["AreaToScanFlag"] = 1		
								DateList[i]["AreaToScan"] = areaToScan								
						companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
						curr += 1
					else:
						if(curr!=0):
							companySubBlocks[curr-1]["Text"] += possibleSubBlock
							previousDateList = companySubBlocks[curr-1]["DateList"]	
							previousDateListLength = len(previousDateList)
							previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock			
		flg = 0
		currentDateFlag = 0
		for (j,companySubBlock) in enumerate(companySubBlocks):
			companyObj = re.compile(r"\b.*\b",re.I|re.M)
			company = [(m.group()) for m in re.finditer(companyObj,companySubBlock["Company"].strip().lower().title())]
			finalListElem = {"Organization" : company[0]}
			finalListElem["WorkExperience"] = []
			dateList = companySubBlock["DateList"]
			dateListLength = len(dateList)
			totalMonthsOfExperience = 0
			flag = 1
			StIndex = dateList[0]["StartIndex"]
			for (i,dateString) in enumerate(dateList):
				onlyYearFlag = 0
				onlyMonthFlag = 0
				dateObject = re.compile(self.dateRegex, re.I|re.M)
				fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]

				if (not fromToDates):
					dateObject = re.compile(self.dateRegex2, re.I|re.M)
					fromToDates = [(m.group()) for m in re.finditer(dateObject,dateString["Date"])]
					start = 0
					if (not fromToDates):
						dateObject = re.compile(self.dateRegex3, re.I|re.M)
						fromToDates = [(m.group()) for m in re.finditer(dateObject,dateString["Date"])]

						if (not fromToDates):
							dateObject = re.compile(r"\d{2}(\d{2})?", re.I|re.M)
							fromToDates = [(m.group()) for m in re.finditer(dateObject,dateString["Date"])]
							if(not fromToDates):
								dateObject = re.compile(r"\d{1,2}",re.I|re.M)
								fromToDates = [(m.group()) for m in re.finditer(dateObject,dateString["Date"])]

								fromDate = toDate = fromDateMonth = toDateMonth = fromMonthNum = toMonthNum = fromYear = toYear = "unspecified"
								onlyMonthFlag = 1
							else:
								fromDate = fromToDates[0]
								fromYear = fromDate
								fromDateMonth = "unspecified"
								fromMonthNum = "unspecified"
								if(len(fromToDates)==1):
									toDate = datetime.date.today().strftime("%b-%Y").capitalize()
									toDateMonth = toDate[:3]
									toYear = toDate[-4:]
									dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
									toMonthNum = dic.get(toDateMonth, toDate[:2])
								else:
									toYear = fromToDates[1]
									toDate = toYear
									toDateMonth = "unspecified"
									toMonthNum = "unspecified"		
								onlyYearFlag = 1
						
						if(onlyYearFlag==0 and onlyMonthFlag==0):	
							end = -1
							date = fromToDates[0]
							date = date.strip()
							while(date[end].isalpha()):
								end -= 1
							fromDateMonth = date[end+1:]
							fromDateMonth = fromDateMonth[:3].capitalize()
							start = 0
							while(date[start].isdigit()):
								start += 1	
							fromYear = date[:start]
							fromDate = fromDateMonth + "-" + fromYear
							if (len(fromToDates) == 2):
								if (j==0):
									flg = 1
								end = -1
								date = fromToDates[1]
								date = date.strip()
								while(date[end].isalpha()):
									end -= 1
								toDateMonth = date[end+1:]
								toDateMonth = toDateMonth[:3].capitalize()
								start = 0
								while(date[start].isdigit()):
									start += 1	
								toYear = date[:start]
								toDate = toDateMonth + "-" + toYear
							else:
								if(j==0):
									toDate = datetime.date.today().strftime("%b-%Y").capitalize()
									toDateMonth = toDate[:3]
									toYear = toDate[-4:]
								else:
									if(j!=(len(companySubBlocks)-1) or (flg==0)):
										toDate = tempDate
										toDateMonth = toDate[:3]
										dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
										toMonthNum = (dic.get(toDateMonth, toDate[:2]) - 1)
										dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Ma", "4" : "Ap", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}
										toDateMonth = dic2.get(str(toMonthNum), toDateMonth)
										toYear = toDate[-4:]
										toDate = toDateMonth + "-" + toYear
										if(fromYear == toYear):
											test = int(toMonthNum) - int(fromMonthNum)
										else:
											test = ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
										if(test<0):
											toDate = datetime.date.today().strftime("%b-%Y").capitalize()
											toDateMonth = toDate[:3]
											toYear = toDate[-4:]
											dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
											toMonthNum = (dic.get(toDateMonth, toDate[:2]) - 1)
									else:
										toDate = datetime.date.today().strftime("%b-%Y").capitalize()
										toDateMonth = toDate[:3]
										toYear = toDate[-4:]
					else:	
						date = fromToDates[0]
						while(date[start].isalpha()):
							start += 1
						fromDateMonth = date[:start]
						end = -1
						while(date[end].isdigit()):
							end -= 1
						fromYear = date[end+1:]
						if (len(fromYear) == 2):
							if(int(fromYear)<60):
								fromYear = "20" + fromYear
							else:
								fromYear = "19"	+ fromYear
						fromDate = fromDateMonth[:3] + "-" + fromYear
						if (len(fromToDates) == 2):
							if (j==0):
								flg = 1
							start = 0
							date = fromToDates[1]
							while(date[start].isalpha()):
								start += 1
							toDateMonth = date[:start]
							end = -1
							while(date[end].isdigit()):
								end -= 1
							toYear = date[end+1:]	
							if(int(toYear)<60):
								toYear = "20" + toYear
							else:
								toYear = "19" + toYear
							toDate = toDateMonth[:3] + "-" + toYear
						else:
							if(j==0):
								toDate = datetime.date.today().strftime("%b-%Y").capitalize()
								toDateMonth = toDate[:3]
								toYear = toDate[-4:]
							else:
								if(j!=(len(companySubBlocks)-1) or (flg==0)):
									toDate = tempDate
									toDateMonth = toDate[:3]
									dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
									toMonthNum = (dic.get(toDateMonth, toDate[:2]) - 1)
									dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Ma", "4" : "Ap", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}
									toDateMonth = dic2.get(str(toMonthNum), toDateMonth)
									toYear = toDate[-4:]
									toDate = toDateMonth + "-" + toYear
									if(fromYear == toYear):
										test = int(toMonthNum) - int(fromMonthNum)
									else:
										test = ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
									if(test<0):
										toDate = datetime.date.today().strftime("%b-%Y").capitalize()
										toDateMonth = toDate[:3]
										toYear = toDate[-4:]
										dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
										toMonthNum = (dic.get(toDateMonth, toDate[:2]) - 1)
								else:
									toDate = datetime.date.today().strftime("%b-%Y").capitalize()
									toDateMonth = toDate[:3]
									toYear = toDate[-4:]		
				else:
					if (len(fromToDates) == 1):
						fromDate = self.FormatDate(fromToDates[0])
						if(j==0):
							toDate = self.FormatDate("present")
						else:
							if(j!=(len(companySubBlocks)-1) or (flg==0)):
								toDate = self.FormatDate(tempDate)
								toDateMonth = toDate[:3]
								dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
								toMonthNum = (dic.get(toDateMonth, toDate[:2]) - 1)
								dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Ma", "4" : "Ap", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}
								toDateMonth = dic2.get(str(toMonthNum), toDateMonth)
								toYear = toDate[-4:]		
								toDate = toDateMonth + "-" + toYear
								if(fromYear == toYear):
									test = int(toMonthNum) - int(fromMonthNum)
								else:
									test = ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
								if(test<0):
									toDate = datetime.date.today().strftime("%b-%Y").capitalize()
									toDateMonth = toDate[:3]
									toYear = toDate[-4:]
									dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
									toMonthNum = (dic.get(toDateMonth, toDate[:2]) - 1)
							else:
								toDate = datetime.date.today().strftime("%b-%Y").capitalize()
								toDateMonth = toDate[:3]
								toYear = toDate[-4:]	
					else:
						if (j==0):
							flg = 1	
						fromDate = self.FormatDate(fromToDates[0]).strip()
						toDate = self.FormatDate(fromToDates[1]).strip()
						#print (repr(fromDate),repr(toDate))
					fromDateMonth = self.removeSpecialChars(fromDate[:3]).strip()
					toDateMonth = self.removeSpecialChars(toDate[:3]).strip()
					#print (repr(fromDateMonth),repr(toDateMonth))

				if(fromDateMonth.isdigit()):				
					fromMonthNum = int(fromDateMonth)
				if(toDateMonth.isdigit()):
					toMonthNum = int(toDateMonth)
				if(onlyYearFlag==1):
					totalMonthsOfExperience = ((int(toYear) - int(fromYear))*12)
				elif(onlyMonthFlag==1):
					totalMonthsOfExperience = fromToDates[0]	
				else:
					tempDate = fromDate	
					dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
					if(not fromDateMonth.isdigit()):
						fromMonthNum = dic.get(fromDateMonth, fromDate[:2])
					if(not toDateMonth.isdigit()):
						toMonthNum = dic.get(toDateMonth, toDate[:2])
					if(int(str(fromMonthNum)[0])==0 and len(str(fromMonthNum))==2):
						fromMonthNum = fromMonthNum[1]
					dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}	
					if(str(fromMonthNum).isdigit()):
						fromDateMonth = dic2.get(str(fromMonthNum), fromDateMonth)
					if(str(toMonthNum).isdigit()):	
						toDateMonth = dic2.get(str(toMonthNum), toDateMonth)
					fromYear = fromDate[-4:]
					toYear = toDate[-4:]
					if (not str(fromDate).isalpha()):
						fromDate = fromDateMonth + "-" + fromYear
					if (not str(toDate).isalpha()):
						toDate = toDateMonth + "-" + toYear	
					if(fromYear == toYear):
						totalMonthsOfExperience += int(toMonthNum) - int(fromMonthNum)
					else:
						totalMonthsOfExperience += ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
				#print (fromDate,toDate,fromDateMonth,toDateMonth,fromMonthNum,toMonthNum)		
				TitlesRegex	= '|'.join(Titles)
				TitlesRegex = r"( )?( |\,|\"|\-|\-|\:|\.)( )?(" + TitlesRegex + r")( )?( |\"|\,|\-|\-|\:|\.)( )?"
				desgObject = re.compile(TitlesRegex, re.I|re.M)
				testList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,dateString["AreaToScan"])]
				if(dateString["AreaToScanFlag"] == 0):
					DesgList = testList
				else:
					DesgList = []
					bodyDesignationRegex = r"^(?!.*(Reporting to|Backup of|Helping the|Reporting|Submitting|Key Responsibilities as an|Responsible for investigation of|Publishing the errors for|Profitable Champ|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?(and)?\b(" + '|'.join(Titles) + r")((?!\S)|((\()|\-|(\/)))"
					desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
					txt = originalEmpBlock
					wordList = dateString["AreaToScan"].split(' ')
					while '.' in wordList: wordList.remove('.')
					while ';' in wordList: wordList.remove(';')
					while ',' in wordList: wordList.remove(',')
					while ')' in wordList: wordList.remove(')')
					while '(' in wordList: wordList.remove('(')
					while ':' in wordList: wordList.remove(':')
					while '-' in wordList: wordList.remove('-')
					for (index,word) in enumerate(wordList):
						if ('(' in word):
							wordList[index] = wordList[index].replace('(','\(')
						if (')' in word):
							wordList[index] = wordList[index].replace(')','\)')
					wordList = list(filter(None, wordList))
					orgRegex = ""
					if(len(wordList)<40):
						start = int(len(wordList)/2)
						end  = int(len(wordList) - start)
					else:
						start = 20
						end = 20
					count = 0
					while(count<start):
						if(count!=(start-1)):
							orgRegex += (wordList[int(count)] + r"\s*(\)|\.|\,|\&|\;|\-|\:|\(| )*\s*")
						else:
							orgRegex += wordList[int(count)]	 
						count += 1
					orgRegex += r"[\d\D]*"
					count = end
					while(count>0):
						if(count!=1):
							orgRegex += (wordList[int(len(wordList)-count)] + r"\s*(\)|\.|\&|\,|\;|\-|\:|\(| )*\s*")
						else:
							orgRegex += wordList[int(len(wordList)-count)]
						count -= 1	
					findOriginalObj = re.compile(orgRegex, re.I|re.M)
					tempSubBlockL = [(m.group()) for m in re.finditer(orgRegex,txt)]
					tempSubBlock = ""
					for i in tempSubBlockL:
						tempSubBlock += i	
					otherDesg = [(m.group().strip().lower().title()) for m in re.finditer(desgObject2,tempSubBlock)]
					#print (otherDesg)
					TitlesRegex	= '|'.join(Titles)
					TitlesRegex = r"\b(" + TitlesRegex + r")(\.)?((?!\S)|((\()|\-|(\/)))"
					desgObject = re.compile(TitlesRegex, re.I|re.M)
					for desg in otherDesg:
						tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
						DesgList.extend(tempList)
				if (not DesgList):
					txt = companySubBlock["Text"]
					DesgList = [(m.group().strip().title()) for m in re.finditer(desgObject,txt[:StIndex])]
				else:
					flag=1		
				for (i,desg) in enumerate(DesgList):
					start = 0
					while(not desg[start].isalpha()):
						start+=1
					end = -1
					while (not desg[end].isalpha()):
						end-=1
					if(end==-1):
						DesgList[i] = desg[start:]
					else:		
						DesgList[i] = desg[start:(end+1)]
					if('(' in DesgList[i] and ')' not in DesgList[i]):
						DesgList[i] = DesgList[i] + ")"	
				if(flag==1):
					tempList = DesgList
				if(dateListLength<len(DesgList)):
					DesgList = list(set(DesgList))	
				finalListElem["WorkExperience"].append({"FromPeriod":{"Date":fromDate,"Month":fromDateMonth,"MonthNum":fromMonthNum,"Year":fromYear},"ToPeriod":{"Date":toDate,"Month":toDateMonth,"MonthNum":toMonthNum,"Year":toYear},"totalMonthsOfExperience":totalMonthsOfExperience,"DesignationList":DesgList})	
			finalList.append(finalListElem)
		someList = []	
		for listElem in finalList:
			workExpList = listElem["WorkExperience"]
			outputList = [x for x in workExpList if x["DesignationList"]]
			listElem["WorkExperience"] = outputList
			outputList = sorted(outputList, key=lambda k: k['DesignationList'][0])
			new_list = []
			usedDesgList = []
			for (i,outputListElem) in enumerate(outputList):
				if outputListElem['DesignationList'][0] not in usedDesgList:
					usedDesgList.append(outputListElem['DesignationList'][0]) 
					new_list.append(outputListElem)
			outputList = new_list
			listElem["WorkExperience"] = outputList
		return (finalList)

	# def AllParsersCall(self):
	# 	ParsedDetails = {}
	# 	ParsedDetails["Education"] = []
	# 	try:
	# 		ParsedDetails["Experience"] = self.returnListforCSV(self.designationTenureParser())
	# 	except (KeyboardInterrupt, SystemExit):
	# 		ParsedDetails["Experience"]  = ["TestSeparately"]
	# 		pass			
	# 	except:
	# 		ParsedDetails["Experience"]  = ["Header/Company/Designation Master incomplete"]
	# 		pass
	# 	ParsedDetails["Skills"] = []
	# 	return ParsedDetails

def main():	
	input = open("input.txt","r")
	input = input.read()
	#print (repr(input))
	#input = 'Mansi Grover\n\n6/69 Old Rajinder Nagar\n\nNew Delhi, 110060,\n\nIndia.\n\nMobile No.: 9999597391 (Delhi)\n\nEmail: grover.mansi24@gmail.com\n\n\n\n\n\nOBJECTIVE\n\nTo achieve excellence in my career and make innovative contribution towards\n\nthe growth and development of the organization. I would like to shoulder increased\n\nresponsibilities and move on the high echelons of the firm.\n\n\t\t\n\nACADEMIC QUALIFICATIONS\n\nCOURSE\n\nUNIVERSITY/ BOARD\n\nINSTITUTE/ SCHOOL \n\nAGGREGATE MARKS\n\nYEAR OF PASSING\n\nMBA   (FINANCE AND MARKETING)\n\nG.G.S.I.P UNIVERSITY\n\nDELHI INSTITUTE OF ADVANCED STUDIES\n\n60.87%\n\n2014\n\nB.COM (P)\n\nDELHI UNIVERSITY\n\nSCHOOL OF OPEN LEARNING\n\n50.15%\n\n2011\n\nSENIOR SECONDARY EDUCATION\n\nC.B.S.E BOARD\n\nSALWAN PUBLIC SCHOOL\n\n77.40%\n\n2007\n\nHIGHER SECONDARY EDUCATION\n\nC.B.S.E. BOARD\n\nSALWAN PUBLIC SCHOOL\n\n73.80%\n\n2005\n\n\n\nWORK EXPERIENCE\n\nCOMPANY                        : INFO EDGE INDIA LTD (NAUKRIGULF.COM DIVISION)\n\nDESIGNATION                 : Sr. Sales Executive \n\nSERVICE TENURE           : March 2014 Till Present.\n\n\n\n\n\n\n\n\n\nJOB RESPONSIBILITIES: \n\nB2B Process - Responsible for selling corporate accounts to the various prospective clients in Middle   east/South East Asia markets.\n\nCreating database of clients through enhanced outbound calls and maintaining the database of the leads generated and make regular follow ups with them.\n\nDo extensive search on the net (Job-Sites / Google).\n\nTarget based business development from generating and contacting leads in the HR Department in the Gulf market, to making prospects clients, generating revenue and after Sales Service(s).\n\nUnderstanding the recruitment needs of companies/ organizations/ consultants, briefing them about the services available on Naukri.com/NaukriGulf.com and proposing suitable hiring solutions.\n\nMaintaining relationship with the existing clients and satisfying them with the services\n\nDeveloping new streams for revenue growth and maintaining relationship with customer to achieve repeat / referral business.\n\nResponsible for acquiring business and achieving sales targets.\n\n\n\n\n\n\n\nINTERNSHIP DETAILS \n\nCompleted Summer Internship Training with EVN GLOBAL SOLUTIONS PRIVATE LIMITED from 14th JUNE 2013 till 16TH AUGUST 2013 and had prepared a project report on \xe2\x80\x9cEffectiveness of recruitment and selection process in context of Accenture\xe2\x80\x9d\n\n\n\n\n\n\n\nOTHER ACHIEVEMENTS\n\nHad anchored events in ANUGOONJ (Annual fest conducted by G.G.S.I.P University) held at Delhi Institute of Advanced Studies in 2013.\n\nParticipated in the creative team of Ecstasy (Annual fest) held at Delhi Institute of Advanced Studies 2013.\n\n\n\n\n\n\n\nCOMPUTER PROFICIENCY\n\n\n\nProficient in various Microsoft technologies like MS-Word, MS-Excel, MS    PowerPoint.\n\nProficient in various accountancy packages like tally ERP.\n\n\n\n\n\nSKILLS\n\n  \n\nGood presence of mind\n\nGood presentation skills\n\nGood communication skills both verbal and written\n\n\n\nHOBBIES\n\n\n\nReading novels\n\nLearning by interacting\n\n\n\nPERSONAL PROFILE\n\n\t\n\n\tDate of Birth\t\t\t\t:\t24th October 1989\n\n\tFather\xe2\x80\x99s Name\t\t\t\t:\tMr. Pradeep Grover\n\n\tNationality\t\t\t\t:\tIndian\n\n\tMarital Status\t\t\t\t:\tSingle\n\n\tLanguages Known\t\t\t:\tEnglish, Hindi \n\n\tCurrent Address\t\t\t:\t6/69 Old Rajinder Nagar New Delhi.'
	obj = GenericResumeParser(repr(input))
	workExperienceList = obj.designationTenureParser()
	print (workExperienceList)
main()
