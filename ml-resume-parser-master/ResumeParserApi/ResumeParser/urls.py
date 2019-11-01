from django.conf.urls import url

from . import views

app_name = 'ResumeParser'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^resumeParser$', views.GetResumeDetails, name='GetResumeDetails'),
]