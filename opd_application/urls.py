"""authentication URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include

from opd_application.views import patient_views, dashboard_views, medical_record_views, physical_exam_views

urlpatterns = [
    url(r'^home/$', dashboard_views.DashboardView.as_view(), name='home'),

    url(r'^record_patient/$', patient_views.PatientFormView.as_view(), name='record_patient'),
    url(r'^record_exam/$', physical_exam_views.PhysicalExamFormView.as_view(), name='record_exam'),
    url(r'^record_medical/$', medical_record_views.MedicalRecordFormView.as_view(), name='record_medical'),

    url(r'^search_patient/$', patient_views.PatientSearchListView.as_view(), name='search_patient'),
    url(r'^search_exam/$', physical_exam_views.PhysicalExamSearchListView.as_view(), name='search_exam'),
    url(r'^search_medical/$', medical_record_views.MedicalRecordSearchListView.as_view(), name='search_medical'),

    url(r'^profile/(?P<id>[0-9]+)/$', patient_views.PatientProfileDetailView.as_view(), name='profile'),
    url(r'^medical/(?P<id>[0-9]+)/$', medical_record_views.MedicalRecordDetailView.as_view(), name='medical'),
    url(r'^exam/(?P<id>[0-9]+)/$', physical_exam_views.PhysicalExamDetailView.as_view(), name='exam'),

    url(r'^list_exam/$', physical_exam_views.PhysicalExamListView.as_view(), name='list_exam'),
    url(r'^list_medical/$', medical_record_views.MedicalRecordListView.as_view(), name='list_medical'),

    url(r'^edit_profile/(?P<id>[0-9]+)/$', patient_views.PatientEditFormView.as_view(), name='edit_profile'),
    url(r'^edit_medical/(?P<id>[0-9]+)/$', medical_record_views.MedicalRecordEditFormView.as_view(),
        name='edit_medical'),
    url(r'^edit_exam/(?P<id>[0-9]+)/$', physical_exam_views.PhysicalExamEditFormView.as_view(),
        name='edit_exam'),

]
