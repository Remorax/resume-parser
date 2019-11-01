from django.http import HttpResponse
from django.http import JsonResponse


def index(request):
    return HttpResponse("Not a valid request")


def GetResumeDetails(request):
	from ResumeAllDetails import getAllResumeDetails
	rawtext = request.POST.get('rawtext', None)
	uid = request.POST.get('uid', "TestResume")
	isBulk = request.POST.get('isBulk', "0")
	msg = False
	if(rawtext):
		data = getAllResumeDetails(rawtext,uid,isBulk)
		msg = True
		return JsonResponse({'status':msg,'data':data})
	return JsonResponse({'status':msg,'msg':'Invalid request'})

