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
		self.ResumeText = str(re.sub(r'\\x\w{1,2}',' ',restext))
		resumeTxt = ""
		for word in self.ResumeText:
			if(ord(word)<194):
				resumeTxt += word
		self.ResumeText = resumeTxt
		#print (resumeTxt)
		self.DurationRegex = r"[\s\\r\\t\\n]*.*?(Duration|Since|From|Working For|Workingfrom)?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{1,4})\s*(\-{1,3}|/|\s|to|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?\s*((\s|\\n|\-{1,3}|\.|,|’|'|‘|/|\d{1,2}|\d{1,4})*.*\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)*\b(\s|\\n|\-{1,3}|\.|,|’|'|‘|)*\d{1,4}|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?"		
		self.dateStringRegex = r"(\,)?(\()?( |\(|\)|\,|\.|\:|\-|\:\-|\-\:|\;|\&|^)((((Since|From|Working from)?( )?(((((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)(\.|\b)( )?(\d{1,2}(th|rd|st|nd)?( )?( |\/|\\|\.|\-|\–|\,)?( )?)?)|((\d{1,2}(rd|st|nd|th)?( )?( |\/|\\|\.|\-|\–)( )?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b))( )?( |\-{1,3}|\–{1,3}|\.|,|’|'|‘)+( )?\d{2}(\d{2})?(\'|\’)?( )?)|((\d{1,2}(rd|st|nd|th)?( )?( |\/|\\|\.|\-)( )?)?\d{1,2}( )?(\/|\\|\-|\–)( )?\d{2}(\d{2})?)|((\d{2}(\d{2})?)( )?(\/|\\|\-|\–| )( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?)))(( )?(\-{1,3}|\/| |\–{1,3}|to|till|to till)*( )?((((((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)(\.|\b)( )?(\d{1,2}(th|rd|st|nd)?( )?( |\/|\\|\.|\-|\–)?( )?)?)|((\d{1,2}(rd|st|th|nd)?( )?( |\/|\\|\.|\-|\–)( )?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)))( )?( |\-{1,3}|\–{1,3}|\.|,|’|'|‘|\/|\\)+( )?\d{2}(\d{2})?(\'|\’)?( )?))|(date|now|the date|present|present date|the present date|to till date|till date|today|current)|((\d{1,2}(rs|st|nd)?( )?( |\/|\\|\.|\-|\–)( )?)?\d{1,2}( )?( |\/|\\|\.|\-|\–| )( )?\d{2}(\d{2})?)|((\d{2}(\d{2})?)( )?(\/|\\|\.|\-|\–| )( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?)))?)|((\d{2}(\d{2})?( )?(\-{1,3}|\/| |\–{1,3}|to|till|to till)+( )?((date|now|the date|present|present date|the present date|to till date|till date|t til date|today|current)|(\d{2}(\d{2})?))))|((Since|From|Working from|Currently working)(\d{2}(\d{2})?))|((for|from|for a duration of|since|till|to till)\d{1,2}( )(months))|(\d{1,2}( )(months|month|year|years)( )(work|as)))(\))?( |\(|\)|\,|\.|\:|\-|\:\-|\-\:|\;|$)"
		self.dateRegex = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\–{1,3}|\.|,|’|'|‘)*(\d{1,2}(th|rd|st|nd)?( )?( |\/|\\|\.|\-|\–|\,)( )?)?\d{2}(\d{2})?)|\b(\d{1,2}(\s|\/|\\|\.|\-|\–)\d{2}(\d{2})?)( |\)|\.)"
		self.dateRegex2 = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)( )\b\d{1,2}( )?(\s|\-{1,3}|\–{1,3}|\.|\,|’|'|‘)*( )?\d{2}(\d{2})?)\b"
		self.dateRegex3 = r"\b(\d{2}(\d{2})?)( )?(\/|\\|\.|\-|\–)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b"
		self.designationRegex = r"(Job Title|Designation|Position|Role|Working\s*as\s*a|Working\s*as\s*an|Worked\s*as\s*an|Worked\s*as\s*a|Promoted\s*to\s*a|Promoted\s*to\s*an|Promoted\s*to|Worked\s*as|Working\s*as|Work\s*as|Work\s*as\s*a|Work\s*as\s*an)\s*\d{0,2}\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.designationRegex2 =r"\s*(as|as\s*a|as\s*an|Profile|Profile\s*\&\s*Product)\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.bodyDesignationRegex = r"^(?!.*(Reporting to|Reporting|Submitting|Publishing the errors for|Profitable Champ|Key Responsibilities as an|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|Leading a team of|Meeting with|Engage in managing the wealth portfolio|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?(and)?\b"	
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
	
	def TitleCleaner(self, title):
		title = str(re.sub(r"(\\n|\\r|\\t)", '', title))
		return title	

	def FormatDate(self,date):
		if(date!="None" or date!="" ):
			if(date.lower() in ['onwards','till date','till now','till the date','till present','present','till today','till','date','continue']):
				date = datetime.date.today().strftime("%b-%Y")
				return date.capitalize()
			date = re.sub(r"(\s|\-{1,3}|\–{1,3}|\.|,|’|'|‘)", '$', date)
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

	def isGenuine(self, originalEmpBlock, areaToScan, specificRegex):
		testList = []
		bodyDesignationRegex = r"^(?!.*(Reporting to|Backup of|Qualified for|for achieving|for the Month of|Helping the|Rated|Leading a team of|Meeting with|Engage in managing the wealth portfolio|Reporting|Submitting|Key Responsibilities as an|Responsible for investigation of|Publishing the errors for|Profitable Champ|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from the|renowned|best|team of)).*(Promoted as )?(and)?\b" + specificRegex + r"((?!\S)|((\()|(\/)|\,|\}|\{))" 
		desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
		txt = originalEmpBlock
		wordList = areaToScan.split(' ') 
		while '.' in wordList: wordList.remove('.') 
		while ';' in wordList: wordList.remove(';')
		while ')' in wordList: wordList.remove(')')
		while '(' in wordList: wordList.remove('(')
		while ':' in wordList: wordList.remove(':')
		while '-' in wordList: wordList.remove('-')
		while '*' in wordList: wordList.remove('*')  
		wordList = list(filter(None, wordList))
		for (index,word) in enumerate(wordList):
			if ('(' in word):
				wordList[index] = wordList[index].replace('(','\(')
			if (')' in word):
				wordList[index] = wordList[index].replace(')','\)')
			if ('.' in word):
				wordList[index] = wordList[index].replace('.','\.')
		orgRegex = ""
		# print (wordList)
		if(len(wordList)<40):
			start = int(len(wordList)/2)
			end  = int(len(wordList) - start)		
		else:
			start = 20
			end = 20
		count = 0	
		while(count<start):
			if(count!=(start-1)):
				orgRegex += (wordList[int(count)] + r"\s*?(\)|\.|\,|\-|\&|\:|\;| |\(|\*?)*?\s*?")
			else:
				orgRegex += wordList[int(count)]	 
			count += 1
		# print (orgRegex,start,end)	
		orgRegex += r"[\d\D]*?"
		count = end
		while(count>0):
			if(count!=1):
				orgRegex += (wordList[int(len(wordList)-count)] + r"\s*?(\)|\.|\,|\-|\&|\:|\;| |\(|\*?)*?\s*?")
			else:
				orgRegex += wordList[int(len(wordList)-count)]
			count -= 1
		orgRegex = orgRegex.strip()
		findOriginalObj = re.compile(orgRegex, re.I|re.M)
		tempSubBlockL = [(m.group()) for m in re.finditer(findOriginalObj,txt)]
		tempSubBlock = ""
		for whatever in tempSubBlockL:
			tempSubBlock += whatever	
		#print (tempSubBlock)
		otherDesg = [(m.group().strip().lower().title()) for m in re.finditer(desgObject2,tempSubBlock)]
		return otherDesg

	def CompanyBaseSections(self,headRegex,isFoundFlag):
		testDocument = self.ResumeText
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
		#print (testDocument)
		if(len(dmatch)>0):
			position = [(m.start(0), m.end(0), self.TitleCleaner(m.group())) for m in re.finditer(regex, testDocument)]
			position = sorted(position, key=lambda x: x[0])
			if(isFoundFlag==1):
				ans = position[0][0]
				ansTitle = position[0][2]
			else:
				try:
					ans = position[1][0]	
					ansTitle = position[1][2]
				except:
					return None	
			listCount = 0	
			for tupleelem in position:
				restext = self.ResumeText[tupleelem[0]:(tupleelem[1]+1)]
				upperRestext = restext.upper()
				if (restext == upperRestext):
					listCount+=1
					if (isFoundFlag==1):
						ans = tupleelem[0]
						ansTitle = tupleelem[2]
						break
					else:
						if(listCount>1):
							ans = tupleelem[0]
							ansTitle = tupleelem[2]
							break									
			return (ans,3,ansTitle)
		else:
			position = [(m.start(0), m.end(0), self.TitleCleaner(m.group())) for m in re.finditer(regex2, testDocument)]
			position = sorted(position, key=lambda x: x[0])
			if(position):
				if(isFoundFlag==1):
					#print (position[0][0],2,position[0][2])
					return (position[0][0],2,position[0][2])
				else:
					try:
						return (position[1][0],2,position[1][2])
					except:
						return None	
			else:
				position = [(m.start(0), m.end(0), self.TitleCleaner(m.group())) for m in re.finditer(regex3, testDocument)]
				position = sorted(position, key=lambda x: x[0])
				if(position):
					if(isFoundFlag==1):
						return (position[0][0],1,position[0][2])
					else:
						try:
							return (position[1][0],1,position[1][2])
						except:
							return None	
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
		#print (type(self.ResumeText))
		allBlocksList = []
		result = self.CompanyBaseSections(self.getHeader('educationHeader'),1)
		allBlocksList.append({'BlockName':"Education",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('accomplishmentsHeader'),1)
		allBlocksList.append({'BlockName':"Accomplishments",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('awardsHeader'),1)
		allBlocksList.append({'BlockName':"Awards",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('extracurricularHeader'),1)
		allBlocksList.append({'BlockName':"ExtraCurricular Activities",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('miscHeader'),1)
		allBlocksList.append({'BlockName':"Miscellaneous",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('summaryHeader'),1)
		allBlocksList.append({'BlockName':"Summary",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('skillsHeader'),1)
		allBlocksList.append({'BlockName':"Skills",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('employmentHeader'),1)
		#print (result)
		allBlocksList.append({'BlockName':"Employment",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('credibilityHeader'),1)
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
		#self.writeToDesignationMaster(['Associate Director','Sr\. Manager','TRAINEE','INTERN'])
		with open('companyMaster.txt') as file:
			for line in file: 
				line = line.strip()
				Companies.append(line)
		#print (Companies)		
		justTrying = re.sub(r'\\x\w{1,2}',' ',employmentBlock)
		justTrying = justTrying.replace('\\n','\n').replace('\\t','\t').replace('\\r','\r')
		originalEmpBlock = justTrying
		# print ("####",originalEmpBlock,"#####")
		employmentBlock = re.split(r'\\n|\\r|\\t|\s|\\x\w{1,2}',employmentBlock)
		employmentBlock = list(filter(None, employmentBlock))
		tempEmpBlock = ' '.join(employmentBlock)
		#print (tempEmpBlock)
		NERCompanyList = OrgNER(tempEmpBlock)
		#print (NERCompanyList)	
		Companies = sorted(list(set(Companies)), key=len, reverse=True)	
		#print (Companies)
		CompanyRegex = r"(\,|M\/S)?( |\-|\.|\–|\(|\\t|\\n|\\r)(" + '|'.join(Companies) + r")( |\-|\.|\,|\;|\(|\)|\.\:|\\t|\\n|\\r)"
		TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
		TitlesRegex = r"( )?( |\,|\;|\-|\"|^|\{|\-|\:|\.|\(|\\n|\\t|\\r)( )?(" + TitlesRegex + r")(\,|\/|\;|\}|\-| |\\n|\\r|\\t)?\b"
		compRegexObj = re.compile(CompanyRegex, re.I|re.M)
		companyList = [{"Company": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(compRegexObj, tempEmpBlock)]
		companyList.sort(key=lambda x: x["StartIndex"])
		if (not NERCompanyList and not companyList):
			result = self.CompanyBaseSections(self.getHeader('employmentHeader'),0)
			if (not result):
				return None
			startingIndex = result[0]
			for (i,Block) in enumerate(allBlocksList):
				if(Block['StartingIndex']!=0):
					if(Block['BlockName']=='Employment'):
						Block['StartingIndex'] = startingIndex
						Block['BlockText'] = ""
			#print (allBlocksList)
			allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
			#print (allBlocksList)
			for (i,Block) in enumerate(allBlocksList):
				if(Block['StartingIndex']!=0 and Block['BlockName']=='Employment'):
					if(i!=(len(allBlocksList)-1)):
						Block['EndingIndex'] = allBlocksList[i+1]['StartingIndex']
						Block['BlockText'] = self.ResumeText[Block['StartingIndex']:Block['EndingIndex']]
					else:
						Block['EndingIndex'] = len(self.ResumeText) - 1
						Block['BlockText'] = self.ResumeText[Block['StartingIndex']:]
					employmentBloc = Block
					employmentBlock = Block['BlockText']
					employmentBlockIndex = i
					justTrying = re.sub(r'\\x\w{1,2}',' ',employmentBlock)
					justTrying = justTrying.replace('\\n','\n').replace('\\t','\t').replace('\\r','\r')
					originalEmpBlock = justTrying
					employmentBlock = re.split(r'\\n|\\r|\\t|\s|\\x\w{1,2}',employmentBlock)
					employmentBlock = list(filter(None, employmentBlock))
					tempEmpBlock = ' '.join(employmentBlock)
					NERCompanyList = OrgNER(tempEmpBlock)
					#print (employmentBlock)
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
		#print (companyStEndTuple)
		nerCompany = []
		for nerComp in NERCompanyList:
			start = 0
			nerCompName = nerComp[1]
			nerCompStart = int(nerComp[2]) #381
			nerCompEnd = nerCompStart + int(nerComp[3]) - 1 #415
			CompMasterList = [item for item in companyStEndTuple if item[0] == nerCompStart]
			#print (nerCompName)
			if(CompMasterList):
				compTuple = CompMasterList[0]
				compTupleIndex = companyStEndTuple.index(compTuple)
				compTupleEndingIndex = compTuple[1]
				if(compTupleEndingIndex<nerCompEnd):
					companyList[compTupleIndex] = {"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd}
					companyStEndTuple[compTupleIndex] = (nerCompStart,nerCompEnd)
					nerCompany.append(nerCompName)
			else:
				flag=0
				for (i,stEndTuple) in enumerate(companyStEndTuple):
					if(i!=(len(companyStEndTuple)-1)):
						if(i!=0):
							if nerCompStart>companyStEndTuple[i][1] and nerCompEnd<companyStEndTuple[i+1][0]:								
								flag=1
								companyList.insert((i+1),{"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd})
								companyStEndTuple.insert((i+1),(nerCompStart,nerCompEnd))
								nerCompany.append(nerCompName)
								break
						else:
							if (nerCompEnd<companyStEndTuple[i][0]):
								flag=1
								companyList.insert(0,{"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd})
								companyStEndTuple.insert(0, (nerCompStart,nerCompEnd))
								nerCompany.append(nerCompName)
								break			
					else:
						if (nerCompStart>companyStEndTuple[i][1]):
							flag=1
							companyList.append({"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd})
							companyStEndTuple.append((nerCompStart,nerCompEnd))
							nerCompany.append(nerCompName)
							break		
				if(flag==0):
					for (i,stEndTuple) in enumerate(companyStEndTuple):
						if nerCompStart>=companyStEndTuple[i][0] and nerCompStart<companyStEndTuple[i][1] and nerCompEnd>companyStEndTuple[i][1]:								
							flag=1
							companyList[i] = {"Company":tempEmpBlock[companyStEndTuple[i][0]:(nerCompEnd+1)],"StartIndex":companyStEndTuple[i][0],"EndingIndex":nerCompEnd}
							companyStEndTuple[i] = (companyStEndTuple[i][0],nerCompEnd)
							nerCompany.append(tempEmpBlock[companyStEndTuple[i][0]:(nerCompEnd+1)])
							break
		if(not companyList):
			for nerComp in NERCompanyList:
				nerCompName = nerComp[1]
				nerCompStart = int(nerComp[2]) #110
				nerCompEnd = nerCompStart + int(nerComp[3]) - 1
				nerCompany.append(nerCompName)
				companyList.append({"Company":nerCompName,"StartIndex":nerCompStart,"EndingIndex":nerCompEnd})					
		#print (companyList,"\n\n\n",nerCompany,"\n\n\n\n")
		Companies.extend(nerCompany)
		#self.writeToCompanyMaster(nerCompany)
		Companies = sorted(list(set(Companies)), key=len, reverse=True)	
		companyList.sort(key=lambda x: x["StartIndex"])
		# print (companyList)					
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
			#print (textBeforeCompany)	
			DateList = [{"Date": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, textBeforeCompany)]
			DesgList = [{"Designation": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textBeforeCompany)]
			# print (DateList,DesgList)
			if (DateList or DesgList):
				if(DateList and DesgList):
					isRubbish = -1
					#print (DateList,DesgList)
				elif(DateList):
					isRubbish = 0
				else:
					isRubbish = 2		
			else:
				isRubbish = 1
		print (isRubbish)						
		if ((not textBeforeCompany) or (isRubbish==1)):
			curr = 0
			for (i,company) in enumerate(companyList):
				someflg = 0
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
				TitlesRegex = r"( )?( |\,|\"|\-|\-|\:|\.|^|\{|\(|\))( )?(" + TitlesRegex + r")\s*( )?( |\"|\”|\,|\-|\-|\:|\.|\)|\-|\(|\}|\(|\))( )?"
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
					if(DateList and DesgList):
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
										if(lastDateFlag not in locals()):
											lastDateFlag = 0
											DateList[j]["AreaToScan"] = areaToScan	
										else:
											if(not lastDateFlag):	
												DateList[j]["AreaToScan"] = areaToScan	
											else:
												DateList[j]["AreaToScan"] += areaToScan
												lastDateFlag = 0
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
											if(lastDateFlag not in locals()):
												lastDateFlag = 0
												DateList[j]["AreaToScan"] = areaToScan	
											else:
												if(not lastDateFlag):	
													DateList[j]["AreaToScan"] = areaToScan	
												else:
													DateList[j]["AreaToScan"] += areaToScan
													lastDateFlag = 0
											DateList[j]["AreaToScanFlag"] = 1		
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
									if(lastDateFlag not in locals()):
										lastDateFlag = 0
										DateList[j]["AreaToScan"] = areaToScan	
									else:
										if(not lastDateFlag):	
											DateList[j]["AreaToScan"] = areaToScan	
										else:
											DateList[j]["AreaToScan"] += areaToScan
											lastDateFlag = 0
							companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
							curr += 1
						else:
							if(curr!=0):
								companySubBlocks[curr-1]["Text"] += possibleSubBlock
								previousDateList = companySubBlocks[curr-1]["DateList"]	
								previousDateListLength = len(previousDateList)
								previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
					elif(not DateList and not DesgList):
						if(curr!=0):
							companySubBlocks[curr-1]["Text"] += possibleSubBlock
							previousDateList = companySubBlocks[curr-1]["DateList"]	
							previousDateListLength = len(previousDateList)
							previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
					elif(not DateList):
						if(curr!=0):
							companySubBlocks[curr-1]["Text"] += possibleSubBlock
							previousDateList = companySubBlocks[curr-1]["DateList"]	
							previousDateListLength = len(previousDateList)
							previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
							companySubBlocks[curr-1]["DesignationList"].extend(DesgList)
					else:
						#only DateList
						textBeforeFirstDate = possibleSubBlock[:DateList[0]["StartIndex"]]
						previousDateList = companySubBlocks[curr-1]["DateList"]	
						previousDateListLength = len(previousDateList)
						previousDateList[previousDateListLength-1]["AreaToScan"] += textBeforeFirstDate
						for (dateIndex,date) in enumerate(DateList):
							if(i!=len(DateList)-1):
								previousDateList.append({"Date":date["Date"],"StartIndex":date["StartIndex"],"EndingIndex":date["EndingIndex"],"AreaToScanFlag":1,"AreaToScan":possibleSubBlock[DateList[i]["StartIndex"]:DateList[i+1]["StartIndex"]]})				
							else:
								lastDateFlag = 1
								previousDateList.append({"Date":date["Date"],"StartIndex":date["StartIndex"],"EndingIndex":date["EndingIndex"],"AreaToScanFlag":1,"AreaToScan":possibleSubBlock[DateList[i]["StartIndex"]:]})				

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
					#print (possibleSubBlock)
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					if(not DateList and j!=0):
						companySubBlocks[curr-1]["Text"] += possibleSubBlock
						textBeforeCompany = ''
						TitlesRegex	= '|'.join(Titles)
						otherDesg = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
						TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|((\()|\-|(\/)))"
						desgObject = re.compile(TitlesRegex, re.I|re.M)	
						for desg in otherDesg:
							tempList = [{"Designation": self.removeSpecialChars(m.group().strip().lower().title()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(desgObject,desg)]
							testList.extend(tempList)
						companySubBlocks[curr-1]["DesignationList"].extend(testList)
						companySubBlocks[curr-1]["DateList"][len(DateList)-1]["AreaToScan"] += possibleSubBlock
					else:	 
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
						#print (possibleSubBlock)		
						DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
						DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
						#print (DateList,DesgList,company["Company"])
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
											TitlesRegex	= '|'.join(Titles)
											otherDesg = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
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
										if(i==(len(DateList)-1)):
											areaToScan = areaToScan + possibleSubBlock[DateList[i]["StartIndex"]:]
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
									print (areaToScan)
								print (DateList)									
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
					rubbishCompanyFlag = 0
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
						if(not DateList):
							DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
							DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
							if (not DesgList):
								companySubBlocks[curr-1]["Text"] += possibleSubBlock
								textBeforeCompany = ''
							else:
								textToReplace = possibleSubBlock[DesgList[0]["StartIndex"]:]
								possibleSubBlock = possibleSubBlock.replace(textToReplace,"")
								textBeforeCompany = textToReplace
							companySubBlocks[curr-1]["Text"] += possibleSubBlock		
							previousDateList = companySubBlocks[curr-1]["DateList"]	
							previousDateListLength = len(previousDateList)
							previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
							companySubBlocks[curr-1]["DesignationList"].extend(DesgList)
							rubbishCompanyFlag = 1
						else:	
							textAfterLastDate = possibleSubBlock[(DateList[len(DateList)-1]["EndingIndex"]):]
							DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
							DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textAfterLastDate)]
							if(not DesgList):
								textBeforeCompany = ''
							else:
								textToReplace = textAfterLastDate[(DesgList[len(DesgList)-1]["StartIndex"]):]
								possibleSubBlock = self.rreplace(possibleSubBlock, textToReplace, '', 1)
								textBeforeCompany = textToReplace
					#print ("*********\n\n\n\n\n\n\n\n\n",possibleSubBlock,"\n\n\n\n\n\n\n\n\n\n\n*********")
					if(rubbishCompanyFlag==0):								
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
											TitlesRegex	= '|'.join(Titles)
											otherDesg = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
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
		flg = 0
		currentDateFlag = 0
		#print (companySubBlocks)
		for (j,companySubBlock) in enumerate(companySubBlocks):
			firstDateRubbish = 0
			newDateList = []
			dateList = companySubBlock["DateList"]	
			dateListLength = len(dateList)
			counter = 0
			alreadyAppended = 0
			for (i,dateString) in enumerate(dateList):
				#print (dateString["Date"])
				if not (self.isGenuine(originalEmpBlock, dateString["Date"], "(" +self.dateRegex + ")")):
					if(counter!=0):
						newDateList[counter-1]["AreaToScan"] = newDateList[counter-1]["AreaToScan"] + dateString["AreaToScan"]
					else:
						if(alreadyAppended==0):
							newDateList.append({"Date": '', "StartIndex": '', "EndingIndex": '', "AreaToScan": dateString["AreaToScan"], "AreaToScanFlag":1})
						else:
							newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]	
						alreadyAppended = 1
						firstDateRubbish = 1
					continue	
				else:
					if(firstDateRubbish==0):
						newDateList.append(dateString)
					else:
						newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]
						newDateList[counter]["StartIndex"] = int(dateString["StartIndex"])
						newDateList[counter]["EndingIndex"] = int(dateString["EndingIndex"])
						newDateList[counter]["Date"] = dateString["Date"]
						firstDateRubbish = 0	
					counter += 1
				dateObject = re.compile(self.dateRegex, re.I|re.M)
				fromToDates = [(self.removeSpecialChars(m.group().strip()),m.group(4)) for m in re.finditer(dateObject,dateString["Date"])]
				#print (fromToDates)
				if (not fromToDates):
					if not (self.isGenuine(originalEmpBlock, dateString["Date"], "(" +self.dateRegex2 + ")")):
						if(counter!=0):
							newDateList[counter-1]["AreaToScan"] = newDateList[counter-1]["AreaToScan"] + dateString["AreaToScan"]
						else:
							if(alreadyAppended==0):
								newDateList.append({"Date": '', "StartIndex": '', "EndingIndex": '', "AreaToScan": dateString["AreaToScan"], "AreaToScanFlag":1})
							else:
								newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]	
							alreadyAppended = 1
							firstDateRubbish = 1
						continue	
					else:
						if(firstDateRubbish==0):
							newDateList.append(dateString)
						else:
							newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]
							newDateList[counter]["StartIndex"] = int(dateString["StartIndex"])
							newDateList[counter]["EndingIndex"] = int(dateString["EndingIndex"])
							newDateList[counter]["Date"] = dateString["Date"]
							firstDateRubbish = 0	
						counter += 1
					dateObject = re.compile(self.dateRegex2, re.I|re.M)
					fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
					start = 0
					if (not fromToDates):
						if not (self.isGenuine(originalEmpBlock, dateString["Date"], "(" +self.dateRegex3 + ")")):
							if(counter!=0):
								newDateList[counter-1]["AreaToScan"] = newDateList[counter-1]["AreaToScan"] + dateString["AreaToScan"]
							else:
								if(alreadyAppended==0):
									newDateList.append({"Date": '', "StartIndex": '', "EndingIndex": '', "AreaToScan": dateString["AreaToScan"], "AreaToScanFlag":1})
								else:
									newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]	
								alreadyAppended = 1
								firstDateRubbish = 1
							continue	
						else:
							if(firstDateRubbish==0):
								newDateList.append(dateString)
							else:
								newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]
								newDateList[counter]["StartIndex"] = int(dateString["StartIndex"])
								newDateList[counter]["EndingIndex"] = int(dateString["EndingIndex"])
								newDateList[counter]["Date"] = dateString["Date"]
								firstDateRubbish = 0	
							counter += 1
						dateObject = re.compile(self.dateRegex3, re.I|re.M)
						fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
						if (not fromToDates):
							if not (self.isGenuine(originalEmpBlock, dateString["Date"], r"(\d{2}(\d{2})?)")):
								if(counter!=0):
									newDateList[counter-1]["AreaToScan"] = newDateList[counter-1]["AreaToScan"] + dateString["AreaToScan"]
								else:
									if(alreadyAppended==0):
										newDateList.append({"Date": '', "StartIndex": '', "EndingIndex": '', "AreaToScan": dateString["AreaToScan"], "AreaToScanFlag":1})
									else:
										newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]	
									alreadyAppended = 1
									firstDateRubbish = 1
								continue	
							else:
								if(firstDateRubbish==0):
									newDateList.append(dateString)
								else:
									newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]
									newDateList[counter]["StartIndex"] = int(dateString["StartIndex"])
									newDateList[counter]["EndingIndex"] = int(dateString["EndingIndex"])
									newDateList[counter]["Date"] = dateString["Date"]
									firstDateRubbish = 0	
								counter += 1
							dateObject = re.compile(r"\d{2}(\d{2})?", re.I|re.M)
							fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
							if(not fromToDates):
								if not (self.isGenuine(originalEmpBlock, dateString["Date"], r"(\d{1,2}( |\-)(month|year|week|day)(s)?( |\b))")):
									if(counter!=0):
										newDateList[counter-1]["AreaToScan"] = newDateList[counter-1]["AreaToScan"] + dateString["AreaToScan"]
									else:
										if(alreadyAppended==0):
											newDateList.append({"Date": '', "StartIndex": '', "EndingIndex": '', "AreaToScan": dateString["AreaToScan"], "AreaToScanFlag":1})
										else:
											newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]	
										alreadyAppended = 1
										firstDateRubbish = 1
									continue	
								else:
									if(firstDateRubbish==0):
										newDateList.append(dateString)
									else:
										newDateList[counter]["AreaToScan"] += dateString["AreaToScan"]
										newDateList[counter]["StartIndex"] = int(dateString["StartIndex"])
										newDateList[counter]["EndingIndex"] = int(dateString["EndingIndex"])
										newDateList[counter]["Date"] = dateString["Date"]
										firstDateRubbish = 0	
									counter += 1
			companySubBlock["DateList"] = newDateList						
			#print ("*****\n\n\n",newDateList,"\n\n******")
									
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
				fromToDates = [(self.removeSpecialChars(m.group().strip()),m.group(4)) for m in re.finditer(dateObject,dateString["Date"])]
				#print (fromToDates)
				if (not fromToDates):
					dateObject = re.compile(self.dateRegex2, re.I|re.M)
					fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
					start = 0
					if (not fromToDates):
						dateObject = re.compile(self.dateRegex3, re.I|re.M)
						fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
						if (not fromToDates):
							dateObject = re.compile(r"\d{2}(\d{2})?", re.I|re.M)
							fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
							if(not fromToDates):
								dateObject = re.compile(r"\d{1,2}( |\-)(month|year|week|day)(s)?( |\b)",re.I|re.M)
								fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
								fromDate = toDate = fromDateMonth = toDateMonth = fromMonthNum = toMonthNum = fromYear = toYear = "unspecified"
								onlyMonthFlag = 1
								for (ftdindex,b) in enumerate(fromToDates):
									value = int(re.match(r"\d{1,2}",b,re.I|re.M).group())
									if('year' in b):
										fromToDates[0] = value*12
									elif('month' in b):
										fromToDates[0] = value
									elif('week' in b):
										fromToDates[0] = (value/4)
									elif('day' in b):
										fromToDates[0] = (value/30)			
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
									toMonthNum = dic.get(toDateMonth)
								else:
									toYear = fromToDates[1]
									toDate = toYear
									toDateMonth = "unspecified"
									toMonthNum = "unspecified"		
								onlyYearFlag = 1
						
						if(onlyYearFlag==0 and onlyMonthFlag==0):	
							end = -1
							date = fromToDates[0].strip()
							while(date[end].isalpha()):
								end -= 1	
							fromDateMonth = date[end+1:]
							fromDateMonth = fromDateMonth[:3].capitalize()
							start = 0
							while(date[start].isdigit()):
								start += 1		
							fromYear = date[:start]
							if(len(fromYear)==2):
								if(int(fromYear)<60):
									fromYear = "20" + fromYear	
								else:	
									fromYear = "19" + fromYear
							fromDate = fromDateMonth + "-" + fromYear
							if (len(fromToDates) == 2):
								if (j==0):
									flg = 1
								end = -1
								date = fromToDates[1].strip()
								while(date[end].isalpha()):
									end -= 1
								toDateMonth = date[end+1:]
								toDateMonth = toDateMonth[:3].capitalize()
								start = 0
								while(date[start].isdigit()):
									start += 1	
								toYear = date[:start]
								if(len(toYear)==2):
									if(int(toYear)<60):
										toYear = "20" + toYear	
									else:	
										toYear = "19" + toYear
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
										toMonthNum = (dic.get(toDateMonth) - 1)
										dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}
										toDateMonth = dic2.get(str(toMonthNum))
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
											toMonthNum = (dic.get(toDateMonth) - 1)
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
									toMonthNum = int(dic.get(toDateMonth) - 1)
									toYear = int(toDate[-4:])
									if(toMonthNum==0):
										toMonthNum = 12
										toYear -= 1
									dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}
									toDateMonth = dic2.get(str(toMonthNum))
									
									toDate = toDateMonth + "-" + str(toYear)
									if(fromYear == toYear):
										test = int(toMonthNum) - int(fromMonthNum)
									else:
										test = ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
									if(test<0):
										toDate = datetime.date.today().strftime("%b-%Y").capitalize()
										toDateMonth = toDate[:3]
										toYear = toDate[-4:]
										dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
										toMonthNum = (dic.get(toDateMonth) - 1)
								else:
									toDate = datetime.date.today().strftime("%b-%Y").capitalize()
									toDateMonth = toDate[:3]
									toYear = toDate[-4:]		
				else:
					datePartList = [a[1] for a in fromToDates]
					datePartList = [x for x in datePartList if x is not None]
					fromToDates = [a[0] for a in fromToDates]
					#print ("EHALO",fromToDates,datePartList)
					if (len(fromToDates) == 1):
						if(not datePartList):
							fromDate = self.FormatDate(fromToDates[0])
						else:
						 	fromDate = self.FormatDate(fromToDates[0].replace(datePartList[0],""))	
						if(j==0):
							toDate = self.FormatDate("present")
						else:
							if(j!=(len(companySubBlocks)-1) or (flg==0)):
								#print (tempDate)
								toDate = self.FormatDate(tempDate)
								toDateMonth = toDate[:3]
								#print (fromDate,toDate,toDateMonth)
								dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
								if(toDate[:2].isalpha()):
									toMonthNum = (dic.get(toDateMonth) - 1)
								else:
									if(toDate[1].isdigit()):
										print (toDate)
										toMonthNum = int(toDate[:2]) - 1
									else:
										toMonthNum = int(toDate[:1]) - 1	
								dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}
								#print (toMonthNum)
								toDateMonth = dic2.get(str(toMonthNum),toDateMonth)
								#print (toDateMonth)
								toYear = toDate[-4:]		
								toDate = toDateMonth + "-" + toYear
								someflg = 1
								fromDate = (self.removeSpecialChars(fromDate).strip())
								fromDateMonth = fromDate[:3]
								if(not fromDateMonth.isalpha()):
									if(fromDateMonth[1].isdigit()):			
										fromMonthNum = int(fromDateMonth[:2],fromMonthNum)
									else:
										fromMonthNum = int(fromDateMonth[:1],fromMonthNum)	
									fromDateMonth = dic2.get(str(fromMonthNum),fromDateMonth)
								else:
									fromMonthNum = dic.get(fromDateMonth)
								if(int(str(fromMonthNum)[0])==0 and len(str(fromMonthNum))==2):
									fromMonthNum = fromMonthNum[1]	
								fromYear = fromDate[-4:]
								fromDate = fromDateMonth + "-" + fromYear
								if(fromYear == toYear):
									test = int(toMonthNum) - int(fromMonthNum)
								else:
									#print (fromDate,toDate,fromDateMonth,toDateMonth,fromYear,toYear)
									test = ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
								if(test<0):
									toDate = datetime.date.today().strftime("%b-%Y").capitalize()
									toDateMonth = toDate[:3]
									toYear = toDate[-4:]
									dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
									toMonthNum = (dic.get(toDateMonth) - 1)
							else:
								toDate = datetime.date.today().strftime("%b-%Y").capitalize()
								toDateMonth = toDate[:3]
								toYear = toDate[-4:]	
					else:
						if (j==0):
							flg = 1	
						if(not datePartList):	
							fromDate = self.FormatDate(fromToDates[0])
							toDate = self.FormatDate(fromToDates[1])
						else:
							fromDate = self.FormatDate(fromToDates[0].replace(datePartList[0],""))
							toDate = self.FormatDate(fromToDates[1].replace(datePartList[1],""))
						#print (repr(fromDate),repr(toDate))
					fromDateMonth = self.removeSpecialChars(fromDate[:3]).strip()
					toDateMonth = self.removeSpecialChars(toDate[:3]).strip()
					#print (repr(fromDateMonth),repr(toDateMonth))

				#print ("####",fromDate,toDate,"####")	
				if(onlyYearFlag==1):
					totalMonthsOfExperience = ((int(toYear) - int(fromYear))*12)
					tempDate = fromYear
				elif(onlyMonthFlag==1):
					totalMonthsOfExperience = fromToDates[0]
					tempDate = "unspecified"	
				else:
					if(fromDateMonth.isdigit()):				
						fromMonthNum = int(fromDateMonth)
						dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}	
						fromDateMonth = dic2.get(str(fromMonthNum))
						fromYear = fromDate[-4:]
						fromDate = fromDateMonth + "-" + fromYear
					if(toDateMonth.isdigit()):
						toMonthNum = int(toDateMonth)
						dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}	
						toDateMonth = dic2.get(str(toMonthNum))
						#print (toMonthNum)
						toYear = toDate[-4:]
						toDate = toDateMonth + "-" + toYear
					tempDate = fromDate	
					dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
					if(fromDateMonth.isalpha()):
						fromMonthNum = dic.get(fromDateMonth, fromDate[:2])
					else:
						if(fromDate[1].isdigit()):
							fromMonthNum = int(fromDate[:2])	
						else:
							fromMonthNum = int(fromDate[:1])	
					if(toDateMonth.isalpha()):
						toMonthNum = dic.get(toDateMonth, toDate[:2])
					else:
						if(toDate[1].isdigit()):
							toMonthNum = int(toDate[:2])	
						else:
							toMonthNum = int(toDate[:1])	
					if(int(str(fromMonthNum)[0])==0 and len(str(fromMonthNum))==2):
						fromMonthNum = fromMonthNum[1]
					dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}	
					if(str(fromMonthNum).isdigit()):
						fromDateMonth = dic2.get(str(fromMonthNum),fromDateMonth)
					if(str(toMonthNum).isdigit()):	
						toDateMonth = dic2.get(str(toMonthNum),toDateMonth)
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
				TitlesRegex = r"( )?( |\,|\"|\-|\-|\:|\.|^|\{|\(|\))( )?(" + TitlesRegex + r")( )?( |\"|\,|\-|\-|\:|\.|\}|\(|\))( )?"
				#print (TitlesRegex)
				desgObject = re.compile(TitlesRegex, re.I|re.M)
				testList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,dateString["AreaToScan"])]
				if(dateString["AreaToScanFlag"] == 0):
					DesgList = testList
				else:
					DesgList = []
					TitlesRegex	= '|'.join(Titles)
					print ("^^^^^^\n\n",dateString["AreaToScan"],"\n\n^^^^^^")
					otherDesg = self.isGenuine(originalEmpBlock, dateString["AreaToScan"], "(" + TitlesRegex + ")")
					#print (otherDesg)
					TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|((\()|\-|(\/)))"
					desgObject = re.compile(TitlesRegex, re.I|re.M)	
					for desg in otherDesg:
						tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
						#print (desg)
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
			for (i,outputListElem) in enumerate(listElem["WorkExperience"]):
				if(outputListElem["totalMonthsOfExperience"]<0):
					listElem["WorkExperience"].pop(i)
		return (finalList)

	def GetExpAsync(self):
		try:
			self.ReturnResult= self.returnListforCSV(self.designationTenureParser())
			self.isResult = True
		except:
			self.start = timeit.default_timer()
				try:
					self.ReturnResult= self.returnListforCSV(self.designationTenureParser())
					self.isResult = True
				except:
					self.start = timeit.default_timer()
					try:
						self.ReturnResult= self.returnListforCSV(self.designationTenureParser())
						self.isResult = True
					except:
						self.ReturnResult = ["Header/Company/Designation Master incomplete"]
						self.isResult = True	

	def AllParsersCall(self):
		ParsedDetails = {}
		ParsedDetails["Education"] = []
		try:
			import timeit,_thread
			self.start = timeit.default_timer()
			self.isResult = False
			self.ReturnResult = []
			 _thread.start_new_thread(GetExpAsync,())
			while(((timeit.default_timer() - self.start)<10) and (not self.isResult)):
				pass
			ParsedDetails["Experience"] = self.ReturnResult
		except (KeyboardInterrupt, SystemExit):
			ParsedDetails["Experience"]  = ["TestSeparately"]
			pass			
		ParsedDetails["Skills"] = []
		return ParsedDetails


