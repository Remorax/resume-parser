# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re, datetime, time, _thread
from nerForCompany import OrgNER
# from OrgFromNltk import Extract_Org
import glob, os, json
BASE = os.path.dirname(os.path.abspath(__file__))
class GenericResumeParser(object):
	"""
	Resume parser: It gives education details,
	Employement history, Skills, Demographic details

	"""
	def __init__(self,restext):
		self.headersroot = ET.parse(BASE+'/ListData2/headers.zhrset').getroot()
		self.degreesroot = ET.parse(BASE+'/ListData2/degrees.zhrset').getroot()
		self.functionalroot = ET.parse(BASE+'/ListData2/functionalareas.zhrset').getroot()
		self.designationroot = ET.parse(BASE+'/ListData2/designation.zhrset').getroot()
		self.employerroot = ET.parse(BASE+'/ListData2/employer.zhrset').getroot()
		self.institutionroot = ET.parse(BASE+'/ListData2/institution.zhrset').getroot()
		self.skillsetroot = ET.parse(BASE+'/ListData2/skillset.zhrset').getroot()
		##print (restext)
		self.ResumeText = str(re.sub(r'(\\x\w{1,2}|\\u\w{4})',' ',repr(restext)))
		self.ResumeText2 = str(re.sub(r'((\\x\w{1,2})|(\\u\w{4}))',' ',repr(restext))).replace("\n","\\n").replace("\t","\\t").replace("\r","\\r")
		#if ('\xa0' in self.ResumeText2):
			#print ("Yes")
		resumeTxt = ""
		for word in self.ResumeText:
			if(ord(word)<194 and ord(word)!=42):
				resumeTxt += word
		self.ResumeText = resumeTxt
		resumeTxt2 = ""
		for word in self.ResumeText2:
			if(ord(word)<194 and ord(word)!=42):
				resumeTxt2 += word
		self.ResumeText2 = resumeTxt2
		##print (resumeTxt)
		##print (self.ResumeText2)
		self.DurationRegex = r"[\s\\r\\t\\n]*.*?(Duration|Since|From|Working For|Workingfrom)?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\.|,|’|'|‘)*\d{1,4})\s*(\-{1,3}|/|\s|to|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?\s*((\s|\\n|\-{1,3}|\.|,|’|'|‘|/|\d{1,2}|\d{1,4})*.*\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)*\b(\s|\\n|\-{1,3}|\.|,|’|'|‘|)*\d{1,4}|onwards|till date|till now|till the date|till present|present|till today|till|date|continue)?"		
		self.dateStringRegex = r"\,?\(?( |\(|\)|\,|\.|\:|\-|\:\-|\-\:|\;|\&|^)((((Since|From|Working from)? ?(((((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)(\.|\b) ?(\d{1,2}(th|rd|st|nd)? ?( |\/|\\|\.|\-|\–|\,)? ?)?)|((\d{1,2}(rd|st|nd|th)? ?( |\/|\\|\.|\-|\–) ?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b)) ?( |\-{1,3}|\–{1,3}|\.|,|’|'|‘)+ ?\d{2}(\d{2})?(\'|\’)? ?)|((\d{1,2}(rd|st|nd|th)? ?( |\/|\\|\.|\-) ?)?\d{1,2} ?(\/|\\|\-|\–) ?\d{2}(\d{2})?)|((\d{2}(\d{2})?) ?(\/|\\|\-|\–| ) ?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b ?)))( ?(\-{1,3}|\/| |\–{1,3}|to|till|to till)* ?((((((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)(\.|\b) ?(\d{1,2}(th|rd|st|nd)? ?( |\/|\\|\.|\-|\–)? ?)?)|((\d{1,2}(rd|st|th|nd)? ?( |\/|\\|\.|\-|\–) ?)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December))) ?( |\-{1,3}|\–{1,3}|\.|,|’|'|‘|\/|\\)+ ?\d{2}(\d{2})?(\'|\’)? ?))|(date|now|the date|present|present date|the present date|to till date|till date|today|current)|((\d{1,2}(rs|st|nd)? ?( |\/|\\|\.|\-|\–) ?)?\d{1,2} ?( |\/|\\|\.|\-|\–| ) ?\d{2}(\d{2})?)|((\d{2}(\d{2})?) ?(\/|\\|\.|\-|\–| ) ?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b ?)))?)|((\d{2}(\d{2})? ?(\-{1,3}|\/| |\–{1,3}|to|till|to till)+ ?((date|now|the date|present|present date|the present date|to till date|till date|t til date|today|current)|(\d{2}(\d{2})?))))|((Since|From|Working from|Currently working)(\d{2}(\d{2})?))|((for|from|for a duration of|since|till|to till)\d{1,2} (months))|(\d{1,2}( ?\.\d{1,2} ?)? (months|month|year|years) (work|as|experience)))\)?( |\(|\)|\,|\.|\:|\-|\:\-|\-\:|\;|$)"
		self.dateRegex = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b(\s|\-{1,3}|\–{1,3}|\.|,|’|'|‘)*(\d{1,2}(th|rd|st|nd)?( )?( |\/|\\|\.|\-|\–|\,)( )?)?\d{2}(\d{2})?)|\b(\d{1,2}(\s|\/|\\|\.|\-|\–)\d{2}(\d{2})?)( |\)|\.)"
		self.dateRegex2 = r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)( )\b\d{1,2}( )?(\s|\-{1,3}|\–{1,3}|\.|\,|’|'|‘)*( )?\d{2}(\d{2})?)\b"
		self.dateRegex3 = r"\b(\d{2}(\d{2})?)( )?(\/|\\|\.|\-|\–)( )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b"
		self.designationRegex = r"(Job Title|Designation|Position|Role|Working\s*as\s*a|Working\s*as\s*an|Worked\s*as\s*an|Worked\s*as\s*a|Promoted\s*to\s*a|Promoted\s*to\s*an|Promoted\s*to|Worked\s*as|Working\s*as|Work\s*as|Work\s*as\s*a|Work\s*as\s*an)\s*\d{0,2}\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.designationRegex2 =r"\s*(as|as\s*a|as\s*an|Profile|Profile\s*\&\s*Product)\s*( |\:|\.|\-|\-\s*\:|\:\s*\-|\>|\-\s*\>)?\s*"
		self.bodyDesignationRegex = r"^(?!.*(Reporting to|Reporting|Nominated for|Build up Relationship with|leading|Accuracy of|Submitting|Publishing the errors for|Profitable Champ|Key Responsibilities as an|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|Leading a team of|Meeting with|Engage in managing the wealth portfolio|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|renowned|best|team of)).*(Promoted as )?(and)?\b"	
		self.articles = ['a', 'an', 'of', 'the', 'is', 'in', 'and']
		self.stopWords = {'needn', 'aren', 'most', 'been', 'o', 've', 'who', 'so', 'my', 'this', 'before', 'just', 'under', 'few', 'didn', 're', 'how', 'ours', 'as', 'her', 'ourselves', 'will', 'm', 'your', 'himself', 'd', 'isn', 'they', 'why', 'against', 'down', 'did', 'were', 'if', 'between', 'below', 'are', 'until', 'wouldn', 'other', 'over', 'very', 'from', 'in', 'those', 'same', 'she', 'won', 'doesn', 'ain', 'weren', 'do', 'had', 'all', 'theirs', 'than', 'then', 'be', 'with', 'only', 'and', 'have', 'yourselves', 'don', 'y', 'their', 'during', 'once', 'above', 'couldn', 'ma', 'or', 'his', 'has', 'while', 'here', 'not', 's', 'when', 'these', 'into', 'by', 'themselves', 'hadn', 'a', 'about', 'hasn', 'the', 'shouldn', 'mightn', 'where', 'at', 'whom', 'mustn', 'yourself', 'because', 'through', 'of', 'he', 'some', 'for', 'doing', 'an', 't', 'again', 'out', 'what', 'shan', 'its', 'own', 'being', 'them', 'yours', 'herself', 'that', 'such', 'was', 'haven', 'can', 'hers', 'after', 'now', 'each', 'll', 'on', 'it', 'myself', 'does', 'should', 'further', 'up', 'there', 'no', 'but', 'itself', 'nor', 'off', 'our', 'i', 'wasn', 'you', 'we', 'both', 'which', 'to', 'him', 'is', 'me', 'am', 'any', 'having', 'more', 'too'}


	def writeToCompanyMaster(self, CompanyList):
		myfile = open(BASE+"/ListData2/companyMaster.txt", "a")
		for company in CompanyList:
			myfile.write("%s\n" % company)
		myfile.close()

	def writeToDesignationMaster(self, DesgList):
		myfile = open(BASE+"/ListData2/designationMaster.txt", "a")
		for desg in DesgList:
			myfile.write("%s\n" % desg)
		myfile.close()	
		
	def rreplace(self, s, old, new, occurrence):
		li = s.rsplit(old, occurrence)
		return new.join(li)
	
	def TitleCleaner(self, title):
		title = str(re.sub(r"(\\n|\\r|\\t)", '', title))
		return title	

	def threadOtherDesg(self, originalEmpBlock, areaToScan, TitlesRegex):
		try:
			##print ("LOADING....")
			self.OtherDesignations = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
			self.CatastrophicBacktracking = False
		except:
			#print ("E1")
			self.startRegexTimer = time.perf_counter()
			try:
				self.OtherDesignations = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
				self.CatastrophicBacktracking = False
			except:
				#print ("E2")
				self.startRegexTimer = time.perf_counter()
				try:
					self.OtherDesignations = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
					self.CatastrophicBacktracking = False
				except:
					#print("E3")
					self.OtherDesignations = ["CATASTROPHIC BACKTRACKING"]
					self.CatastrophicBacktracking = False

	def getCompanySubBlocks(self, textBeforeCompany, Titles, TitlesRegex, companyList, tempEmpBlock, originalEmpBlock):
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
			# #print (DateList,DesgList)
			if (DateList or DesgList):
				if(DateList and DesgList):
					isRubbish = -1
					##print (DateList,DesgList)
				elif(DateList):
					isRubbish = 0
				else:
					isRubbish = 2		
			else:
				isRubbish = 1
		# #print (textBeforeCompany)			
		# #print (isRubbish)
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
				# #print (company["Company"],repr(possibleSubBlock),DateList,DesgList)
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
								# #print (areaToScanList)
								if(not areaToScanList):
									DateList[j-1]["AreaToScanFlag"] = 1
									# #print (repr(DateList[j-1]["AreaToScan"]))
									DateList[j-1]["AreaToScan"] = (DateList[j-1]["AreaToScan"].rstrip() + " " + date["Date"].strip() + " " + areaToScan.lstrip())
									# #print (repr(areaToScan))
									# #print (repr(DateList[j]["Date"]))
									DateList.pop(j)
								else:
									DateList[j]["AreaToScanFlag"] = 1		
									DateList[j]["AreaToScan"] = areaToScan
									# #print (areaToScan)
					else:
						for (j,date) in enumerate(DateList):
							if(j!=0):
								areaToScan = possibleSubBlock[DateList[j-1]["EndingIndex"]:DateList[j]["StartIndex"]]
									# #print ("^^^^^\n\n\n",areaToScan,"\n\n\n^^^^^^^^")
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
							if(j==(len(DateList)-1)):
								areaToScan = areaToScan + possibleSubBlock[DateList[j]["StartIndex"]:]		
							DateList[j]["AreaToScanFlag"] = 1		
							DateList[j]["AreaToScan"] = areaToScan								
					companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
					curr += 1
				else:
					if(curr!=0):
						companySubBlocks[curr-1]["Text"] += (possibleSubBlock)
						previousDateList = companySubBlocks[curr-1]["DateList"]	
						previousDateListLength = len(previousDateList)
						previousDateList[previousDateListLength-1]["AreaToScan"] += (possibleSubBlock)
						##print (previousDateList[previousDateListLength-1]["AreaToScan"])
			return companySubBlocks						
		else:
			curr = 0
			if(isRubbish==-1):
				TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
				TitlesRegex = r"( )?( |\,|\"|\-|\-|\:|\.|^|\{|\(|\))( )?(" + TitlesRegex + r")\s*( )?( |\"|\”|\,|\-|\-|\:|\.|\)|\-|\(|\}|\(|\))( )?"
				##print (repr(textBeforeCompany))
				nextCompanyIsRubbish = 0
				for (i,company) in enumerate(companyList):
					if (i!=(len(companyList)-1)):
						possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:companyList[i+1]["StartIndex"]]
					else:
						possibleSubBlock = tempEmpBlock[companyList[i]["StartIndex"]:]
					possibleSubBlock = textBeforeCompany + possibleSubBlock
					DateRegexObj = re.compile(self.dateStringRegex, re.I|re.M)
					DesgRegexObj = re.compile(TitlesRegex, re.I|re.M)
					##print (possibleSubBlock)
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
					##print (DateList,DesgList,company['Company'],possibleSubBlock)
					if(DateList and DesgList):
						if(len(DateList)==1 or len(DesgList)==1):
							# #print ("HURRAY")
							if(nextCompanyIsRubbish==0):
								# #print (possibleSubBlock)
								textBeforeCompany = ''
								if(DateList[0]["StartIndex"]<DesgList[0]["StartIndex"]):
									areaToScan = possibleSubBlock[DateList[0]["EndingIndex"]:]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									DateList[0]["AreaToScanFlag"] = 1		
								else:
									areaToScan = possibleSubBlock[:DateList[0]["StartIndex"]]
									if(not areaToScan.startswith(' ')):
										areaToScan = ' ' + areaToScan
									if(not areaToScan.endswith(' ')):
										areaToScan = areaToScan + ' '
									areaToScan = areaToScan + possibleSubBlock[DateList[0]["StartIndex"]:]		
									DateList[0]["AreaToScanFlag"] = 1									
								DateList[0]["AreaToScan"] = areaToScan
								companySubBlocks.append({"Company": company["Company"], "Text":possibleSubBlock, "DateList": DateList, "DesignationList": DesgList})
								curr += 1
								nextCompanyIsRubbish = 1
							else:
								if((DateList[len(DateList)-1])["StartIndex"]<(DesgList[len(DesgList)-1])["StartIndex"]):
									textBeforeCompany = possibleSubBlock[(DateList[len(DateList)-1])["StartIndex"]:]				
								else:
									lastDesg = (DesgList[len(DesgList)-1])
									textBeforeCompany = possibleSubBlock[lastDesg["StartIndex"]:]
								# #print ("$$$$$$",textBeforeCompany,"$$$$$$")	
								possibleSubBlock = possibleSubBlock.replace(textBeforeCompany,'')
								companySubBlocks[curr-1]["Text"] += possibleSubBlock
								previousDateList = companySubBlocks[curr-1]["DateList"]	
								# #print (previousDateList)
								previousDateListLength = len(previousDateList)
								previousDateList[previousDateListLength-1]["AreaToScan"] += possibleSubBlock
								nextCompanyIsRubbish = 0	
								# #print ("*********",repr(possibleSubBlock),"*********")
						else:
							# #print ("WHY")
							if((DateList[len(DateList)-1])["StartIndex"]<(DesgList[len(DesgList)-1])["StartIndex"]):
								textBeforeCompany = possibleSubBlock[(DateList[len(DateList)-1])["StartIndex"]:]				
							else:
								lastDesg = (DesgList[len(DesgList)-1])
								textBeforeCompany = possibleSubBlock[lastDesg["StartIndex"]:]
							if(i!=(len(companyList)-1)):
								possibleSubBlock = self.rreplace(possibleSubBlock, textBeforeCompany, '', 1)	
							##print ("^^^^^^^^",repr(possibleSubBlock),"^^^^^^^")
							DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
							DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]	
							# #print (DateList,DesgList)
							if (DateList and DesgList):
								if(DateList[0]["StartIndex"]<DesgList[0]["StartIndex"]):
									for (j,date) in enumerate(DateList):
										if(j!=(len(DateList)-1)):
											areaToScan = possibleSubBlock[DateList[j]["EndingIndex"]:DateList[j+1]["StartIndex"]]
											if(not areaToScan.startswith(' ')):
												areaToScan = ' ' + areaToScan
											if(not areaToScan.endswith(' ')):
												areaToScan = areaToScan + ' '
											try:
												if(not lastDateFlag):	
													DateList[j]["AreaToScan"] = areaToScan	
												else:
													DateList[j]["AreaToScan"] += areaToScan
													lastDateFlag = 0
											except:	
												lastDateFlag = 0
												DateList[j]["AreaToScan"] = areaToScan		
											DateList[j]["AreaToScanFlag"] = 1
										else:
											areaToScan = possibleSubBlock[DateList[j]["EndingIndex"]:]
											if(not areaToScan.startswith(' ')):
												areaToScan = ' ' + areaToScan
											if(not areaToScan.endswith(' ')):
												areaToScan = areaToScan + ' '
											TitlesRegex	= '|'.join(Titles)
											testList = []
											otherDesg = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
											# #print (otherDesg)
											TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|\.|((\()|\-|(\/)))"
											desgObject = re.compile(TitlesRegex, re.I|re.M)	
											for desg in otherDesg:
												tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
												testList.extend(tempList)
											if(not testList):
												DateList[j-1]["AreaToScanFlag"] = 1
												DateList[j-1]["AreaToScan"] = DateList[j-1]["AreaToScan"].rstrip() + " " + date["Date"].strip() + " " + areaToScan.lstrip()
												DateList.pop(j)
											else:
												try:
													if(not lastDateFlag):	
														DateList[j]["AreaToScan"] = areaToScan	
													else:
														DateList[j]["AreaToScan"] += areaToScan
														lastDateFlag = 0
												except:	
													lastDateFlag = 0
													DateList[j]["AreaToScan"] = areaToScan	
												DateList[j]["AreaToScanFlag"] = 1		
								else:
									for (j,date) in enumerate(DateList):
										if(j!=0):
											areaToScan = possibleSubBlock[DateList[j-1]["EndingIndex"]:DateList[j]["StartIndex"]]
											if(j==(len(DateList)-1)):
												areaToScan = areaToScan + possibleSubBlock[DateList[j]["StartIndex"]:]
												# #print ("^^^^^\n\n\n",areaToScan,"\n\n\n^^^^^^^^")
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
										if(j==(len(DateList)-1)):
											areaToScan = areaToScan + possibleSubBlock[DateList[j]["StartIndex"]:]		
										DateList[j]["AreaToScanFlag"] = 1
										try:
											if(not lastDateFlag):	
												DateList[j]["AreaToScan"] = areaToScan	
											else:
												DateList[j]["AreaToScan"] += areaToScan
												lastDateFlag = 0
										except:
											lastDateFlag = 0
											DateList[j]["AreaToScan"] = areaToScan		
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
							# #print ("TTTTT\n\n",companySubBlocks[curr-1]["Text"],"TTTTT\n\n\n")
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
				return companySubBlocks				
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
					##print (possibleSubBlock)
					DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
					# #print (DateList,possibleSubBlock)
					if(not DateList and j!=0):
						companySubBlocks[curr-1]["Text"] += possibleSubBlock
						textBeforeCompany = ''
						TitlesRegex	= '|'.join(Titles)
						otherDesg = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
						TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|\.|((\()|\-|(\/)))"
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
						# #print (repr(possibleSubBlock))		
						DateList = [{"Date": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DateRegexObj, possibleSubBlock)]
						DesgList = [{"Designation": self.removeSpecialChars(m.group()), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(DesgRegexObj, possibleSubBlock)]
						##print (DateList,DesgList,company["Company"])
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
											DateList[i-1]["AreaToScan"] = (DateList[j-1]["AreaToScan"].rstrip() + " " + date["Date"].strip() + " " + areaToScan.lstrip())
											DateList.pop(i)
										else:
											testList = []
											TitlesRegex	= '|'.join(Titles)
											otherDesg = self.isGenuine(originalEmpBlock, areaToScan, "(" + TitlesRegex + ")")
											##print (originalEmpBlock,areaToScan)
											TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|((\()|\.|\-|(\/)))"
											desgObject = re.compile(TitlesRegex, re.I|re.M)
											for desg in otherDesg:
												tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
												testList.extend(tempList)
											##print (testList,otherDesg)	
											if(not testList):
												DateList[i-1]["AreaToScanFlag"] = 1
												DateList[i-1]["AreaToScan"] = (DateList[i-1]["AreaToScan"].rstrip() + " " + date["Date"].strip() + " " + areaToScan.lstrip())
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
									if(j==(len(DateList)-1)):
										areaToScan = areaToScan + possibleSubBlock[DateList[j]["StartIndex"]:]		
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

				return companySubBlocks			
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
					##print ("*********\n\n\n\n\n\n\n\n\n",possibleSubBlock,"\n\n\n\n\n\n\n\n\n\n\n*********")
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
											TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|((\()|\-|\.|(\/)))"
											desgObject = re.compile(TitlesRegex, re.I|re.M)	
											for desg in otherDesg:
												tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
												testList.extend(tempList)
											if(not testList):
												DateList[i-1]["AreaToScanFlag"] = 1
												DateList[i-1]["AreaToScan"] = (DateList[j-1]["AreaToScan"].rstrip() + " " + date["Date"].strip() + " " + areaToScan.lstrip())
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
									if(j==(len(DateList)-1)):
										areaToScan = areaToScan + possibleSubBlock[DateList[j]["StartIndex"]:]		
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
				return companySubBlocks				
								
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
		bodyDesignationRegex = r"^(?!.*(Reporting to|Backup of|Qualified for|Nominated for|Build up Relationship with|leading|Supporting|Received Appreciation from|for achieving|for the Month of|Helping the|Rated|Leading a team of|Meeting with|Engage in managing the wealth portfolio|Reporting|Submitting|Key Responsibilities as an|Responsible for investigation of|Publishing the errors for|Profitable Champ|Profitability Legends|Follow-up with|Qualified for|Awarded \& felicitated by|Highest number of|opened in|Awarded|Awarded by|Submitting|highest numbers of accounts|Business Development through|co\-ordinate with|implement Training to|Training \& Development of|Provide backend support to|Attaining a joint sales call|Awarded|a team of|Update|Conducted|Won (the|a|an)?(.*)?Award|Achieved|leading|from the|renowned|best|team of)).*(Promoted as )?(and)?\b" + specificRegex + r"((?!\S)|((\()|(\/)|\.|\,|\}|\{)|to|\-|since|till|$)" 
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
			if ('[' in word):
				wordList[index] = wordList[index].replace('[','\[')
			if (']' in word):
				wordList[index] = wordList[index].replace(']','\]')
			if ('{' in word):
				wordList[index] = wordList[index].replace('{','\{')
			if ('}' in word):
				wordList[index] = wordList[index].replace('}','\}')
			if ('.' in word):
				wordList[index] = wordList[index].replace('.','\.')	
			if ('+' in word):
				wordList[index] = wordList[index].replace('+','\+')
		#print (wordList)			
		orgRegex = ""
		if(len(wordList)<8):
			start = int(len(wordList)/2)
			end  = int(len(wordList) - start)		
		else:
			start = 4
			end = 4
		count = 0	
		while(count<start):
			if(count!=(start-1)):
				orgRegex += (wordList[int(count)] + r"\s*?(\)|\.|\,|\:\-|\: \-|\-|\&|\:|\;| |\(|\*?)*?\s*?")
			else:
				orgRegex += wordList[int(count)]	 
			count += 1
		orgRegex += r"[\d\D]*?"
		count = end
		while(count>0):
			if(count!=1):
				orgRegex += (wordList[int(len(wordList)-count)] + r"\s*?(\)|\.|\,|\:\-|\: \-|\-|\&|\:|\;| |\(|\*?)*?\s*?")
			else:
				orgRegex += wordList[int(len(wordList)-count)]
			count -= 1
		orgRegex = orgRegex.strip()
		##print (tempSubBlock)
		# #print (self.ResumeText2)
		# #print (tempSubBlock)
		#print (orgRegex)
		findOriginalObj = re.compile(orgRegex, re.I|re.M)
		#print (txt)
		tempSubBlockL = [(m.group()) for m in re.finditer(findOriginalObj,txt)]
		tempSubBlock = ""
		for whatever in tempSubBlockL:
			tempSubBlock += whatever
		##print (tempSubBlock)	
		otherDesg = [(m.group().strip().lower().title()) for m in re.finditer(desgObject2,tempSubBlock)]
		##print (otherDesg)
		return otherDesg

	def CompanyBaseSections(self,headRegex,isFoundFlag, isEmploymentBlock):
		testDocument = self.ResumeText2
		##print (self.ResumeText2)
		##print (testDocument)
		regex = re.compile(r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*( |\:|\:\-|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)*( )*(\\r|\\n|\\t)",re.M)
		##print (r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( |\s)*(\\r|\\n|\\t)")
		if(isEmploymentBlock==1):
			regex = re.compile(r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*(\(In reverse chronological order\))?( |\:|\:\-|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)*( )*(\(?(Total)? *(Professional)? *(Experience)? *(in year|in month|in week|in day)? *(s)? *(\-|\–|\=|\:|\-\:|\-\:|\-\>|\>)* *\d{1,4}\.*\d{1,4}? *(Year|Month|Week|Day)s?\)?)?( )*(\\r|\\n|\\t)",re.M)
			#print(r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*(\(In reverse chronological order\))?( |\:|\:\-|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\(?(Total)? *(Professional)? *(Experience)? *(in year|in month|in week|in day)? *(s)? *(\-|\–|\=|\:|\-\:|\-\:|\-\>|\>)* *\d{1,4}\.*\d{1,4}? *(Year|Month|Week|Day)s?\)?)?( )*(\\r|\\n|\\t)")
			#print(repr(testDocument))
			##print ("(\\r|\\n|\\t)( )*("+headRegex+")( )*(\(In reverse chronological order\))?( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\(?(Total)? *(Professional)? *(Experience)? *(in year|in month|in week|in day)? *(s)? *(\-|\–|\=|\:|\-\:|\-\:|\-\>|\>)* *\d{1,4}\.*\d{1,4}? *(Year|Month|Week|Day)s?\)?)? *(\\r|\\n|\\t)")
			##print (r"(\\r|\\n|\\t)( )*(" + headRegex+r")( )*(\(In reverse chronological order\))?( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\(?(Total)? *(Professional)? *(Experience)? *(in year|in month|in week|in day)? *(s)? *(\-|\–|\=|\:|\-\:|\-\:|\-\>|\>)* *\d{1,4}\.*\d{1,4}? *(Year|Month|Week|Day)s?\)?)? *(\\r|\\n|\\t)")
		headRegex2List = []
		headRegex3List = []
		headRegexList = headRegex.split('|')
		for header in headRegexList:
			headRegex2List.append(header.upper())
			headRegex3List.append(self.title_except(header, (self.articles)))
		headRegex2List = list(set(headRegex2List))
		headRegex2 = '|'.join(headRegex2List)
		headRegex3List = list(set(headRegex3List))
		headRegex3 = '|'.join(headRegex3List)	
		regex2 = re.compile(r"("+headRegex2+r")( )*( |\:|\-|\-( )*\:|\:( )*\-|\>|\-\>)?( )*",re.M)
		regex3 = re.compile(r"("+headRegex3+r")( )*( |\:|\-|\-( )*\:|\:( )*\-|\>|\-\>)?( )*",re.M)
		#if (headRegex == 'PERSONAL DETAILS|Personal Interests|MISCELLANEOUS|INTERESTS|Miscellaneous|PERSONAL INTERESTS|STRENGTHS|Family Background|Hobbies|Interests|Personal Information|STRENGTH|DATE OF BIRTH|Personal Profile|Personal details|Personal detail|Personal information|PERSONAL QUALITIES|Strengths|Personal Qualities|Date of Birth|Personal interests|Personal Details|PERSONAL STRENGTH|PERSONAL DATA|Date of birth|HOBBIES|FAMILY BACKGROUND|Personal data|Family background|PERSONAL PROFILE|PERSONAL INFORMATION|Personal profile|PERSONAL DETAIL|Address|Personal strength|Personal Strengths|Personal Strength|Personal Data|Strength|Personal Detail|ADDRESS|PERSONAL STRENGTHS|Personal qualities|Personal strengths'):
		# #print (headRegex)
		##print (r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\(?(Total)? *(Professional)? *(Experience)? *(in year|in month|in week|in day)? *(s)? *(\-|\–|\=|\:|\-\:|\-\:|\-\>|\>)* *\d{1,4}\.*\d{1,4}? *(Year|Month|Week|Day)s?\)?)? *(\\r|\\n|\\t)","\n\n\n\n^^^^^^^^^\n\n\n\n",testDocument)
		##print (testDocument)
		dmatch=re.findall(regex,testDocument)
		##print (dmatch)
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
				restext = self.ResumeText2[tupleelem[0]:(tupleelem[1]+1)]
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
					##print (position[0][0],2,position[0][2])
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
		for employmentHeader in self.headersroot.findall(headerString):
			employmentHeaderText = employmentHeader.text
		RegEmploymentHeads = employmentHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").replace("&amp;","&").replace("/","\/").strip()
		RegEmploymentHeads = self.RemoveLowerCase(RegEmploymentHeads)
		#if(headerString=='employmentHeader'):
		#	#print (RegEmploymentHeads)
		return RegEmploymentHeads	

	def removeSpecialChars(self, string):
		RegexObj = re.compile(r"\b.*\b",re.I|re.M)
		# #print (string)
		RegexList = [(m.group()) for m in re.finditer(RegexObj,string.strip())]
		return RegexList[0]

	def tryAgainForEmpBlock(self, allBlocksList):
		result = self.CompanyBaseSections(self.getHeader('employmentHeader'),0,1)
		if (not result):
			return None
		startingIndex = result[0]
		Block = {}
		employmentBloc = ""
		employmentBlock = ""
		employmentBlockIndex = 0
		originalEmpBlock = ""
		tempEmpBlock = ""
		NERCompanyList = []
		for (i,Block) in enumerate(allBlocksList):
			if(Block['StartingIndex']!=0):
				if(Block['BlockName']=='Employment'):
					Block['StartingIndex'] = startingIndex
					Block['BlockText'] = ""
		##print (allBlocksList)
		allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
		##print (allBlocksList)
		for (i,Block) in enumerate(allBlocksList):
			if(Block['StartingIndex']!=0 and Block['BlockName']=='Employment'):
				if(i!=(len(allBlocksList)-1)):
					Block['EndingIndex'] = allBlocksList[i+1]['StartingIndex']
					Block['BlockText'] = self.ResumeText2[Block['StartingIndex']:Block['EndingIndex']]
				else:
					Block['EndingIndex'] = len(self.ResumeText2) - 1
					Block['BlockText'] = self.ResumeText2[Block['StartingIndex']:]
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
		return [employmentBloc,employmentBlock,employmentBlockIndex,originalEmpBlock,tempEmpBlock,NERCompanyList]		

	def getCompanyList (self, companyList, NERCompanyList, Companies, tempEmpBlock):
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
		##print (companyList)	
		companyStEndTuple = [(company["StartIndex"],company["EndingIndex"]) for company in companyList]
		companyStEndTuple.sort(key=lambda x: x[0])
		##print (companyStEndTuple)
		nerCompany = []
		for nerComp in NERCompanyList:
			start = 0
			nerCompName = nerComp[1]
			nerCompStart = int(nerComp[2]) #381
			nerCompEnd = nerCompStart + int(nerComp[3]) - 1 #415
			CompMasterList = [item for item in companyStEndTuple if item[0] == nerCompStart]
			##print (nerCompName)
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
		Companies.extend(nerCompany)
		Companies = sorted(list(set(Companies)), key=len, reverse=True)	
		companyList.sort(key=lambda x: x["StartIndex"])
		return [Companies, companyList, nerCompany, companyStEndTuple]	

	def designationTenureParser(self):
		##print (type(self.ResumeText2))
		allBlocksList = []
		result = self.CompanyBaseSections(self.getHeader('educationHeader'),1,0)
		allBlocksList.append({'BlockName':"Education",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('accomplishmentsHeader'),1,0)
		allBlocksList.append({'BlockName':"Accomplishments",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('awardsHeader'),1,0)
		allBlocksList.append({'BlockName':"Awards",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('employmentHeader'),1,1)
		##print (result)
		allBlocksList.append({'BlockName':"Employment",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('extracurricularHeader'),1,0)
		allBlocksList.append({'BlockName':"ExtraCurricular Activities",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('miscHeader'),1,0)
		# #print (result)
		allBlocksList.append({'BlockName':"Miscellaneous",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('summaryHeader'),1,0)
		allBlocksList.append({'BlockName':"Summary",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		result = self.CompanyBaseSections(self.getHeader('skillsHeader'),1,0)
		allBlocksList.append({'BlockName':"Skills",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})		
		result = self.CompanyBaseSections(self.getHeader('credibilityHeader'),1,0)
		allBlocksList.append({'BlockName':"Credibility",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
		allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
		for (i,Block) in enumerate(allBlocksList):
			if(Block['StartingIndex'] == 0):
				Block['EndingIndex']=(len(self.ResumeText2)-1)
				Block['BlockText']=self.ResumeText2
			else:
				if(i!=8):
					nextBlock = allBlocksList[i+1]
					Block['EndingIndex']=nextBlock['StartingIndex']
				else:
					Block['EndingIndex']=len(self.ResumeText2)-1
				Block['BlockText']=self.ResumeText2[int(Block['StartingIndex']):int(Block['EndingIndex'])]
		for (i,Block) in enumerate(allBlocksList):
			if(Block['StartingIndex']!=0):
				if(Block['BlockName']=='Employment'):
		 			employmentBlock = Block['BlockText']
		 			employmentBloc = Block
		 			employmentBlockIndex = i
		##print (employmentBlock) 			
		if ('employmentBlock' not in locals()):
			employmentBlockRegexObj = re.compile(r"(\\r|\\n)\s*(\u2022|\u2023|\u25E6|\u2043|\u2219)?("+self.getHeader('employmentHeader')+r")\s*(\d{1,2})( |\:|\-|\-(\s)?\:|\:(\s)?\-|>|\-\s*\>|\d{1,2})?( )?\s*(\\r|\\n)",re.M)
			employmentBlockL = [(m.group(),m.start(),m.end()) for m in re.finditer(employmentBlockRegexObj,self.ResumeText2)]
			try:
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
								Block['BlockText']=self.ResumeText2[int(Block['StartingIndex']):int(ans)]
								Block['EndingIndex']=ans
							else:
								Block['BlockText']=self.ResumeText2[int(Block['StartingIndex']):]
								Block['EndingIndex']=len(self.ResumeText2)-1	
							Block['BlockText']=self.ResumeText2[int(Block['StartingIndex']):int(Block['EndingIndex'])]
							employmentBlock = Block['BlockText']
							employmentBloc = Block
							employmentBlockIndex = j
			except:
				employmentBlock = self.ResumeText2
				employmentBloc = {'BlockName':"Employment",'StartingIndex':0,'EndingIndex':(len(self.ResumeText2)-1),'BlockText':employmentBlock,'BlockTitle':''}				
			allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
		Titles = []
		##print (employmentBlock)
		with open(BASE+'/ListData2/designationMaster.txt') as file:
			for line in file: 
				line = line.strip()
				Titles.append(line)
		Titles = list(set(Titles))
		Titles = sorted(Titles, key=len, reverse=True)
		for (i,title) in enumerate(Titles):
			titleWords = title.split()
			Titles[i] = ' '.join(titleWords)
		Companies = [] 
		with open(BASE+'/ListData2/companyMaster.txt') as file:
			for line in file: 
				line = line.strip()
				Companies.append(line)
		##print (Companies)		
		justTrying = employmentBlock.replace('\\n','\n').replace('\\t','\t').replace('\\r','\r')
		originalEmpBlock = justTrying
		##print (originalEmpBlock)
		employmentBlock = re.split(r'\\n|\\r|\\t|\s|\\x\w{1,2}',employmentBlock)
		employmentBlock = list(filter(None, employmentBlock))
		##print (employmentBlock)
		tempEmpBlock = ' '.join(employmentBlock)
		try:
			NERCompanyList = OrgNER(tempEmpBlock)
		except:
			NERCompanyList = []
			pass

		# #print (NERCompanyList)
		Companies = sorted(list(set(Companies)), key=len, reverse=True)	
		CompanyRegex = r"(\,|M\/S)?( |\-|\.|\–|\(|\\t|\\n|\\r)(" + '|'.join(Companies) + r")( |\-|\.|\,|\;|\(|\)|\.\:|\\t|\\n|\\r)"
		TitlesRegex = '|'.join(sorted(list(set(Titles)),key=len,reverse=True))
		TitlesRegex = r"( )?( |\,|\;|\-|\"|^|\{|\-|\:|\.|\(|\\n|\\t|\\r)( )?(" + TitlesRegex + r")(\,|\/|\;|\}|\-| |\\n|\\r|\\t)?\b"
		compRegexObj = re.compile(CompanyRegex, re.I|re.M)
		companyList = [{"Company": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(compRegexObj, tempEmpBlock)]
		# #print (companyList)
		##print (tempEmpBlock)
		companyList.sort(key=lambda x: x["StartIndex"])
		if (not NERCompanyList and not companyList):
			resultList = self.tryAgainForEmpBlock(allBlocksList)
			try:
				employmentBloc = resultList[0]
				employmentBlock = resultList[1]
				employmentBlockIndex = resultList[2]
				originalEmpBlock = resultList[3]
				tempEmpBlock = resultList[4]
				NERCompanyList = resultList[5]
				companyList = [{"Company": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(compRegexObj, tempEmpBlock)]
				companyList.sort(key=lambda x: x["StartIndex"])
			except:
				return ['Formatting Error/No employment Block/Very small company:NER can\'t detect']							
		resultList = self.getCompanyList(companyList, NERCompanyList, Companies, tempEmpBlock)
		Companies = resultList[0]
		companyList = resultList[1]
		nerCompany = resultList[2]
		companyStEndTuple = resultList[3]
		firstCompany = companyList[0]["Company"]
		firstCompanyStart = companyList[0]["StartIndex"]
		TitleLength = len(employmentBloc["BlockTitle"].strip())
		textBeforeCompany = tempEmpBlock[TitleLength:firstCompanyStart]
		##print (firstCompany)
		finalList= []
		##print (companyList)
		##print (tempEmpBlock)
		try:
			companySubBlocks = self.getCompanySubBlocks(textBeforeCompany, Titles, TitlesRegex, companyList, tempEmpBlock, originalEmpBlock)
			# #print (companySubBlocks)
		except Exception as e:
			# #print (e)
			return ['Update company and designation master/Inconsistent Format']	
		# #print (companySubBlocks)
		if (not companySubBlocks):
			resultList = self.tryAgainForEmpBlock(allBlocksList)
			try:
				employmentBloc = resultList[0]
				employmentBlock = resultList[1]
				employmentBlockIndex = resultList[2]
				originalEmpBlock = resultList[3]
				tempEmpBlock = resultList[4]
				NERCompanyList = resultList[5]
				companyList = [{"Company": m.group(), "StartIndex": m.start(), "EndingIndex": m.end()} for m in re.finditer(compRegexObj, tempEmpBlock)]
				companyList.sort(key=lambda x: x["StartIndex"])						
				resultList = self.getCompanyList(companyList, NERCompanyList, Companies, tempEmpBlock)
				Companies = resultList[0]
				companyList = resultList[1]
				# #print (companyList)
				nerCompany = resultList[2]
				companyStEndTuple = resultList[3]
				firstCompany = companyList[0]["Company"]
				firstCompanyStart = companyList[0]["StartIndex"]
				TitleLength = len(employmentBloc["BlockTitle"].strip())
				textBeforeCompany = tempEmpBlock[TitleLength:firstCompanyStart]
				finalList= []
				companySubBlocks = self.getCompanySubBlocks(textBeforeCompany, Titles, TitlesRegex, companyList, tempEmpBlock, originalEmpBlock)
			except Exception as e:
				##print (e)
				return ['Formatting Error/No employment Block/Very small company:NER can\'t detect']	
		# #print (companyList)
		# #print (companySubBlocks)	
		flg = 0
		currentDateFlag = 0
		##print (companySubBlocks)
		for (j,companySubBlock) in enumerate(companySubBlocks):
			companyObj = re.compile(r"\b.*\b",re.I|re.M)
			company = [(m.group()) for m in re.finditer(companyObj,companySubBlock["Company"].strip().lower().title())]
			finalListElem = {"Organization" : company[0]}
			finalListElem["WorkExperience"] = []
			finalListElem["CompanyBlock"] = companySubBlock['Text']
			dateList = companySubBlock["DateList"]
			dateListLength = len(dateList)
			totalMonthsOfExperience = 0
			flag = 1
			StIndex = dateList[0]["StartIndex"]
			for (i,dateString) in enumerate(dateList):
				# #print (dateString["Date"])
				onlyYearFlag = 0
				onlyMonthFlag = 0
				dateObject = re.compile(self.dateRegex, re.I|re.M)
				fromToDates = [(self.removeSpecialChars(m.group().strip()),m.group(4)) for m in re.finditer(dateObject,dateString["Date"])]
				# #print (dateString["Date"])
				if (not (self.isGenuine(originalEmpBlock, dateString["Date"], "(" +self.dateRegex + ")")) and fromToDates):
					# #print ("$$$$$$$",fromToDates,"$$$$$$$")
					continue
				##print (fromToDates)
				if (not fromToDates):
					dateObject = re.compile(self.dateRegex2, re.I|re.M)
					fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]
					if (not (self.isGenuine(originalEmpBlock, dateString["Date"], "(" +self.dateRegex2 + ")")) and fromToDates):
						continue
					start = 0
					if (not fromToDates):
						dateObject = re.compile(self.dateRegex3, re.I|re.M)
						fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]		
						if (not (self.isGenuine(originalEmpBlock, dateString["Date"], "(" +self.dateRegex3 + ")")) and fromToDates):
							continue
						if (not fromToDates):
							dateObject = re.compile(r"\d{2}(\d{2})?", re.I|re.M)
							fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]		
							if (not (self.isGenuine(originalEmpBlock, dateString["Date"], r"(\d{2}(\d{2})?)")) and fromToDates):
								continue
							if(not fromToDates):
								# #print ("OHYEAH")
								dateObject = re.compile(r"\d{1,2} ?(\.?\d{1,2})? ?( |\-)(month|year|week|day)(s)?( |\b)",re.I|re.M)				
								fromToDates = [(self.removeSpecialChars(m.group().strip())) for m in re.finditer(dateObject,dateString["Date"])]	
								##print (fromToDates)
								if (not (self.isGenuine(originalEmpBlock, dateString["Date"], r"(\d{1,2}( |\-)(month|year|week|day)(s)?( |\b))")) and fromToDates):
									continue
								fromDate = toDate = fromDateMonth = toDateMonth = fromMonthNum = toMonthNum = fromYear = toYear = "unspecified"
								onlyMonthFlag = 1
								for (ftdindex,b) in enumerate(fromToDates):
									valueObj = re.compile(r"\d{1,2}",re.I|re.M)
									valueList = [int(m.group()) for m in re.finditer(valueObj,b)]
									value = valueList[0]
									if(len(valueList)==2):
										value = float(str(value) + "." + str(valueList[1]))
									if('year' in b):
										fromToDates[0] = int(round(value*12))
									elif('month' in b):
										fromToDates[0] = int(round(value))
									elif('week' in b):
										fromToDates[0] = int(round(value/4))
									elif('day' in b):
										fromToDates[0] = int(round(value/30))		
									# #print (value,companySubBlock["Company"])			
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
					##print ("EHALO",fromToDates,datePartList)
					if (len(fromToDates) == 1):
						if(not datePartList):
							fromDate = self.FormatDate(fromToDates[0])
						else:
						 	fromDate = self.FormatDate(fromToDates[0].replace(datePartList[0],""))	
						if(j==0):
							toDate = self.FormatDate("present")
						else:
							if(j!=(len(companySubBlocks)-1) or (flg==0)):
								##print (tempDate)
								toDate = self.FormatDate(tempDate)
								toDateMonth = toDate[:3]
								##print (fromDate,toDate,toDateMonth)
								dic = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
								if(toDate[:2].isalpha()):
									toMonthNum = (dic.get(toDateMonth) - 1)
								else:
									if(toDate[1].isdigit()):
										# #print (toDate)
										toMonthNum = int(toDate[:2]) - 1
									else:
										toMonthNum = int(toDate[:1]) - 1	
								dic2 = {"1" : "Jan", "2" : "Feb", "3" : "Mar", "4" : "Apr", "5" : "May", "6" : "Jun", "7":"Jul", "8" : "Aug", "9":"Sep", "10": "Oct", "11":"Nov", "12":"Dec"}
								# #print (toMonthNum)
								toDateMonth = dic2.get(str(toMonthNum),toDateMonth)
								# #print (toDateMonth)
								toYear = toDate[-4:]		
								toDate = toDateMonth + "-" + toYear
								someflg = 1
								fromDate = (self.removeSpecialChars(fromDate).strip())
								fromDateMonth = fromDate[:3]
								if(not fromDateMonth.isalpha()):
									if(fromDateMonth[1].isdigit()):
										try:		
											fromMonthNum = int(fromDateMonth[:2])
										except:
											pass	
									else:
										try:
											fromMonthNum = int(fromDateMonth[:1])
										except:
											pass		
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
									##print (fromDate,toDate,fromDateMonth,toDateMonth,fromYear,toYear)
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
						##print (repr(fromDate),repr(toDate))
					fromDateMonth = self.removeSpecialChars(fromDate[:3]).strip()
					toDateMonth = self.removeSpecialChars(toDate[:3]).strip()
					##print (repr(fromDateMonth),repr(toDateMonth))

				# #print ("####",fromDate,toDate,"####")	
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
						# #print (toMonthNum)
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
						totalMonthsOfExperience = int(toMonthNum) - int(fromMonthNum)
					else:
						totalMonthsOfExperience = ((12-int(fromMonthNum)) + int(toMonthNum) + ((int(toYear) - (int(fromYear) + 1))*12))
					# #print (totalMonthsOfExperience,fromDate,toDate,fromMonthNum,toMonthNum,fromYear,toYear)	
				##print (fromDate,toDate,fromDateMonth,toDateMonth,fromMonthNum,toMonthNum)		
				TitlesRegex	= '|'.join(Titles)
				TitlesRegex = r"( )?( |\,|\"|\-|\-|\:|\.|^|\{|\(|\))( )?(" + TitlesRegex + r")( )?( |\"|\,|\-|\-|\:|\.|\}|\(|\))( )?"
				##print (TitlesRegex)
				desgObject = re.compile(TitlesRegex, re.I|re.M)
				testList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,dateString["AreaToScan"])]
				if(dateString["AreaToScanFlag"] == 0):
					DesgList = testList
				else:
					DesgList = []
					TitlesRegex	= '|'.join(Titles)
					# #print ("\n\n\n\n#######",repr(dateString["AreaToScan"]),"\n\n\n\n#######")
					self.startRegexTimer = time.perf_counter()
					self.CatastrophicBacktracking = True
					# print ("I got till here")
					self.OtherDesignations = ['CatastrophicBacktrackingError']
					try:
						_thread.start_new_thread(self.threadOtherDesg,(originalEmpBlock,dateString["AreaToScan"],TitlesRegex))
					except (KeyboardInterrupt, SystemExit):
						return 	['CatastrophicBacktrackingError']
				##print ()	
					while(((time.perf_counter() - self.startRegexTimer)<10) and self.CatastrophicBacktracking):
						##print ((time.perf_counter() - self.startRegexTimer),self.CatastrophicBacktracking)
						pass
					otherDesg = self.OtherDesignations
					if(self.CatastrophicBacktracking):
						return otherDesg
					##print (otherDesg)
					TitlesRegex = r"\b(" + TitlesRegex + r")(\(|\))?((?!\S)|((\()|\.|\-|(\/)))"
					desgObject = re.compile(TitlesRegex, re.I|re.M)	
					for desg in otherDesg:
						tempList = [(m.group().strip().lower().title()) for m in re.finditer(desgObject,desg)]
						##print (desg)
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
	
	def BaseSections(self,headRegex):
		"""" 
		to find the exact block 

		"""
		testDocument = self.ResumeText
		# return self.ResumeText2
		# regex = re.compile("(\\n|\\r|\\t)\s*([a-z]+\s?[a-z]+\s?)(\\n|\\r|\\t|)",re.I|re.M)
		regex = re.compile("(\\n|\\r|\\t)\s*("+re.escape(headRegex).replace('\\|','|')+")(\\n|\\r|\\t|)",re.I|re.M)
		# regex = re.compile(headRegex,re.I|re.M)
		# #print regex
		# dmatch=re.findall(regex,testDocument)
		# #print dmatch
		position = [(m.start(2), m.end(2)) for m in re.finditer(regex, testDocument)]
		# return testDocument
		if(len(position)>0):
			# #print position
			if(len(position)==1):
				# #print testDocument[position[0][0]:]
				return testDocument[position[0][0]:]
			# #print testDocument[position[0][0]:position[-1][0]+250]
			return testDocument[position[0][0]:position[-1][0]+300]
		else:
			return testDocument[0:]

	def CompanyBaseSections2(self,headRegex):
		testDocument = self.ResumeText
		# #print re.escape(headRegex)
		regex = re.compile(headRegex,re.I|re.M)
		# #print regex
		dmatch=re.findall(regex,testDocument)
		# #print dmatch
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
		##print RegEducationHeads
		# get specific lists
		degreesElement = self.degreesroot.findall('d')
		instituteElement = self.institutionroot.findall('i')		
		# get document section from headers
		strDocumemtText = self.BaseSections(RegEducationHeads)
		##print strDocumemtText
		degreeList = []
		institutionList = []
		passingYearList = []
		instindexP = 0
		instindexN = 0
		isHighestDegree = 0
		HighestDegree = ""
		for degrees in degreesElement:
			isDegreefound = False
			for variant in degrees.findall('v'):
				if(isDegreefound):
					break
				regex = re.compile("(?<!\S)[\(]?(" + re.escape(variant.text.replace("&amp;", "&")) + ")[\)]?(?!\S)", re.I|re.M)
				m = regex.search(strDocumemtText)
				if(m):
					isDegreefound = True
					degreeList.append(degrees.attrib["key"])
					if(isHighestDegree < int(degrees.attrib["level"])):
						HighestDegree = degrees.attrib["key"]
						isHighestDegree = int(degrees.attrib["level"]) 				
					instindexP = 0 if m.span()[0]-50 < 0 else m.span()[0]-50 
					instindexN = len(strDocumemtText) if m.span()[0]+50 > len(strDocumemtText) else m.span()[0]+50
					probebalyear = strDocumemtText[instindexP:instindexN]
					# #print probebalyear
					# #print variant.text.replace("&amp;", "&")
					probebalyear2 =  [line for line in strDocumemtText.split('\n') if variant.text.replace("&amp;", "&").lower() in line.lower()]
					# #print probebalyear2
					if(len(probebalyear2)>0):
						probebalyear = probebalyear2[0].strip()
						if(len(probebalyear)<len(variant.text.replace("&amp;", "&"))+10):
							probebalyear = strDocumemtText[m.span()[0]:instindexN]
					# #print probebalyear.encode("utf-8")
					regex = re.compile("([\d]{4})\s*\-*[to|till|upto]*\s*([\d]{4}|\-[\d]{2})*", re.IGNORECASE)
					passingYearList.append(re.findall(regex,probebalyear))
					isInsitutefound = False
					inStituteFoundName = "None"
					# #print strDocumemtText.encode("ascii")
					# sss =  Extract_Org(strDocumemtText)
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
		tempData = []
		# #print HighestDegree
		from .CommonClassObject import QualificationsDetails
		self.QualificationsDetailsObj = QualificationsDetails()
		self.QualificationsDetailsObj.HighestQualificationDegree = HighestDegree
		# #print passingYearList
		# #print degreeList
		# #print institutionList
		# #print degreeList
		
		# if(len(degreeList)==0):
		# 	data.append("None")
		# 	data.append("None")
		# 	data.append("None")
		# 	data.append("None")
		# 	tempData=["None","None","None"]
		# 	# #print "non"
		# 	self.QualificationsDetailsObj.AddQualificationData(tempData[0],tempData[1],tempData[2],tempData[1])
		
		for d in range(len(degreeList)):
			tempData = []
			# #print tempData,"1"
			if(degreeList[d]!=""):
				data.append(degreeList[d])
				tempData.append(degreeList[d])
			else:
				data.append("None")
				tempData.append("None")
			if(d<len(institutionList)):
				if(institutionList[d]):
					data.append(institutionList[d])
					tempData.append(institutionList[d])
				else:
					data.append("None")
					tempData.append("None")
			else:
				data.append("None")
				tempData.append("None")
			if(d<len(passingYearList)):
				if(passingYearList[d] and passingYearList[d][0][0]!=""):
					data.append(passingYearList[d][0][0])
					tempData.append(passingYearList[d][0][0])
				else:
					data.append("None")	
				if(passingYearList[d] and passingYearList[d][0][1]!=""):
					data.append(passingYearList[d][0][1])
					if(passingYearList[d][0][1].strip()!=""):
						tempData[-1]=passingYearList[d][0][1]
				else:
					data.append("None")
					tempData.append("None")	
			else:
				data.append("None")	
				data.append("None")
				tempData.append("None")
			# #print tempData,"2"
			if(len(tempData)>0):
				self.QualificationsDetailsObj.AddQualificationData(tempData[0],tempData[1],tempData[2],tempData[1])
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
		desgElement = self.designationroot.findall('d')
		# #print OrgLists
		# #print docSection.encode("utf-8")
		for xy in range(len(OrgLists)):
			Org = OrgLists[xy]
			tempData = []
			instindexP = Org[1]
			instindexN = OrgLists[xy+1][1] if xy< len(OrgLists)-1 else -1
			probebalExp = str(docSection[instindexP:instindexN].encode("utf-8").lower())
		
			# #print re.escape(Org[0][:6])
			regex = re.compile(re.escape(str(Org[0])+self.DurationRegex), re.I|re.M)		
			res = re.findall(regex,probebalExp)		
			if(len(res)>0):
				# #print res[0][1]
				try:
					# #print Org[0], res[0][1]
					# #print res
					OrgCompleteList.append(Org[0])
					tempData.append(Org[0])
					if res[0][1].strip() !="":
						if(len(res[0][1].split("."))>1):
							OrgCompleteList.append("None")
							tempData.append("None")
						else:
							OrgCompleteList.append(res[0][1].strip())
							tempData.append(res[0][1].strip())
					else:
						OrgCompleteList.append("None")
						tempData.append("None")
					
					if res[0][5].strip() !="":
						if(len(res[0][5].split("."))>1):
							OrgCompleteList.append("None")
							tempData.append("None")
						else:
							OrgCompleteList.append(res[0][5].strip())
							tempData.append(res[0][5].strip())
					else:
						OrgCompleteList.append("None")
						tempData.append("None")
					
					isDesgfound = False
					mydesignation = ""					
					for desg in desgElement:
						if(isDesgfound):
							break
						mydesignation = "None"
						for variant in desg.findall('v'):
								# #print variant.text
								regex = re.compile("[\s\n\r\t\)\(\.,\-]" + re.escape(variant.text.replace("&amp;", "&")) + "[\s\n\r\t\)\(\.,\-]", re.IGNORECASE)
								desgres = re.findall(regex,probebalExp)
								if(len(desgres)>0):
									# #print desgres
									mydesignation = desgres[0].strip()
									# #print mydesignation
									# DesgList.append(desgres)
									isDesgfound=True
				except(UnicodeEncodeError):
					pass
			if(len(tempData)>0):
				self.EmployementsHistoryDetailsObj.AddEmployementHistoryData(tempData[0],tempData[1],tempData[2],mydesignation,"")
		return OrgCompleteList

	def ExperienceParser(self):
		# get specific heders
		for employmentHeader in self.headersroot.findall('employmentHeader'):
			employmentHeaderText = employmentHeader.text
		RegEmploymentHeads = employmentHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").strip()
		
		# get specific lists
		# empdesigroot = ET.parse(BASE+'/ListData2/employer.zhrset').getroot()
		empElement = self.employerroot.findall('emp')
		desgElement = self.designationroot.findall('d')
		
		AllEmpList = []
		for i in empElement:
			AllEmpList.append(i.text.replace("&amp;", "&").lower())
		
		# AllDesgList = []
		# for i in desgElement:
		# 	AllDesgList.append(i.text.replace("&amp;", "&"))

		strDocumemtText = str(self.CompanyBaseSections2(RegEmploymentHeads))		
		# #print strDocumemtText
		# Extract_Org(strDocumemtText)
		EmplList = []
		ExpList = []
		DesgList=[]
		instindexP = 0
		instindexN = 0
		
		tempData = []
		from .CommonClassObject import EmployementsHistoryDetails
		self.EmployementsHistoryDetailsObj = EmployementsHistoryDetails()

		OrgCompleteList = []
		OrgCompleteList.extend(self.CompanyNamesFromNER(strDocumemtText))
		# #print "From NER"
		# #print OrgCompleteList
		# #print "NLTK"
		# from OrgFromNltk import Extract_Org
		# #print Extract_Org(self.ResumeText)

		emplists = self.check_data(strDocumemtText.lower(),AllEmpList)
		
		for emp in emplists:
				# #print emp
				regex = re.compile("[\s\n\r\t\)\(\.,\-]" + str(re.escape(emp.replace("&amp;", "&"))) + "[\s\n\r\t\)\(\.,\-]", re.IGNORECASE)
				m = regex.search(str(strDocumemtText.encode('utf-8')))
				if(m):
					EmplList.append(emp.replace("&amp;", "&"))
					instindexP = 0 if m.span()[0]-75 < 0 else m.span()[0]-75 
					instindexN = len(strDocumemtText) if m.span()[0]+75 > len(strDocumemtText) else m.span()[0]+75
					probebalExp = str(strDocumemtText[instindexP:instindexN].encode('utf-8'))
					regex = re.compile(re.escape(emp.replace("&amp;", "&"))+self.DurationRegex, re.IGNORECASE)
					tempExp = re.findall(regex,probebalExp)
					# if(len(tempExp)>0):
					# 	tempExp[0] = self.FormatDate(tempExp[0])
					# if(len(tempExp)>1):
					# 	tempExp[1] = self.FormatDate(tempExp[1])
					ExpList.append(tempExp)
					# #print probebalExp
					# self.EmployementSkills(probebalExp)
					isDesgfound = False
					# #print "------------------------------------"
					# #print probebalExp
					for desg in desgElement:
						if(isDesgfound):
							break
						for variant in desg.findall('v'):
								# #print variant.text
								regex = re.compile("[\s\n\r\t\)\(\.,\-]" + re.escape(variant.text.replace("&amp;", "&")) + "[\s\n\r\t\)\(\.,\-]", re.IGNORECASE)
								desgres = re.findall(regex,probebalExp)
								if(len(desgres)>0):
									# #print desgres
									DesgList.append(desgres[0].strip())
									isDesgfound=True
					if(not isDesgfound):
							DesgList.append("None")	


		

		data = []
		
		# #print EmplList
		for d in range(len(EmplList)):
			tempData = []
			if(EmplList[d]!=""):
				data.append(EmplList[d])
				tempData.append(EmplList[d])
				# #print EmplList[d]
			else:
				data.append("None")
				tempData.append("None")
			if(d<len(ExpList)):
				if(ExpList[d]):
					if(ExpList[d][0][0]!=""):
						data.append(ExpList[d][0][0])
						tempData.append(ExpList[d][0][0])
					else:
						data.append("None")
						tempData.append("None")
				else:
					data.append("None")
					tempData.append("None")	
				if(ExpList[d]):
					if(ExpList[d][0][1]!=""):
						data.append(ExpList[d][0][1])
						tempData.append(ExpList[d][0][1])
					else:
						data.append("None")
						tempData.append("None")
				else:
					data.append("None")	
					tempData.append("None")
			else:
				data.append("None")
				data.append("None")
				tempData.append("None")
				tempData.append("None")
			if(d<len(DesgList)):				
				tempData.append(DesgList[d])
			else:
				tempData.append("None")
			# #print tempData
			if(len(tempData)>0):
				# #print "dewfewfwf"
				self.EmployementsHistoryDetailsObj.AddEmployementHistoryData(tempData[0],tempData[1],tempData[2],tempData[3],"")
			
		OrgCompleteList.extend(data)
		if(len(OrgCompleteList)==0):
			OrgCompleteList.append("None")
			OrgCompleteList.append("None")
			OrgCompleteList.append("None")
			tempData.append("None")
			tempData.append("None")
			tempData.append("None")
			tempData.append("None")
			self.EmployementsHistoryDetailsObj.AddEmployementHistoryData(tempData[0],tempData[1],tempData[2],tempData[3],"")


		OrgCompleteList.append(strDocumemtText)
		return OrgCompleteList

	def compSkills(self, list1, list2):
		from CommonClassObject import SkillsDetails
		SkillSetDataList = []
		for val in list1:
			if val.lower() in list2:
				# #print val
				skillfreq = str(list2.count(val.lower()))				
				skillobj = SkillsDetails()
				skillobj.skillname = val
				skillobj.frequency = skillfreq 
				SkillSetDataList.append(skillobj)
		
		return SkillSetDataList

	def SkillsParser(self):
		# get specific lists
		SkillsElementRegex = '|'.join(re.escape(x.strip()) for x in str(self.skillsetroot.find('./itskills').text).split(','))
		# #print re.escape(SkillsElementRegex.replace("&amp;", "&")).replace('\\|','|')
		regex = re.compile("(?<!\S)(" + re.escape(SkillsElementRegex.replace("&amp;", "&")).replace('\\|','|') + ")\.?(?!\S)", re.I|re.M)
		dmatch = re.findall(regex, self.ResumeText)
		##print self.ResumeText
		##print dmatch
		from .CommonClassObject import SkillsDetails
		self.SkillSetDataList = []
		dmatchtemp = [x.encode('utf-8') for x in dmatch]
		dmatch = [x.encode('utf-8').lower() for x in dmatch]
		for skillDict in set(dmatch):
			skillobj = SkillsDetails()
			skillobj.skillname = str(dmatchtemp[dmatch.index(skillDict.lower())].decode("utf-8"))
			skillobj.frequency = dmatch.count(skillDict.lower())
			self.SkillSetDataList.append(skillobj) 
		return self.SkillSetDataList

	def GetFormatedSkills(self,dmatch):
		from CommonClassObject import SkillsDetails
		self.SkillSetDataList = []
		dmatchtemp = [x.encode('utf-8') for x in dmatch]
		dmatch = [x.encode('utf-8').lower() for x in dmatch]
		for skillDict in set(dmatch):
			skillobj = SkillsDetails()
			skillobj.skillname = str(dmatchtemp[dmatch.index(skillDict.lower())])
			skillobj.frequency = dmatch.count(skillDict.lower())
			self.SkillSetDataList.append(skillobj) 
		return self.SkillSetDataList

	def EmployementSkills(self,EmployementBlock):
		# get specific lists
		SkillsElementRegex = '|'.join(re.escape(x.strip()) for x in str(self.skillsetroot.find('./itskills').text).split(','))
		##print SkillsElementRegex
		##print re.escape(SkillsElementRegex.replace("&amp;", "&")).replace('\\|','|')
		regex = re.compile("(?<!\S)(" + re.escape(SkillsElementRegex.replace("&amp;", "&")).replace('\\|','|') + ")\.?(?!\S)", re.I|re.M)
		dmatch = re.findall(regex, EmployementBlock)
		# #print dmatch
		return dmatch

	def FormatDate(self,date):
		if(date!="None" or date!="" ):
			# #print "unformatted date"
			# #print date
			# #print "formatted date"
			if(date.lower() in ['onwards','till date','till now','till the date','till present','present','till today','till','date','continue']):
					date = datetime.date.today().strftime("%b-%Y")
					return date.capitalize()
			date = re.sub("(\s|\-{1,3}|\.|,|’|'|‘)", '$', date)
			
			y = date.split("$")
			y = [x for x in y if x.strip()!=""]

			# #print len(y)
			if(len(y)==1):
				year = y[0]
				if(len(year)==2):
					if(int(year)<60):
						year = "20"+year
					else:
						year = "19"+year
				date = 'Dec'+'-'+year.strip()
				# #print date
				return date.capitalize()

			if(len(y)==3):
				try:
					if(int(y[0].replace("th","").replace("rd","").replace("st","").replace("nd","")) in range(1,32)):
						y.pop(0)
					else:
						y.pop(1)
				except(Exception):
					y.pop(0)

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
			# #print date
			return date.capitalize()

	def ToJSON(self):
		DataJson = {}
		## skills 
		DataJson["SkillSetDetails"] = self.SkillSetDataList
		## PersonnelDetails
		from .CommonClassObject import PersonalDetails
		PersonnelDetailsObj = PersonalDetails()
		phoneList = self.GetPhoneNumber()
		# PersonnelDetailsObj.Contact1 = phoneList[0]
		# PersonnelDetailsObj.Contact2 = phoneList[1]
		emailList = self.GetEmailId()

		# PersonnelDetailsObj.EmailId1 = emailList[0]
		# PersonnelDetailsObj.EmailId2 = emailList[1]

		PersonnelDetailsObj.ContactDetails.Contact = phoneList[0]
		PersonnelDetailsObj.ContactDetails.AlternateContact = phoneList[1]
		PersonnelDetailsObj.ContactDetails.EmailId = emailList[0]
		PersonnelDetailsObj.ContactDetails.AlternateEmailId = emailList[1]
		dob = self.GetDob()
		PersonnelDetailsObj.DateOfBirth = dob
		PersonnelDetailsObj.ResumeInPlainText = self.ResumeText
		PersonnelDetailsObj.PanNo = self.GetPan()
		PersonnelDetailsObj.PassportNo = self.GetPassport()
		PersonnelDetailsObj.Gender = self.GetGender()
		CandidateFullName = self.GetCandidateName(PersonnelDetailsObj.ContactDetails.EmailId,PersonnelDetailsObj.ContactDetails.AlternateEmailId,PersonnelDetailsObj.ContactDetails.Contact,PersonnelDetailsObj.ContactDetails.AlternateContact)
		#print(CandidateFullName)
		PersonnelDetailsObj.CandidateNameDetails.CandidateFullName = CandidateFullName
		names= CandidateFullName.split(" ")
		if (len(names) == 1):
			PersonnelDetailsObj.CandidateNameDetails.FirstName = names[0]
			PersonnelDetailsObj.CandidateNameDetails.MiddleName = ""
			PersonnelDetailsObj.CandidateNameDetails.LastName = ""
		elif (len(names) == 2):
			PersonnelDetailsObj.CandidateNameDetails.FirstName = names[0]
			PersonnelDetailsObj.CandidateNameDetails.MiddleName = ""
			PersonnelDetailsObj.CandidateNameDetails.LastName = names[1]
        
		elif (len(names) > 2):     
			PersonnelDetailsObj.CandidateNameDetails.FirstName = names[0]
			PersonnelDetailsObj.CandidateNameDetails.MiddleName = names[1]
			PersonnelDetailsObj.CandidateNameDetails.LastName = names[2]

		GetCityAndAddress = self.GetCityAndAddress()
		PersonnelDetailsObj.Address = GetCityAndAddress[0]
		PersonnelDetailsObj.City = GetCityAndAddress[1]
		DataJson["PersonnelDetails"] = [PersonnelDetailsObj]

		## QualificationsDetails
		# from CommonClassObject import QualificationsDetails
		# QualificationsDetailsObj = QualificationsDetails()
		# QualificationsDetailsObj.HighestQualificationDegree = "B.Tech"
		# QualificationsDetailsObj.AddQualificationData("institute Name","B.Tech","2010")
		DataJson["QualificationsDetails"] = self.QualificationsDetailsObj
		
		## EmployementsHistoryDetails
		# from CommonClassObject import EmployementsHistoryDetails
		# EmployementsHistoryDetailsObj = EmployementsHistoryDetails()
		# EmployementsHistoryDetailsObj.ExperianceInMonth=48
		# EmployementsHistoryDetailsObj.AddEmployementHistoryData("Gateway TechnoLabs Pvt. Ltd. Gateway Group of Companies",None,None,"Asst. Manager-HR","IT")
		
		DataJson["EmployementsHistoryDetails"] = self.EmployementsHistoryDetailsObj
		
		myallDates = []
		ActualDates=[]

		# for myHistory in self.EmployementsHistoryDetailsObj.EmployementHistoryData:
		# 	if(len(myHistory.WorkExperience)!=0):
		# 		if myHistory.WorkExperience[0].ToPeriod.Date is not "None" and myHistory.WorkExperience[0].FromPeriod.Date is not "None":
		# 			myallDates.append([self.ResumeText.lower().index(myHistory.WorkExperience[0].FromPeriod.Date.lower()),self.ResumeText.lower().index(myHistory.WorkExperience[0].ToPeriod.Date.lower())])
		# 			ActualDates.append([myHistory.FromPeriod,myHistory.ToPeriod])
		# 		else:
		# 			if myHistory.ToPeriod is "None" and myHistory.FromPeriod is not "None":
		# 				myallDates.append([self.ResumeText.lower().index(myHistory.FromPeriod.lower()),self.ResumeText.lower().index(myHistory.FromPeriod.lower())])
		# 				ActualDates.append([myHistory.FromPeriod,myHistory.FromPeriod])
		# 			elif myHistory.ToPeriod is not "None" and myHistory.FromPeriod is "None":
		# 				myallDates.append([self.ResumeText.lower().index(myHistory.ToPeriod.lower()),self.ResumeText.lower().index(myHistory.ToPeriod.lower())])
		# 				ActualDates.append([myHistory.ToPeriod,myHistory.ToPeriod])
		# # #print ActualDates
		# ActualDates = [[self.FormatDate(x),self.FormatDate(y)] for x, y in ActualDates]
		# # #print ActualDates
		for i in range(len(self.EmployementsHistoryDetailsObj.EmployementHistoryData)): 
			restring = self.EmployementsHistoryDetailsObj.EmployementHistoryData[i].CompanyBlock
			for x in range(len(DataJson["SkillSetDetails"])):
				regex = re.compile("(?<!\S)(" + str(re.escape(str(DataJson["SkillSetDetails"][x].skillname).replace("&amp;", "&"))).replace('\\|','|') + ")(?!\S)", re.I|re.M)
				dmatch = re.findall(regex, restring)
				if(len(dmatch)>0):
					try:
						myTodate = self.EmployementsHistoryDetailsObj.EmployementHistoryData[i].WorkExperience[0].ToPeriod.Date
						myFromdate = self.EmployementsHistoryDetailsObj.EmployementHistoryData[i].WorkExperience[0].FromPeriod.Date
						if(DataJson["SkillSetDetails"][x].Skillused.lastused==""):
							DataJson["SkillSetDetails"][x].Skillused.lastused = myTodate
						elif(int(DataJson["SkillSetDetails"][x].Skillused.lastused.split("-")[1])<int(myTodate.split("-")[1])):
							DataJson["SkillSetDetails"][x].Skillused.lastused = myTodate
					except(Exception):
						pass
					try:
						DataJson["SkillSetDetails"][x].Skillused.months += abs(int(((datetime.datetime.strptime(myFromdate , '%b-%Y')-datetime.datetime.strptime(myTodate, '%b-%Y')).days)/30))
					except(Exception):
						pass
					
		DataJson["SrNo"] = 1
		CandidateData = {}
		CandidateData["CandidateData"]=[DataJson]
		CandidateData["Version"]="1.0.0.0"
		##print CandidateData
		return CandidateData

		###########
		#def SkillsProjectwise(self,CompanywiseText):
		#	for data in CompanywiseText:

		###########
	
	def obj_dict(self,obj):
		return obj.__dict__

	def GetPhoneNumber(self):
		from .phoneParser import GetMaxTwoPhoneNumbers
		return GetMaxTwoPhoneNumbers(self.ResumeText)
	
	def GetEmailId(self):
		from .GetAllEmailIDs import GetMaxTwoEmails
		return GetMaxTwoEmails(self.ResumeText)

	def GetDob(self):
		from .dobParser import GetDobInResume
		return GetDobInResume(self.ResumeText)

	def GetPan(self):
		from .GetPAN import GetPAN
		return GetPAN(self.ResumeText)
	
	def GetCandidateName(self,em1,em2,ph1,ph2):
		from .GetCandidateName import ExtractName
		if em2=="":
			em2=em1
		if ph2=="":
			ph2=ph1
		return ExtractName(self.ResumeText,em1,em2,ph1,ph2,"")
	
	def GetCityAndAddress(self):
		from .GetCityAndAddress import GetCityAndAddress
		return GetCityAndAddress(self.ResumeText)
	
	def GetPassport(self):
		from .GetPassport import GetPassport
		return GetPassport(self.ResumeText)
	
	def GetGender(self):
		from .GetGender import GetGender
		return GetGender(self.ResumeText)

	def GetFuncAreaFromCompanyBlock(self,text):
		f=filter(None, re.split("[, \-!?: \\n \s]+",text ))
		list1=[]
		for i in f:
			list1.append(i.strip())
		for i in list1:
			if i.lower() in self.stopWords:
				list1.remove(i)
		root = self.functionalroot
		dictionary= {}
		count=0
		for fa in root :	
			for child in fa :		
				for word in list1:
					x=child.text.lower()
					y=word.lower()		
					if (x==y):
						count=count+1
				v=fa.attrib
				dictionary [v['name']]=count
			count=0	  
		maximum = max(dictionary, key=dictionary.get)
		try:
			maximum = max({}, key=dictionary.get)
		except(Exception):
			maximum = ""
		return maximum
	
	def ExperienceParser2(self):
		empHistory = self.designationTenureParser()
		# empHistory = []
		from collections import namedtuple
		from .CommonClassObject import EmployementsHistoryDetails,EmployementHistoryData,WorkExperience
		self.EmployementsHistoryDetailsObj = EmployementsHistoryDetails()
		for EmployementHistoryDataList in empHistory:
			EmployementHist = EmployementHistoryData()
			EmployementHist.Organization = EmployementHistoryDataList["Organization"]
			EmployementHist.CompanyBlock = EmployementHistoryDataList["CompanyBlock"]
			EmployementHist.FunctionalArea = self.GetFuncAreaFromCompanyBlock(EmployementHist.CompanyBlock)
			for w in EmployementHistoryDataList["WorkExperience"]:
				WorkExperienceObj = WorkExperience()
				WorkExperienceObj.DesignationList = w["DesignationList"]
				WorkExperienceObj.totalMonthsOfExperience = w["totalMonthsOfExperience"]
				WorkExperienceObj.FromPeriod = Struct(w["FromPeriod"])
				WorkExperienceObj.ToPeriod = Struct(w["ToPeriod"])
				self.EmployementsHistoryDetailsObj.TotalExperienceInMonths += WorkExperienceObj.totalMonthsOfExperience
				EmployementHist.WorkExperience.append(WorkExperienceObj)
			self.EmployementsHistoryDetailsObj.EmployementHistoryData.append(EmployementHist)


		return empHistory			 

	def GetExpAsync(self):
		try:
			#print ("CHALNA CHALU")
			self.ReturnResult= self.returnListforCSV(self.designationTenureParser())
			#print("CHALNA BAND")
			self.isResult = True
		except:
			#print ("Exception 1")
			self.start = time.perf_counter()
			try:
				self.ReturnResult= self.returnListforCSV(self.designationTenureParser())
				self.isResult = True
			except:
				#print ("Exception 2")
				self.start = time.perf_counter()
				try:
					self.ReturnResult= self.returnListforCSV(self.designationTenureParser())
					self.isResult = True
				except:
					#print ("Exception 3")
					self.ReturnResult = ["Header/Company/Designation Master incomplete"]
					self.isResult = True	

	def AllParsersCall(self):
		# #print self.ResumeText
		ParsedDetails = {}
		ParsedDetails["Education"] = self.EducationParser()
		ParsedDetails["Skills"] = self.SkillsParser()
		ParsedDetails["Experience"] = self.ExperienceParser2()	
		# #print(self.designationTenureParser())
		# ParsedDetails["Education"] = []
		# ParsedDetails["Experience"] = []
		# ParsedDetails["Skills"] = []
		# #print ParsedDetails["Skills"]
		# return ParsedDetails["Education"]
		# make JSON formate which you want to return from our objects 
		myskillsjson = self.ToJSON()
		DataJson =  json.dumps(myskillsjson, default=self.obj_dict)
		DataToreturn = json.loads(DataJson)
		return DataToreturn

	def AllParsersCall2(self):
		ParsedDetails = {}
		ParsedDetails["Education"] = []
		try:
			self.start = time.perf_counter()
			self.isResult = False
			self.ReturnResult = []
			try:
				_thread.start_new_thread(self.GetExpAsync,())
			except (KeyboardInterrupt, SystemExit):
				ParsedDetails["Experience"]  = ["TestSeparately"]	
				##print ()	
			while(((time.perf_counter() - self.start)<10) and (not self.isResult)):
				pass
			ParsedDetails["Experience"] = self.ReturnResult
		except (KeyboardInterrupt, SystemExit):
			ParsedDetails["Experience"]  = ["TestSeparately"]
			pass			
		ParsedDetails["Skills"] = []
		return ParsedDetails	

def main():	
	input = open('input.txt','r').read()
	##print (repr(input))
	obj = GenericResumeParser(str(input))
	workExperienceList = obj.designationTenureParser()
	print (workExperienceList)
main()

class Struct(object):
    def __init__(self, adict):
        """Convert a dictionary to a class

        @param :adict Dictionary
        """
        self.__dict__.update(adict)
        for k, v in adict.items():
	        if isinstance(v, dict):
	            self.__dict__[k] = Struct(v)
