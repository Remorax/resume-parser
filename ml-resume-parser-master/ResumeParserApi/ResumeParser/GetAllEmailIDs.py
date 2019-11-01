# -*- coding: utf-8 -*-
import re

def GetMaxTwoEmails(a):
	EMAIL_REGEX = "\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b"
	EMAIL_REGEX1 = "^(?!\.)(""([^""\r\\]|\\[""\r\\])*""|([-a-z0-9!#$%&'*+/=?^_`{|}~]|(?<!\.)\.)*)(?<!\.)@[a-z0-9][\w\.-]*[a-z0-9]\.[a-z][a-z\.]*[a-z]$"
	testDocument = a
	Email1 = ExtractEmail(testDocument, EMAIL_REGEX)
	if(Email1 == ''):
		Email1 = ExtractEmail(testDocument, EMAIL_REGEX1)

	Email2 = ExtractEmailOther(testDocument, EMAIL_REGEX, Email1)
	if(Email2 == ''):
		Email2 = ExtractEmailOther(testDocument, EMAIL_REGEX1, Email1)
	
	# print 'Email1'
	# print Email1.strip()

	# print 'Email2'
	# print Email2.strip()

	return [Email1.strip(),Email2.strip()]
def ExtractEmail(testDocument, RegexToUse):
	emailAddress = ''
	temp = testDocument
	
	regex = re.compile(RegexToUse, re.IGNORECASE)
	m = re.findall(regex, temp)
	
	if(len(m) > 0):
		emailAddress = m[0].strip()

	return emailAddress
	
def ExtractEmailOther(testDocument, RegexToUse, Email1):
	
	emailAddress = ''
	temp = testDocument;
	temp = temp.replace(Email1, " ")

	regex = re.compile(RegexToUse, re.IGNORECASE)
	m = re.findall(regex, temp)

	if(len(m) > 0):
		if(len(m) > 0):
			emailAddress = m[0].strip()

	return emailAddress

# print GetMaxTwoEmails('testdocu.docx')