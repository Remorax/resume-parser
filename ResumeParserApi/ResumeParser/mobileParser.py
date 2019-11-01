# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import textract
import re
import csv
import glob, os
from nerForCompany import OrgNER


def GetMaxTwoPhoneNumbers(a):
	PHONE_REGEX1 = "(\\(?(\\+)?91\\)?(\\s)?(\\-)?(\\s)?)?([7|8|9][\\d]{2}(\\s|-)?[\\d]{3}(\\s|-)?[\\d]{4,5})"
	PHONE_REGEX2 = "(\\(?(\\+)?91\\)?(\\s)?(\\-)?(\\s)?)?([7|8|9][\\d]{4}(\\s|-)?[\\d]{5,6})"
	PHONE_REGEX3 = "(\\(?(\\+)?91\\)?(\\s)?(\\-)?(\\s)?)?([7|8|9][\\d]{3}(\\s|-)?[\\d]{3}(\\s|-)?[\\d]{3,4})"
	PHONE_REGEX4 = "(\\(?(\\+)?(91|0)\\)?(\\s)?(\\-)?(\\s)?)?(([\\d]{2,4})\\s*(\\-)?\\s*[\\d]{6,11})"
	PHONE_REGEX5 = "(([\\(]\\s*([\\d]{2,5})\\s*[\\)])?\\s*[\\d]{6,11})"
	PHONE_REGEX6 = "([0-9+\\(][\\(\\)0-9 +-]{6,20}[0-9])"

	testDocument = textract.process(a)
	phoneRegexNo = 0

	phoneRegexNo = 1
	telephone1 = ExtractPhone(PHONE_REGEX1, testDocument, phoneRegexNo)
	if(telephone1 == ''):
		phoneRegexNo = 2
		telephone1 = ExtractPhone(PHONE_REGEX2, testDocument, phoneRegexNo)
		if(telephone1 == ''):
			phoneRegexNo = 3
			telephone1 = ExtractPhone(PHONE_REGEX3, testDocument, phoneRegexNo)
			if(telephone1 == ''):
				phoneRegexNo = 4
				telephone1 = ExtractPhone(PHONE_REGEX4, testDocument, phoneRegexNo)
				if(telephone1 == ''):
					phoneRegexNo = 5
					telephone1 = ExtractPhone(PHONE_REGEX5, testDocument, phoneRegexNo)
					if(telephone1 == ''):
						phoneRegexNo = 6
						telephone1 = ExtractPhone(PHONE_REGEX6, testDocument, phoneRegexNo)
	print 'No1'
	print telephone1.replace("\n","").replace(" ","").replace("\r","").replace("\t","").strip()

	phoneRegexNo = 1
	telephone2 = ExtractPhoneOther(PHONE_REGEX1, testDocument, phoneRegexNo, telephone1)
	if(telephone2 == ''):
		phoneRegexNo = 2
		telephone2 = ExtractPhoneOther(PHONE_REGEX2, testDocument, phoneRegexNo, telephone1)
		if(telephone2 == ''):
			phoneRegexNo = 3
			telephone2 = ExtractPhoneOther(PHONE_REGEX3, testDocument, phoneRegexNo, telephone1)
			if(telephone2 == ''):
				phoneRegexNo = 4
				telephone2 = ExtractPhoneOther(PHONE_REGEX4, testDocument, phoneRegexNo, telephone1)
				if(telephone2 == ''):
					phoneRegexNo = 5
					telephone2 = ExtractPhoneOther(PHONE_REGEX5, testDocument, phoneRegexNo, telephone1)
					if(telephone2 == ''):
						phoneRegexNo = 6
						telephone2 = ExtractPhoneOther(PHONE_REGEX6, testDocument, phoneRegexNo, telephone1)
		
	

	print 'No2'
	print telephone2.replace("\n","").replace(" ","").replace("\r","").replace("\t","").strip()
	return ""

