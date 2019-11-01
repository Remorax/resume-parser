import xml.etree.ElementTree as ET
import re, datetime
import glob, os, json
import csv
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
		self.DurationRegex = r"[\s\r\t\n]*.*?(Duration|Since|From|Working For|Workingfrom)?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{1,4})\s*(\-{1,3}|/|\s|to|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?\s*((\s|\n|\-{1,3}|\.|,|’|'|‘|/|\d{1,2}|\d{1,4})*.*\\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)*\\b(\s|\n|\-{1,3}|\.|,|’|'|‘|)*\d{1,4}|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?"		
		self.dateStringRegex = r"\b(\,)?(\()?((((Since|From|Working from)?( )?((((\d{1,2}(rs|rd|st|nd)?( )?( |\/|\\|\.|\-)( )?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b|((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?(\d{1,2}(rs|rd|st|nd)?( )?( |\/|\\|\.|\-)( )?)?))( )?( |\-{1,3}|\.|,|’|'|‘)+( )?\d{2}(\d{2})?(\'|\’)?( )?)|((\d{1,2}(rs|rd|st|nd)?( )?( |\/|\\|\.|\-)( )?)?\d{1,2}( )?(\/|\\|\-)( )?\d{2}(\d{2})?)|((\d{2}(\d{2})?)( )?(\/|\\|\-)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?)))(( )?(\-{1,3}|\/| |\–{1,3}|to|till)?( )?((((((\d{1,2}(rs|rd|st|nd)?( )?( |\/|\\|\.|\-)( )?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December))|((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?(\d{1,2}(rs|rd|st|nd)?( )?( |\/|\\|\.|\-)( )?)?))( )?( |\-{1,3}|\.|,|’|'|‘|\/|\\)+( )?\d{2}(\d{2})?(\'|\’)?( )?))|(date|now|the date|present|present date|the present date|to till date|till date|today|current)|((\d{1,2}(rs|st|nd)?( )?( |\/|\\|\.|\-)( )?)?\d{1,2}( )?( |\/|\\|\.|\-)( )?\d{2}(\d{2})?)|((\d{2}(\d{2})?)( )?(\/|\\|\.|\-)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b( )?)))?)|((\d{2}(\d{2})?( )?(\-{1,3}|\/| |\–{1,3}|to|till)?( )?((date|now|the date|present|present date|the present date|to till date|till date|t til date|today|current)|(\d{2}(\d{2})?))))|((Since|From|Working from|Currently working)(\d{2}(\d{2})?))|((for|from|for a duration of|since|till)\d{1,2}( )(months))|(\d{1,2}( )(months|month|year|years)( )(work)))(\))?"
		self.dateRegex = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{2}(\d{2})?)|(\d{1,2}(\s|\/|\\|\.|\-)\d{2}(\d{2})?)( )"
		self.dateRegex2 = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)( )\b\d{1,2}( )?(\s|\-{1,3}|\.|\,|’|'|‘)*( )?\d{2}(\d{2})?)\b"
		self.dateRegex3 = r"\b(\d{2}(\d{2})?)( )?(\/|\\|\.|\-)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b"
		self.designationRegex = r"(Job Title|Designation|Position|Role|Working\s*as\s*a|Working\s*as\s*an|Worked\s*as\s*an|Worked\s*as\s*a|Promoted\s*to\s*a|Promoted\s*to\s*an|Promoted\s*to|Worked\s*as|Working\s*as|Work\s*as|Work\s*as\s*a|Work\s*as\s*an)\s*\d{0,2}\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.designationRegex2 =r"\s*(as|as\s*a|as\s*an|Profile|Profile\s*\&\s*Product)\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.bodyDesignationRegex = r"^(?!.*(Reporting to|Awarded by|Leading a team of|implement Training to|Won (the|a|an)?(.*)?Award|leading|from|renowned)).*\b"	
	def FormatDate(self,date):
		if(date!="None" or date!="" ):
			if(date.lower() in ['onwards','till date','till now','till the date','till present','present','till today','till','date','continue']):
				date = datetime.date.today().strftime("%b-%Y")
				return date.capitalize()
			date = re.sub("(\s|\-{1,3}|\.|,|’|'|‘)", '$', date)
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

	def CompanyBaseSections(self,headRegex):
		testDocument = self.ResumeText
		regex = re.compile("(\r|\n)\s*(\u2022|\u2023|\u25E6|\u2043|\u2219)?("+headRegex+")\s*( |\:|\-|\-(\s)?\:|\:(\s)?\-|>|\-\s*\>)?( )?\s*(\r|\n)",re.M)
		headRegex2List = []
		headRegex3List = []
		for header in headRegex:
			headRegex2List.append(header.upper())
			headRegex3List.append(header.lower().title())
		headRegex2List = list(set(headRegex2List))
		headRegex2 = '|'.join(headRegex2List)
		headRegex3List = list(set(headRegex3List))
		headRegex3 = '|'.join(headRegex3List)	
		regex2 = re.compile("("+headRegex2+")\s*( |\:|\-|\-\s*\:|\:\s*\-|>|\-\>)?\s*",re.M)
		regex3 = re.compile("("+headRegex3+")\s*( |\:|\-|\-\s*\:|\:\s*\-|>|\-\>)?\s*",re.M)
		dmatch=re.findall(regex,testDocument)
		if(len(dmatch)>0):
			position = [(m.start(0), m.end(0), m.group()) for m in re.finditer(regex, testDocument)]
			ans = position[0][0]
			ansTitle = position[0][2]
			for tupleelem in position:
				restext = self.ResumeText[tupleelem[0]:(tupleelem[1]+1)]
				upperRestext = restext.upper()
				if (restext == upperRestext):
					ans = tupleelem[0]
					ansTitle = tupleelem[2]
			return (ans,3,ansTitle)
		else:
			position = [(m.start(0), m.end(0), m.group()) for m in re.finditer(regex2, testDocument)]
			if(position):
				return (position[0][0],2,position[0][2])
			else:
				position = [(m.start(0), m.end(0),m.group()) for m in re.finditer(regex3, testDocument)]
				if(position):
					return (position[0][0],1,position[0][2])
			return (0,0,"")

	def RemoveLowerCase(self, RegEmploymentHeads):
		returnList = []
		RegList = RegEmploymentHeads.split('|')
		for (n,i) in enumerate(RegList):
			returnList.append(i.upper())
			returnList.append(i.title())
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
		PriorityDict = {}
		result = self.CompanyBaseSections(self.getHeader('educationHeader'))
		PriorityDict["Education"] = result[1]
		allBlocksList.append({'BlockName':"Education",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('accomplishmentsHeader'))
		PriorityDict["Accomplishments"] = result[1]
		allBlocksList.append({'BlockName':"Accomplishments",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('awardsHeader'))
		PriorityDict["Awards"] = result[1]
		allBlocksList.append({'BlockName':"Awards",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('extracurricularHeader'))
		PriorityDict["ExtraCurricular Activities"] = result[1]
		allBlocksList.append({'BlockName':"ExtraCurricular Activities",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('miscHeader'))
		PriorityDict["Miscellaneous"] = result[1]
		allBlocksList.append({'BlockName':"Miscellaneous",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('summaryHeader'))
		PriorityDict["Summary"] = result[1]
		allBlocksList.append({'BlockName':"Summary",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('skillsHeader'))
		PriorityDict["Skills"] = result[1]
		allBlocksList.append({'BlockName':"Skills",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('employmentHeader'))
		PriorityDict["Employment"] = result[1]
		allBlocksList.append({'BlockName':"Employment",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('credibilityHeader'))
		PriorityDict["Credibility"] = result[1]
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
			employmentBlockRegexObj = re.compile(r"(\r|\n)\s*(\u2022|\u2023|\u25E6|\u2043|\u2219)?("+self.getHeader('employmentHeader')+r")\s*(\d{1,2})( |\:|\-|\-(\s)?\:|\:(\s)?\-|>|\-\s*\>|\d{1,2})?( )?\s*(\r|\n)",re.M)
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

		designationFile = open("designations.txt","r")
		designationFile = designationFile.read()
		designationList = designationFile.split('\n')
		Titles = ['Officer','Area Sales Manager','Processing Assistant','BDR','Manager \– Sales Development','Life Advisor','Tally Teacher','Management Trainee','CCE','BANK ASSURANCE OFFICER','JUNIOR OFFICER','TEAM LEADER','Acquisition  Manager','Business Associates','Business Associate','Factuality','SALES MANAGER\: PERSONAL BANKING','Sr\. Business Associates','Sr. Chanel Sales Manager','Tele\-broking Executive','Accounts Officer','Senior Associate \- Operations','zonal operational manager','Senior Sales Officer','branch co\-ex','RM','Senior Executive','Financial Service Manager','AKRM Band\-A','DKRM Band\-B','Senior Financial Service Manager','Customer Service Manager','Asset Head','Regional Head','RO CASA','Zonal Head','National Head','Sales Development Manager','SBA','Store Manager','Recruitment \& training manager','Liability desk counsellor\/team leader','Recruitment and developement Manager','Privilege Banker\/Relationship manager','Investment Manager','Officer\-sales','SALES MANAGER','Client relationship partner','Contract sales executive','Lead generator','Nemmadi Project Taluka Co\-ordinater','MANAGER DISTRIBUTION','SLI Department Finance Co\-Executive','Team Manager','CBE','Senior Corporate Agency Manager','Branch Sales officer','Administrative Officer','Corporate Agency Manager','Gold Financial Service Consultant','Senior Financial Service Consultant','Sales Coordinator','Financial Service Consultant','JUNIOR OFFICER','Senior Corporate Agency Manager','Assistant Accountant','Senior Business Development Executive','Officer \(CASA\)','Electronic Banking Support Executive','Software Implementation Executive','Deputy Sales Manager','Team Leader','Senior Business Executive','CSE','Deputy Manager \(Branch Banking\)','BDE','Admin Executive','Sales Officer','Office Administrator','Branch Corporate-executive','Senior Officer','Associate Relationship Manager','Relationship Officer','Salary Officer Sales','Modeling Associate','Associate Service Finance Manager','Branch Corporate\-executive','Account Head','Administration Manager','Auditor','Grade Officer Sales','Development Manager','Senior Customer Care Associate','S\.F\.S\.M\.','ACCOUNT ASSISTANT','ACCOUNT Staff','Client Relationship Partner','Assistant Manager','Assistant Manager in Operations','Sr.sales Executive','Credit Operation Officer\(Astt\. Manager \)','Gold Appraiser','Motor Insurance\, Travel \& Health Insurance\( Sales Officer\)','Backup To teller', 'Brach CASA target \(Astt\. Manager \)','Branch CASA target \(Astt\. Manager \)','Sales Officer','Business Development Executive','Business Development Executive\(BDE\)','Customer Service Officer','Sales Co\-ordinator','Analyst \(Global Finance \& Foreign Exchange Operation\)','Analyst \(Foreign Exchange Reconciliation\)','Area Manager','Branch Manager \– Ettumanoor Branch','Customer Manager','Tax Analyst','Advance Tax Analyst','JC\/Customer Service Executive\/BIC','Area Sales Manager',' Value Banker','Chef de partie','Commie I','Sales Manager \( Bank Channel \)','Sales Manager','Front Desk Officer','Sales Officer\-CASA','Sales Executive \(Salary \& TASC Accounts\)','Marketing Executive','Relationship Manager','Executive','Agency Manager','Associate Manager \(Sales\)','Asst. Manager \(Sales\)','Asst. manager','Center Head','Business Development Officer','Branch Development Resource','Call center agent','Account Manager – Sales','Liability Co-Ex','Sales Executive \– Corporate Sales','Officer\-Sales','Junior Officer','Manager','Business Development Manager','Sr. Business Development Manager','Sales Team Leader','Senior Business Development Manager','Supervisor','Sr. Sales Executive','Senior Sales Manager','Sales Manager','Unit Manager','Accountant','Sales Executive','Corporate Sales Manager','Senior Manager','Quality Checker','Sales Coordinator','Team Manager','Equity Advisor','Financial Advisor','Sr\. Dealer','Finance Executive','Deputy Manager','Branch Head','Branch Manager','Wealth Manager','Senior Relationship Manager','Senior Relationship Officer','Investment Counselor','Junior Officer Sales','Personal Banker']
		for (i,designation) in enumerate(designationList):
			Titles.append(designation.replace('/','\/').replace('(','\(').replace(')','\)').replace('-','\-'))
		desgElement = self.designationroot.findall('d')
		for desg in desgElement:
			for variant in desg.findall('v'):
				Titles.append(variant.text.replace('&amp;','&'))
		Titles = list(set(Titles))
		Titles = sorted(Titles, key=len, reverse=True)
		for (i,title) in enumerate(Titles):
			titleWords = title.split()
			Titles[i] = ' '.join(titleWords)
		TitlesRegex	= '|'.join(Titles)
		TitlesRegex = r"(\")?(" + TitlesRegex + r")\s*(\.|\,|\")?\s\s*"
		ConjuctionRegex = r"(\s*(,|/|&|and|and\s*later|and\s*later\s*a|and\s*later\s*an|and\s*a|and\s*an)\s*(Job Title|Designation|Position|Role|Working\s*as\s*a|Working\s*as\s*an|Worked\s*as\s*an|Worked\s*as\s*a|Promoted\s*to\s*a|Promoted\s*to\s*an|Promoted\s*to|Worked\s*as|Working\s*as|Work\s*as|Work\s*as\s*a|Work\s*as\s*an|as|as\s*a|as\s*an|Profile|Profile\s*\&\s*Product)?\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*" + TitlesRegex + r")*"
		self.designationRegex += TitlesRegex
		self.designationRegex += ConjuctionRegex
		self.designationRegex2 += TitlesRegex
		self.designationRegex2 += ConjuctionRegex
		designationRegexObj = re.compile(self.designationRegex, re.I|re.M)
		designationIterator = re.finditer(designationRegexObj, employmentBlock)
		dmatch = re.findall(designationRegexObj, employmentBlock)
		if(not dmatch):
			designationRegexObj = re.compile(self.designationRegex2, re.I|re.M)
			designationIterator = re.finditer(designationRegexObj, employmentBlock)
		allDesgList = []
		allowedIndices = []
		for designation in designationIterator:
			designationObject = re.compile(TitlesRegex, re.I|re.M)
			desgIterator = re.finditer(designationObject, designation.group())
			designationWords = designation.group().split()
			curr = designation.start()
			for desg in desgIterator:
				if desg.start() not in allowedIndices:
					allDesgList.append(desg.group())
			allowedIndices.append(curr)
			for (i,designationWord) in enumerate(designationWords):
				if(i != (len(designationWords)-1)):
					if designationWord in Titles:
						allowedIndices.append(curr + len(designationWord) + 1)
						curr = curr + len(designationWord) + 1
		if(employmentBlockIndex!=(len(allBlocksList)-1)):
			nextBlock = allBlocksList[employmentBlockIndex+1]
			nextBlockName = nextBlock['BlockName']
			priority = PriorityDict[nextBlockName]
			if(priority<2):
				txt = self.ResumeText
				txtMinusEmploymentBlock = txt.replace(employmentBlock,"")
				curr = employmentBlockIndex + 1
				EndingIndex = len(txtMinusEmploymentBlock) - 1
				while (curr<9):
					currBlock = allBlocksList[curr+1]
					currBlockName = currBlock['BlockName']
					priority2 = PriorityDict[currBlockName]
					if(priority2>1):
						EndingIndex = txtMinusEmploymentBlock.find(currBlockName)
						break
				txtMinusEmploymentBlock	= txtMinusEmploymentBlock [:EndingIndex]					
				designationIterator = re.finditer(designationRegexObj, txtMinusEmploymentBlock) 
				for designation in designationIterator:
					designationObject = re.compile(TitlesRegex, re.I|re.M)
					desgIterator = re.finditer(designationObject, designation.group())
					designationWords = designation.group().split()
					curr = designation.start()
					for desg in desgIterator:
						if desg.start() not in allowedIndices:
							allDesgList.append(desg.group())
					allowedIndices.append(curr)
					for (i,designationWord) in enumerate(designationWords):
						if(i != (len(designationWords)-1)):
							if designationWord in Titles:
								allowedIndices.append(curr + len(designationWord) + 1)
								curr = curr + len(designationWord) + 1	

		for (i,designation) in enumerate(allDesgList):
			allDesgList[i] = designation.strip()
		


##### Commment this out
		allDesgList = []
		




		if(not allDesgList):
			empElement = self.employerroot.findall('emp')
			Companies = ['KINGFISHER AIRLINES LTD','Times Business Solutions - TimesJobs','Karvy Stock Broking Ltd','Shelter ( Citi Bank Associate )','Fast Track Management Services Pvt Ltd','North India Finserve Pvt Ltd','India infoline Ltd','Centurion Finance','Anand Rathi Share And Stock Brokers Ltd','HDFC SLIC','India Today Group','Key Computer Academy','Kotak Mahindra Old Mutual Life Insurance','PNB MetLife (Karnataka Bank)','Kotak Old Mutual Life Insurance Co. LTD','Birla Sun Life Insurance Company LTD','Qatar Airways','Hyatt Regency','HDFC Life Insurance','HDFC LIFE INSURANCE COMPANY Ltd','IDBI BANK Ltd','Development Credit Bank Ltd','Allegro Capital Advisors (P) Limited','Mahindra Rural Housing Finance Limited','Travancore Pravassy Housing Finance Limited','HBL Global Pvt Ltd','Apple Tree Chits India (P) Limited','VODAFONE CALL CENTER','MASCOAT EDUCATION LTD','VADILAL INDUSTRIES','ICICI BANK (ICICI PRUDENTIAL LIFE INSURANCE CO, Thrissur)','Soft Tech Institute','Shiva Sangam Finance','ING Vysya Bank','Deutsche Asset Management Pvt. Ltd','TATA-AIA Life Insurance Company Ltd','Universal Sompo General Insurance Company Ltd','Apollo Munich Health insurance','Cholamandalam General Insurance Company Ltd','Hutchison Essar Cellular Ltd','ICICI Lombard General Insurance Company Ltd','STANDARD CHARTERED BANK','Ratnakar Bank','RBL Bank LTD','RBL Bank','STANDARD CHARTERED BANK','SBI Life Insurance company Ltd(Bancassaurance)','ING Vysya Bank','HSBC Invest Direct (India) Ltd.','CD Equisearch Pvt Ltd','Religare Securities Ltd','ICICI Bank Limited','Jardine Lloyd Thompson India PVT. LTD.','BALAJEE FRAGRANCE','Sony India Pvt. Ltd.','ASIAN INTERNATIONAL','RELIANCE COMMUNICATION','KOTAK MAHINDRA GROUP','VODAFONE ESSAR GUJARAT LTD','INDUSIND BANK','Deutsche Bank','INDUSIND BANK LTD','Angel Broking Pvt Ltd','United Insitute Of Management','HDFC Securities Ltd','Reliance Securities Ltd','HDFC standard life Insurance Company LTD','AXIS BANK','AXIS BANK LTD','YES BANK LTD.','Capital Experts','Bank Card Services','HDFC BANK LTD.','HDFC BANK LTD','Pratham Software Pvt Ltd','K.J.Marketing, A.V. Marketing','MYSHORE IT SOLUTIONS Pvt Ltd','COMAT TECHNOLOGIES Pvt Ltd','BIRLA SUN LIFE INSURANCE CO LTD','MAX LIFE INSURANCE CO.LTD','Destimoney Securities Pvt. Ltd','Motilal Oswal Securities Ltd','kotak mahindra bank limited','KOTAK MAHINDRA BANK LTD','ICICI BANK LTD','Outfield Management Services','GENIES SHIPPING SERVICES','Globe Capital Market Limited','ICICI BANK','KOTAK SECURITIES','KOTAK SECURITIES LTD','HDFC Life, Bangalore (Bancassaurance)','ICICI Prudential Life Insurance','B.K.B Computers Pvt. Ltd','ING LIFE INSURANCE CO LTD','IBBI FEDERAL LIFE INSURANCE CO LTD','Max New York Life Insurance Co Ltd','Reliance Communications']
			tempEmpBlock = employmentBlock
			tempEmpBlock = ' '.join(employmentBlock.split())
			for i in empElement:
				element = i.text.replace("&amp;", "&")
				Companies.append(element)
			allPositionsList = []
			Companies = list(set(Companies))
			for (i,Company) in enumerate(Companies):
				Companies[i] = Company.replace('/','\/').replace('(','\(').replace(')','\)').replace('-','\-')
			Companies = sorted(list(set(Companies)), key=len, reverse=True)	
			CompanyRegex = "(\,|M\/S)?( |\-|\–)(" + '|'.join(Companies) + ")( |\.|\,)"
			TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
			TitlesRegex = r"( )?( |\,|\-|\"|\-|\:|\.)( )?(" + TitlesRegex + r")\s*( )?( |\,|\"|\-|\-|\:|\.)( )?"
			compRegexObj = re.compile(CompanyRegex, re.I|re.M)
			companyList = [{"Company": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(compRegexObj, tempEmpBlock)]
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
							for (i,date) in enumerate(DateList):
								if(i!=(len(DateList)-1)):
									areaToScan = possibleSubBlock[DateList[i]["EndingIndex"]:DateList[i+1]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									DateList[i]["AreaToScan"] = areaToScan	
									DateList[i]["AreaToScanFlag"] = 0			
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
								DateList[i]["AreaToScanFlag"] = 0		
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
				curr = 0
				if(isRubbish==-1):
					TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
					TitlesRegex = r"( )?( |\"|\,|\-|\-|\:|\.)( )?(" + TitlesRegex + r")\s*( )?( |\"|\,|\-|\-|\:|\.)( )?"
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
							possibleSubBlock = possibleSubBlock.replace(textBeforeCompany,"")
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
										DateList[i]["AreaToScanFlag"] = 0			
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
									DateList[i]["AreaToScanFlag"] = 0		
									DateList[i]["AreaToScan"] = areaToScan
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
					TitlesRegex = r"( )?( |\,|\-|\"|\“|\-|\:|\.|\()( )?(" + TitlesRegex + r")\s*( )?( |\"|\”|\,|\-|\-|\:|\.|\))( )?"
					for (i,company) in enumerate(companyList):
						if (i!=(len(companyList)-1)):
							possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:companyList[i+1]["StartIndex"]]
						else:
							possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:]
						possibleSubBlock = textBeforeCompany + possibleSubBlock	
						DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
						DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
						if(i!=(len(companyList)-1)):
							textAfterLastDate = possibleSubBlock[(DateList[len(DateList)-1]["EndingIndex"]):]
							DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
							DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textAfterLastDate)]						
							if(not DesgList):
								textToReplace = possibleSubBlock[(DateList[len(DateList)-1]["StartIndex"]):]
								possibleSubBlock = possibleSubBlock.replace(textToReplace,"")
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
										DateList[i]["AreaToScanFlag"] = 0			
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
											bodyDesignationRegex = r"^(?!.*(Reporting to|Awarded by|Leading a team of|implement Training to|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?\b(and)?(" + '|'.join(Titles) + r")\b" 
											desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
											txt = self.ResumeText
											wordList = areaToScan.split(' ') 
											while '.' in wordList: wordList.remove('.') 
											wordList = list(filter(None, wordList))
											orgRegex = ""
											if(len(wordList)<20):
												start = int(len(wordList)/2)
												end  = int(len(wordList) - start)		
											else:
												start = 10
												end = 10
											count = 0	
											while(count<start):
												if(count!=(start-1)):
														 (wordList[int(count)] + r"\s*(\)|\.|\()*\s*")
												else:
													orgRegex += wordList[int(count)]	 
												count += 1
											orgRegex += r"[\d\D]*"
											count = end
											while(count>0):
												if(count!=1):
													orgRegex += (wordList[int(len(wordList)-count)] + r"\s*(\)|\.|\()*\s*")
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
											TitlesRegex = r"\b(" + TitlesRegex + r")\b"
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
									DateList[i]["AreaToScanFlag"] = 0		
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
					for (i,company) in enumerate(companyList):
						if (i!=(len(companyList)-1)):
							possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:companyList[i+1]["StartIndex"]]
						else:
							possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:]
						possibleSubBlock = textBeforeCompany + possibleSubBlock			
						DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
						DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
						if(i!=(len(companyList)-1)):
							textAfterLastDate = possibleSubBlock[(DateList[len(DateList)-1]["EndingIndex"]):]
							DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
							DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, textAfterLastDate)]
							if(not DesgList):
								textBeforeCompany = ''
							else:
								textToReplace = textAfterLastDate[(DesgList[len(DesgList)-1]["StartIndex"]):]
								possibleSubBlock = possibleSubBlock.replace(textToReplace,"")
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
										DateList[i]["AreaToScanFlag"] = 0			
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
											bodyDesignationRegex = r"^(?!.*(Reporting to|Awarded by|implement Training to|Leading a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?\b(and)?(" + '|'.join(Titles) + r")\b" 
											desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
											txt = self.ResumeText
											wordList = areaToScan.split(' ')  
											while '.' in wordList: wordList.remove('.') 
											wordList = list(filter(None, wordList))
											orgRegex = ""
											if(len(wordList)<20):
												start = int(len(wordList)/2)
												end  = int(len(wordList) - start)
											else:
												start = 10
												end = 10
											count = 0	
											while(count<start):
												if(count!=(start-1)):
													orgRegex += (wordList[int(count)] + r"\s*(\)|\.|\()*\s*")
												else:
													orgRegex += wordList[int(count)]	 
												count += 1
											orgRegex += r"[\d\D]*"
											count = end
											while(count>0):
												if(count!=1):
													orgRegex += (wordList[int(len(wordList)-count)] + r"\s*(\)|\.|\()*\s*")
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
											TitlesRegex = r"\b(" + TitlesRegex + r")\b"
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
									DateList[i]["AreaToScanFlag"] = 0		
									DateList[i]["AreaToScan"] = areaToScan								
							companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
							curr += 1
						else:
							if(curr!=0):
								companySubBlocks[curr-1]["Text"] += possibleSubBlock
								previousDateList = companySubBlocks[curr-1]["DateList"]	
								previousDateListLength = len(previousDateList)
								previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock			
		
			#### Given companySubBlocks get the final output from below:

			flg = 0
			currentDateFlag = 0
			for (j,companySubBlock) in enumerate(companySubBlocks):
				companyObj = re.compile(r"\b.*\b",re.I|re.M)
				company = [(m.group()) for m in re.finditer(companyObj,companySubBlock["Company"].strip().lower().title())]
				finalListElem = {"Company" : company[0]}
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
					fromToDates = [(m.group()) for m in re.finditer(dateObject,dateString["Date"])]
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
											dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}
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
										dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}
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
									dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}
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
							fromDate = self.FormatDate(fromToDates[0])
							toDate = self.FormatDate(fromToDates[1])
						fromDateMonth = fromDate[:3]
						toDateMonth = toDate[:3]
					if(onlyYearFlag==1):
						totalMonthsOfExperience = ((int(toYear) - int(fromYear))*12)
					elif(onlyMonthFlag==1):
						totalMonthsOfExperience = fromToDates[0]	
					else:
						tempDate = fromDate	
						dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
						fromMonthNum = dic.get(fromDateMonth, fromDate[:2])
						toMonthNum = dic.get(toDateMonth, toDate[:2])
						if(int(str(fromMonthNum)[0])==0 and len(str(fromMonthNum))==2):
							fromMonthNum = fromMonthNum[1]
						dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sept", "10": "Oct", "11":"Nov", "12":"Dec"}	
						fromDateMonth = dic2.get(fromMonthNum, fromDateMonth)
						toDateMonth = dic2.get(toMonthNum, toDateMonth)
						fromYear = fromDate[-4:]
						toYear = toDate[-4:]
						if(fromYear == toYear):
							totalMonthsOfExperience += int(toMonthNum) - int(fromMonthNum)
						else:
							totalMonthsOfExperience += ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
					TitlesRegex	= '|'.join(Titles)
					TitlesRegex = r"( )?( |\,|\"|\-|\-|\:|\.)( )?(" + TitlesRegex + r")( )?( |\"|\,|\-|\-|\:|\.)( )?"
					desgObject = re.compile(TitlesRegex, re.I|re.M)
					testList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,dateString["AreaToScan"])]
					if(i!=(len(dateList)-1) or (dateString["AreaToScanFlag"] == 0)):
						DesgList = testList

					else:
						possibleDesgList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,dateString["AreaToScan"])]
						if(len(possibleDesgList)==1):
							DesgList = possibleDesgList
						else:
							DesgList = []
							bodyDesignationRegex = r"^(?!.*(Reporting to|Awarded by|implement Training to|Leading a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from|renowned|best|team of)).*(Promoted as )?\b(and)?(" + '|'.join(Titles) + r")\b" 
							desgObject2 = re.compile(bodyDesignationRegex,re.I|re.M)
							txt = self.ResumeText
							wordList = dateString["AreaToScan"].split(' ')
							while '.' in wordList: wordList.remove('.') 
							wordList = list(filter(None, wordList))
							orgRegex = ""
							if(len(wordList)<20):
								start = int(len(wordList)/2)
								end  = int(len(wordList) - start)
							else:
								start = 10
								end = 10
							count = 0	
							while(count<start):
								if(count!=(start-1)):
									orgRegex += (wordList[int(count)] + r"\s*(\)|\.|\()*\s*")
								else:
									orgRegex += wordList[int(count)]	 
								count += 1
							orgRegex += r"[\d\D]*"
							count = end
							while(count>0):
								if(count!=1):
									orgRegex += (wordList[int(len(wordList)-count)] + r"\s*(\)|\.|\()*\s*")
								else:
									orgRegex += wordList[int(len(wordList)-count)]
								count -= 1
							findOriginalObj = re.compile(orgRegex, re.I|re.M)
							tempSubBlockL = [(m.group()) for m in re.finditer(orgRegex,txt)]
							tempSubBlock = ""
							for i in tempSubBlockL:
								tempSubBlock += i
							otherDesg = [(m.group().strip().lower().title()) for m in re.finditer(desgObject2,tempSubBlock)]
							TitlesRegex	= '|'.join(Titles)
							TitlesRegex = r"\b(" + TitlesRegex + r")\b"
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
					if(flag==1):
						tempList = DesgList
					if(dateListLength<len(DesgList)):
						DesgList = list(set(DesgList))	
					finalListElem["WorkExperience"].append({"From":{"Date":fromDate,"Month":fromDateMonth,"MonthNum":fromMonthNum,"Year":fromYear},"To":{"Date":toDate,"Month":toDateMonth,"MonthNum":toMonthNum,"Year":toYear},"totalMonthsOfExperience":totalMonthsOfExperience,"DesignationList":DesgList})	
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
			print (finalList)	
def main():	
	input = open("input9.txt","r")
	input = input.read()
	obj = GenericResumeParser(input)
	obj.designationTenureParser()
main()
