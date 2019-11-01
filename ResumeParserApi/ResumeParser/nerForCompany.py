# -*- coding: utf-8 -*-
import urllib.request
from urllib.request import urlopen
from urllib.error import HTTPError
import json 

def OrgNER(txt):
    data =  {

            "Inputs": {

                    "input1":
                    {
                        "ColumnNames": ["data"],
                        "Values": [ [ txt ], ]
                    },        },
                "GlobalParameters": {
    }
        }

    body = str.encode(json.dumps(data))
    url = 'https://ussouthcentral.services.azureml.net/workspaces/9d7395bb7ae74ed880ca99d94c56b911/services/96426d2e3d554c21a8415d87af792d3d/execute?api-version=2.0'
    api_key = 'abc123' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ 'FE5R2ATZTdoGQod3/voqp9emocYSfpwPrWMEyNqitXsDu9ZsGshnmLvXZBhwP9013WfQMu2VOOuSlKZWunbLvw==')}

    req = urllib.request.Request(url, body, headers) 

    try:
        response = urlopen(req)
        result = response.read()
        # print(str(result))
        data = json.loads(str(result.decode("utf-8")))
        return data["Results"]['output1']['value']['Values'] 
    except (HTTPError):
        print("The request failed with status code: " + str(HTTPError.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(HTTPError.info())

        print(json.loads(HTTPError.read()))
        return []


# data = OrgNER("""PROFESSIONAL EXPERIENCE
# PMAM IT Services Pvt. Ltd.                                      Mumbai
# Technology Specialist                                      January 2014 – Present

# SureQuest Food Service Management Software.
# Collaborated on a team of 6 to investigate their US client’s existing OnDemand Dining Management software system in order to develop a framework for process integration to support the company’s new globalization initiative.
# Designed using Asp.Net 3.5 C# framework and SQL Server 2012 as backend in an agile environment.
# Overhauled web forms to feature global languages with ongoing enhancements.
# Utilized Google translator API for translation of existing data to new foreign language.
# Remodeled underlying databases to streamline other foreign languages with English.
# Resolved problems of production by working with customer support.

# PMAM Smart Select.
# A complete recruitment and staffing solution that allows recruiters to design tests for candidates applying for specialized skills required for the job.
# Worked with a team of 4 developed using pure HTML with JQuery, JSON, Ajax with Web API C# & SQL Server 2014.
# Primarily designed Certification and Job Posting module of the application.

# SYSCON Infotech Pvt. Ltd.                                       Mumbai Software Programmer                                February 2011 – December 2013
# Logistic Software Solution.
# Responsibility included engineering and assisting project lead in managing team of 10 in implementing company’s Logistics Software Solution across various shipping and freight forwarders clients.
# Developed using Asp.Net 3.5 VB JavaScript, SQL Server 2008 with Crystal Reports.
# Actively participated with the business development team in requirement analysis and customized the application to advance clients business processes.
# Designed database driven components that significantly reduced application development time and cost.
# Responsible for knowledge transfer and mentoring new team members.
# Provided on-call support to ensure our clients felt well attended.

# Ambrose Technologies Pvt. Ltd.                                  Mumbai Software Programmer                                      June 2007 – December 2010

# Easy Button EMR.
# Independently programmed and implemented client’s desktop application in order to automate business communication process for specialty doctor/patients.
# Built using Windows Forms C#, SQL Server 2005, Crystal Report 8 with Infragistics controls for GUI.
# Formalized procedures and methodology to decrease redundant development.
# Tested and delivered several key modules like patient/doctor check in, vital sign, visit notes, document management, diagnosis and appointment scheduling for the client to introduce the application in live environment.""")




# print data  