def ExtractPhone(RegexToUse, testDocument, phoneRegexNo):
	mobileNumber = ""
	temp = ""
	tempLandLineNumber = ""
	tempLandLineNo = ""

	temp = testDocument
	
	regex = re.compile(RegexToUse, re.IGNORECASE)
	m = re.findall(regex, temp)

	if(len(m) > 0):
		if (phoneRegexNo == 4):
		   for strNo in m:
				if(len(strNo[6])>0):
					tempLandLineNumber = strNo[6].strip()
					tempLandLineNo = tempLandLineNumber
					tempLandLineNumber = re.sub(r"([\\s]|-)", "", tempLandLineNo)
					if (len(tempLandLineNumber) >= 10):
						mobileNumber = tempLandLineNo
						break
		elif (phoneRegexNo == 5 or phoneRegexNo == 6):
		   	for strNo in m:
				if(len(strNo[1])>6):
					tempLandLineNumber = strNo[1].strip()
					tempLandLineNo = tempLandLineNumber
					tempLandLineNumber = re.sub(r"([\\s]|\\(|\\))", "", tempLandLineNo)
					if (len(tempLandLineNumber) >= 10):
						mobileNumber = tempLandLineNo
						break
		elif (phoneRegexNo == 1 or phoneRegexNo == 2 or phoneRegexNo == 3):
			mobileNumber = m[0][5].strip() 	

	if(mobileNumber == ''):
		regex = re.compile(RegexToUse, re.IGNORECASE)
		me = re.findall(regex, temp)

		if(len(me) > 0):
			if (phoneRegexNo == 4):
				for strNo in me:
					if(len(strNo[6])>6):
						tempLandLineNumber = strNo[6].strip()
						tempLandLineNo = tempLandLineNumber
						tempLandLineNumber = re.sub(r"([\\s]|-)", "", tempLandLineNo)
						if (len(tempLandLineNumber) >= 10):
							mobileNumber = tempLandLineNo
							break
			elif (phoneRegexNo == 5 or phoneRegexNo == 6):
				for strNo in me:
					if(len(strNo[1])>6):
						tempLandLineNumber = strNo[1].strip()
						tempLandLineNo = tempLandLineNumber
						tempLandLineNumber = re.sub(r"([\\s]|\\(|\\))", "", tempLandLineNo)
						if (len(tempLandLineNumber) >= 10):
							mobileNumber = tempLandLineNo
							break
			elif (phoneRegexNo == 1 or phoneRegexNo == 2 or phoneRegexNo == 3):
				mobileNumber = me[0][5].strip()

	return mobileNumber


def ExtractPhoneOther(RegexToUse, testDocument, phoneRegexNo, telephone1):
	mobileNumber = ""
	temp = ""
	tempLandLineNumber = ""
	tempLandLineNo = ""

	temp = testDocument
	temp = temp.replace(telephone1, " ")

	regex = re.compile(RegexToUse, re.IGNORECASE)
	m = re.findall(regex, temp)

	if(len(m) > 0):
		if (phoneRegexNo == 4):
			for strNo in m:
				if(len(strNo[6])>0):
					tempLandLineNumber = strNo[6].strip()
					tempLandLineNo = tempLandLineNumber
					tempLandLineNumber = re.sub(r"([\\s]|-)", "", tempLandLineNo)
					if (len(tempLandLineNumber) >= 10):
						mobileNumber = tempLandLineNo
						break
		elif (phoneRegexNo == 5 or phoneRegexNo == 6):
			for strNo in m:
				if(len(strNo[1])>6):
					tempLandLineNumber = strNo[1].strip()
					tempLandLineNo = tempLandLineNumber
					tempLandLineNumber = re.sub(r"([\\s]|\\(|\\))", "", tempLandLineNo)
					if (len(tempLandLineNumber) >= 10):
						mobileNumber = tempLandLineNo
						break
		elif (phoneRegexNo == 1 or phoneRegexNo == 2 or phoneRegexNo == 3):
			mobileNumber = m[0][5].strip() 	

	if(mobileNumber == ''):
		regex = re.compile(RegexToUse, re.IGNORECASE)
		me = re.findall(regex, temp)

		if(len(me) > 0):
			if (phoneRegexNo == 4):
				for strNo in me:
					if(len(strNo[6])>6):
						tempLandLineNumber = strNo[6].strip()
						tempLandLineNo = tempLandLineNumber
						tempLandLineNumber = re.sub(r"([\\s]|-)", "", tempLandLineNo)
						if (len(tempLandLineNumber) >= 10):
							mobileNumber = tempLandLineNo
							break
			elif (phoneRegexNo == 5 or phoneRegexNo == 6):
				for strNo in me:
					if(len(strNo[1])>6):
						tempLandLineNumber = strNo[1].strip()
						tempLandLineNo = tempLandLineNumber
						tempLandLineNumber = re.sub(r"([\\s]|\\(|\\))", "", tempLandLineNo)
						if (len(tempLandLineNumber) >= 10):
							mobileNumber = tempLandLineNo
							break
			elif (phoneRegexNo == 1 or phoneRegexNo == 2 or phoneRegexNo == 3):
				mobileNumber = me[0][5].strip()

	return mobileNumber

print GetMaxTwoPhoneNumbers('testdocu.docx')