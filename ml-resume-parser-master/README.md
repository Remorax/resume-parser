# ml-resume-parser
Machine Learning based resume parser code lies in this repo

Setup Requirments:
python 2.7 64bit
Make a virtual environment. Activate it then clone this project in that folder.
find a requirement.txt file inside ResumeParserApi folder.
run a command on that folder pip install -r requirement.txt
to fullfill all python library requirements. If you got any compile error regarding visual c++ 
then install Microsoft Visual C++ Compiler for Python 2.7 from https://www.microsoft.com/en-in/download/details.aspx?id=44266.
Make sure your pip is updated one.


move to ResumeParserApi folder and start django project using command python manage.py runserver 

please find a usage.txt file for the instructions on how to call the apis


Api Usage :

1. Get All parsed data information 
	http://127.0.0.1:8000/ResumeParser/resumeParser

	Type:POST
	x-urlencoded-params Parameters

	"rawtext":"Resume text",
	"uid":"sample.txt", (optional)
	"isBulk":"0" (optional)

	
	output : {JSON of resume parsed}

