import xml.etree.ElementTree as ET
import re,os

BASE = os.path.dirname(os.path.abspath(__file__))
headersroot2 = ET.parse(BASE+'/ListData2/headers2.zhrset').getroot()
articles = ['a', 'an', 'of', 'the', 'is', 'in', 'and']

ResumeText = ''

def title_except(s, exceptions):
	word_list = re.split(' ', s)
	final = [word_list[0].capitalize()]
	for word in word_list[1:]:
		final.append(word if word in exceptions else word.capitalize())
	return " ".join(final)

def callMeFirst(restext):
	global ResumeText
	ResumeText = str(re.sub(r'\\x\w{1,2}',' ',restext))
	resumeTxt = ""
	for word in ResumeText:
		if(ord(word)<194):
			resumeTxt += word
	ResumeText = resumeTxt
	findAllBlocks()

def TitleCleaner(title):
	title = str(re.sub(r"(\\n|\\r|\\t)", '', title))
	return title	

def getHeader(headerString):
	for employmentHeader in headersroot2.findall(headerString):
		employmentHeaderText = employmentHeader.text
	RegEmploymentHeads = employmentHeaderText.replace("(","").replace(")","").replace("\n","").replace("\r","").replace("\t","").replace("&amp;","&").replace("/","\/").strip()
	RegEmploymentHeads = RemoveLowerCase(RegEmploymentHeads)
	return RegEmploymentHeads

def CompanyBaseSections(headRegex,isFoundFlag):
	testDocument = ResumeText
	regex = re.compile(r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\\r|\\n|\\t)",re.M)
	headRegex2List = []
	headRegex3List = []
	for header in headRegex:
		headRegex2List.append(header.upper())
		headRegex3List.append(title_except(header, articles))
	headRegex2List = list(set(headRegex2List))
	headRegex2 = '|'.join(headRegex2List)
	headRegex3List = list(set(headRegex3List))
	headRegex3 = '|'.join(headRegex3List)	
	regex2 = re.compile(r"("+headRegex2+r")( )*( |\:|\-|\-( )*\:|\:( )*\-|\>|\-\>)?( )*",re.M)
	regex3 = re.compile(r"("+headRegex3+r")( )*( |\:|\-|\-( )*\:|\:( )*\-|\>|\-\>)?( )*",re.M)
	#if (headRegex == 'PERSONAL DETAILS|Personal Interests|MISCELLANEOUS|INTERESTS|Miscellaneous|PERSONAL INTERESTS|STRENGTHS|Family Background|Hobbies|Interests|Personal Information|STRENGTH|DATE OF BIRTH|Personal Profile|Personal details|Personal detail|Personal information|PERSONAL QUALITIES|Strengths|Personal Qualities|Date of Birth|Personal interests|Personal Details|PERSONAL STRENGTH|PERSONAL DATA|Date of birth|HOBBIES|FAMILY BACKGROUND|Personal data|Family background|PERSONAL PROFILE|PERSONAL INFORMATION|Personal profile|PERSONAL DETAIL|Address|Personal strength|Personal Strengths|Personal Strength|Personal Data|Strength|Personal Detail|ADDRESS|PERSONAL STRENGTHS|Personal qualities|Personal strengths'):
	#print (r"(\\r|\\n|\\t)( )*("+headRegex+r")( )*( |\:|\-|\-( )?\:|\:( )?\-|>|\-( )*\>)?( )*(\(?(Total)? *(Professional)? *(Experience)? *(in year|in month|in week|in day)? *(s)? *(\-|\–|\=|\:|\-\:|\-\:|\-\>|\>)* *\d{1,4}\.*\d{1,4}? *(Year|Month|Week|Day)s?\)?)? *(\\r|\\n|\\t)","\n\n\n\n^^^^^^^^^\n\n\n\n",testDocument)
	dmatch=re.findall(regex,testDocument)
	#print (testDocument)
	if(len(dmatch)>0):
		position = [(m.start(0), m.end(0), TitleCleaner(m.group())) for m in re.finditer(regex, testDocument)]
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
			restext = ResumeText[tupleelem[0]:(tupleelem[1]+1)]
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
		position = [(m.start(0), m.end(0), TitleCleaner(m.group())) for m in re.finditer(regex2, testDocument)]
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
			position = [(m.start(0), m.end(0), TitleCleaner(m.group())) for m in re.finditer(regex3, testDocument)]
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

