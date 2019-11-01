# -*- coding: utf-8 -*-
import re
from dateutil.parser import parse

def GetDobInResume(a):
	DOB_REGEX1 = "(Born\s*On|Date\s*of\s*Birth|D.O.B[.]*|DOB\s*[:|-]|Date\s*of\s*Birth.*?Age|Birth\s*Date)\s*[:|-|:\s*-]*[\s]*[\(|\{|\[]*([a-z0-9].*?[\d]{2})\s*[a-z\.\s*]"
	DOB_REGEX2 = "(Date\s*of\s*Birth|D.O.B[.]*|DOB\s*[:|-]|Date\s*of\s*Birth.*?Age|Birth\s*Date|Born On)\s*[:|-|:\s*-]*[\s]*[\(|\{|\[]*([a-z0-9].*?[\d]{4})\s*[a-z\.\s*]"
	
	testDocument = a
	dob = "";
	regex = re.compile(DOB_REGEX2, re.IGNORECASE)
	m = re.findall(regex, testDocument)
	if(len(m)!=0):
		try:
			if(m[0][1].strip()!=""):
				try:
					dob = parse(m[0][1].strip(),dayfirst=True).strftime('%d-%m-%Y')
				except Exception, e:
					dob = ""
			else:
				regex = re.compile(DOB_REGEX1, re.IGNORECASE)
				m = re.findall(regex, testDocument)
				try:
					dob = parse(m[0][1].strip(),dayfirst=True).strftime('%d-%m-%Y')
				except Exception, e:
					dob = ""
		except Exception, e:
			dob = ""
	return dob