def main():	
	input = open("input55.txt","r")
	input = input.read()
	#print (repr(input))
	input = "Amit Babaji Hule\n\n502/5 Mandar Niketan N.M.Joshi Marg Byculla West Mumbai:400027\n\nhule.amit@rediffmail.com\n\nMobile No:9870902115.\n\n\n\nBRIEF OVERVIEW \n\n\n\n6 Years of experience in Banking Industry \n\nResult oriented and ready to accept challenges\n\nHardworking and innovative, with multi tasking abilities and strong self-believe.\n\n\n\nPROFESSIONAL EXPERIENCE\n\nCurrently Engaged with:\n\nRatnakar Bank \t\t\t\t\t\t\tFrom  September 2011\n\nPersonal Banker \n\nMumbai\n\n\n\n\tJob Profile:\n\n\t\n\n\t             \n\n\tHandling portfolio of 150 customers and their total average balance of 4.5 to 5.0Cr.\n\n\tNew customer acquisition.\n\n\tOpening CASA ,Term Deposits.\n\n\tServicing the Customer & Managing Key Relationships.\n\n\tCross selling of products like Life Insurance, General Insurance, Mutual funds.\n\n\tKnowledge of Asset Product.\n\n\tKnowledge of Finnacle System.\n\n\tKey Achievements:        \n\n\t\n\n\tPromoted from RO CASA to Personal Banker.\n\n\tWon the Award from Asset Head on Outstanding Performance on Home Loan.\n\n\tWon the Award on Life Insurance and General Insurance Contest\n\n\tWon the Award for the Outstanding Performance for the Current Account from the Regional Head. \n\n\tWon Award from National Head on Outstanding Performance in Products Traning.\n\n\tWon the Award for Highest Saving Account Nos from Regional Head.\n\n                                                       \n\n\t\n\n\t\n\nICICI Bank\n\nOfficer\n\nMumbai\t\t\t\t\t\t\t\tFrom   November 2009\n\n\t\t\t\t\t\t\t\t\t   To   September 2011\n\nICICI Bank is India\xe2\x80\x99s second largest bank. ICICI Bank offers a wide range of banking products and financial services to corporate and retail customers through a variety of delivery channels and through its specialised subsidiaries and affiliates in the areas of investment banking, life and non-life insurance, venture capital and asset management.\n\n\t\t\t \t\t\t\t\n\n\tJob Profile:\n\n\t\n\n\tNew customer acquisition.\n\n\tOpening Saving Account, Term Deposits.\n\n\tServicing the Customer & Managing Key Relationships.\n\n\tCross selling of products like Life Insurance, General Insurance, Gold Coins.\n\n\t\n\n\t\n\n\t\n\n\t\n\n\t\n\n\t\n\n\tKey Achievements:        \n\n\t\n\n\tRated No.1 for the performance for the FY 2010-2011.\n\n\tWon the Award for the Outstanding Performance for the Savings Account from the Zonal Head.\n\n\tWon the Achiever Award for Saving Account Nos from Regional Head.\n\n                                                       \n\nICICI Bank ltd\t\t\t\t\t\t\t\tFrom  July 2007\n\nSales Executive\n\n\n\nJob Profile:\n\nNew Customer acquisition\n\n\tOpening Saving Account ,Term Deposits.\n\n\n\n\n\n\n\n                                                               EDUCATION            \n\nDegree                          Institution                       Year                      Percentage\n\n\n\nB.Com                      Mumbai University                2007                              48 %  \t\n\nH.S.C.\t                    Mumbai University                2004\t\t             61 %\n\nS.S.C.     \t       Mumbai University                2002\t\t             54 %\t\n\n\n\n\n\n\n\n\n\nExecute strategies to drive sales, augment turnover and achieve desired targets.\n\n           Identify and pursue business opportunities through market surveys and mapping         \n\n           as per targeted plans as well as through lead generation.\n\n\n\nIdentify new market segments and tap profitable business opportunities.\n\n           Evolve market segmentation & penetration strategies to achieve product wise \n\n           targets.\n\n\n\nEnable business growth by developing and managing a network of Channel Partners and monitor day to day operations.\n\n\n\nCreate an environment that sustains and encourage high performance; motivate teams in optimizing their contribution levels.\n\n\n\nCOMPUTER KNOWLEDGE\n\n\n\nOperating System\t: Windows 95-98-2000-2003\n\nPackages\t\t: MS \xe2\x80\x93 Office, Tally 6.3 &7.2, Fact , Ace\n\nHandy in Excel\n\nInternet Knowledge\n\nSTRENGTHS\n\n\n\nVery much result oriented and ready to accept challenges\n\nHardworking, innovative and analytical with an ability to identify loopholes and plug the same to achieve desired results\n\nAbility to handle multiple tasks simultaneously\n\nGood team player with an ability to lead and motivate teams\n\nConstant learner with an ability to imbibe new knowledge with ease\n\nGood communication and inter personal skills\n\n\n\n\n\n\n\n\n\nINTEREST\n\n\n\nKeen Interest In Cricket\n\nListing Old Songs.\n\n\n\nPERSONAL DETAILS\n\n\n\nDate of birth\t\t:\t28th November 1984\n\nMarital status\t\t: \tMarried\n\nMobility                           :            Flexible\n\nNationality                      :            Indian\n\nLanguages known\t:\tEnglish, Hindi and Marathi\n\n\n\nPage 1 of 3"
	#print (repr(input))
	obj = GenericResumeParser(repr(input))
	workExperienceList = obj.designationTenureParser()
	print (workExperienceList)
main()