def RemoveLowerCase(RegEmploymentHeads):
	returnList = []
	RegList = RegEmploymentHeads.split('|')
	for (n,i) in enumerate(RegList):
		returnList.append(i.upper())
		returnList.append(title_except(i, articles))
		returnList.append(i.capitalize())	
	returnList = list(set(returnList))
	RegEmploymentHeads = '|'.join(returnList)
	return (RegEmploymentHeads)

def findAllBlocks():
	print (ResumeText)
	allBlocksList = []
	result = CompanyBaseSections(getHeader('educationHeader',),1)
	allBlocksList.append({'BlockName':"Education",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('accomplishmentsHeader'),1)
	allBlocksList.append({'BlockName':"Accomplishments",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('awardsHeader'),1)
	allBlocksList.append({'BlockName':"Awards",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('extracurricularHeader'),1)
	allBlocksList.append({'BlockName':"ExtraCurricular Activities",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('miscHeader'),1)
	# print (result)
	allBlocksList.append({'BlockName':"Miscellaneous",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('summaryHeader'),1)
	allBlocksList.append({'BlockName':"Summary",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('skillsHeader'),1)
	allBlocksList.append({'BlockName':"Skills",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('employmentHeader'),1)
	#print (result)
	allBlocksList.append({'BlockName':"Employment",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	result = CompanyBaseSections(getHeader('credibilityHeader'),1)
	allBlocksList.append({'BlockName':"Credibility",'StartingIndex':result[0],"BlockText":"", "EndingIndex":"", "BlockTitle":result[2]})
	allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
	for (i,Block) in enumerate(allBlocksList):
		if(Block['StartingIndex'] == 0):
			Block['EndingIndex']=(len(ResumeText)-1)
			Block['BlockText']=ResumeText
		else:
			if(i!=8):
				nextBlock = allBlocksList[i+1]
				Block['EndingIndex']=nextBlock['StartingIndex']
			else:
				Block['EndingIndex']=len(ResumeText)-1
			Block['BlockText']=ResumeText[int(Block['StartingIndex']):int(Block['EndingIndex'])]

	print (allBlocksList)		
	##### HERE INSTEAD OF EMPLOYMENT BLOCK, INSERT THE NAME OF THE BLOCK YOU WANT TO FIND


	if ('employmentBlock' not in locals()):
		employmentBlockRegexObj = re.compile(r"(\\r|\\n)\s*(\u2022|\u2023|\u25E6|\u2043|\u2219)?("+getHeader('employmentHeader')+r")\s*(\d{1,2})( |\:|\-|\-(\s)?\:|\:(\s)?\-|>|\-\s*\>|\d{1,2})?( )?\s*(\\r|\\n)",re.M)
		employmentBlockL = [(m.group(),m.start(),m.end()) for m in re.finditer(employmentBlockRegexObj,ResumeText)]
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
							Block['BlockText']=ResumeText[int(Block['StartingIndex']):int(ans)]
							Block['EndingIndex']=ans
						else:
							Block['BlockText']=ResumeText[int(Block['StartingIndex']):]
							Block['EndingIndex']=len(ResumeText)-1	
						Block['BlockText']=ResumeText[int(Block['StartingIndex']):int(Block['EndingIndex'])]
						employmentBlock = Block['BlockText']
						employmentBloc = Block
						employmentBlockIndex = j
		except:
			employmentBlock = ResumeText
			employmentBloc = {'BlockName':"Employment",'StartingIndex':0,'EndingIndex':(len(ResumeText)-1),'BlockText':employmentBlock,'BlockTitle':''}				
		allBlocksList = sorted(allBlocksList, key=lambda k: k['StartingIndex'])
	print (allBlocksList)

input =  """+91-9027735751\n\nHarsh Bihari Agarwal                                             Email: harshagarwal0291@gmail.com\n\n\n\n\n\nPROFESSIONALOBJECTIVE\n\n\n\nA passion to be an expert at my skills and abilities giving all my strengths against the challenges made by the job and thus becoming an integral part of the group which is    Intended to put the company always in new rising heights.\n\n\n\n\n\nSUMMARY\n\n\n\nHaving 2.6 years of experience in Banking Domain.\n\n\n\nExperience in cash handling.\n\n\n\nHandling Front Desk queries in a retail Banking Environment including AOF, \n\n               CQMS, RTGS, Statements, ,NEFT, Fund Transfer, DD and Customer queries.\n\n\n\nHard working, leadership qualities and self-starter.\n\n\n\nWilling to learn and adapt to new challenges.\n\n\n\nGood communication and interpersonal skills.\n\n\n\n\n\n\n\nWORK EXPERIENCE (2..6 years) \n\n \n\n\n\n\xc2\xa7 Yes Bank\xe2\x80\x93BSP (Branch Service Partner) from Nov2011 to till date.\n\n\n\nJob Responsibilites \xe2\x80\x93 \n\n\t\n\nCash Handling.\n\nCustomer Service.\n\nAccount opening.\n\nTransaction handling includes NEFT, RTGS,DD, Fund Transfer.\n\nCross sales to the customers like LI , CASA.\n\n\n\n\n\nEDUCATION\n\n\n\n\n\n\xc2\xa7 BBA from Jaipuria Institute of technology, Ghaziabad with an aggregate of       56.4%.\n\n\xc2\xa7 10+ 2 from CBSE Board, Dewan Public School, hapur, with 45% in batch 2008.\n\n\xc2\xa7 10 from CBSE Board, Dewan Public School, hapur, with 56.8%  in batch 2006.\n\n\n\n\n\n\n\n\n\nEXTRA ACTIVITIES\n\n\n\n\xc2\xa7 Selected in YES Bank Cricket team.\n\n\n\n\n\nACADEMIC PROJECT UNDERTAKEN\n\n\n\n\n\n\n\nCompany Name\n\n\n\nShriram Pistons and Rings ltd,Ghaziabad\n\n \n\nProject Description\n\n\n\nProject on the training and development of shriram pistons and rings, was taken into the BBA Vth semester,\n\n\n\nProject Duration\n\n\n\n2months\n\n\n\n\n\nNON-TECHNICALASSETS\n\n\n\n\xc2\xb7 Good Communication and interpersonal skills\n\n\xc2\xb7 Work effectively in a team as well as individual\n\n\xc2\xb7 Can handle pressure and very energetic.\n\n\xc2\xb7 Ambitious, innovative and can coordinate very well.\n\n\n\n\n\n\n\nHOBBIES\n\n\xc2\xb7Playing Cricket.\n\n\xc2\xb7Listening music.\n\n\n\n\n\n\n\n\n\nLANGUAGE KNOWN\n\n\n\nRead/Write:                              English, Hindi\n\nSpeak:                                      English, Hindi\n\n\n\n\n\n\n\nPERSONAL DETAILS\n\n\n\nNationality                                Indian\n\n  Gender                                     Male            \n\n  Marital Status                           Single\n\nDate of Birth                               02-01-1991\n\nFather\xe2\x80\x99s Name                           Mr.S.K. Agarwal\n\nPhone No                                   Ph: +91-9412825480\n\nADDRESS                                1433,New shivpuri, Hapur\n\n\n\nHarsh BihariAgarwal\n\nPage1"""
callMeFirst(repr(input))
