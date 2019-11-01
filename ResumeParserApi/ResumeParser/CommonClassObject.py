class PersonalDetails(object):

	def __init__(self):
			self.CandidateName=""
			self.Contact1=""
			self.Contact2= ""
			self.EmailId1= ""
			self.EmailId2= ""
			self.DateOfBirth= ""
			self.Gender= ""
			self.Address= ""
			self.City= ""
			self.State= ""
			self.Country= ""
			self.PanNo= ""
			self.PassportNo= ""
			self.ResumeFileType= ""
			self.ResumeInPlainText= ""
			self.SourcingDetails= ""


class SkillsDetails(object):

	def __init__(self):
			self.skillname=""
			self.frequency=""
			self.Skillused = Skillused()

class Skillused(object):
	def __init__(self):
			self.months=0
			self.lastused=""

class QualificationsDetails(object):

	def __init__(self):
			self.HighestQualificationDegree=""
			self.QualificationData = []
	def AddQualificationData(self,d,i,p,u):
			qualfications = QualificationData()
			qualfications.AddQualification(d,i,p,u)
			self.QualificationData.append(qualfications)

class QualificationData(object):

	def __init__(self):			
			self.Degree=""
			self.Institution=""
			self.PassingYear= ""
			self.University = ""
	def AddQualification(self,d,i,p,u):
			self.Degree=d
			self.Institution=i
			self.PassingYear=p
			self.University = u

class  EmployementsHistoryDetails(object):

	def __init__(self):
			self.ExperienceInMonths=""
			self.EmployementHistoryData = []
	def AddEmployementHistoryData(self,org,fromdate,todate,desg,func):
			employement = EmployementHistoryData()
			employement.AddEmployementHistory(org,fromdate,todate,desg,func)
			self.EmployementHistoryData.append(employement)



class  EmployementHistoryData(object):

	def __init__(self):
			self.Organization=""
			self.FromPeriod=""
			self.ToPeriod= ""
			self.Designation=""
			self.FunctionalArea =""
	def AddEmployementHistory(self,org,fromdate,todate,desg,func):
			self.Organization=org
			self.FromPeriod=fromdate
			self.ToPeriod=todate
			self.Designation=desg
			self.FunctionalArea =func