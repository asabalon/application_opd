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
from django.conf.urls import url

from opd_application.views import patient_views, dashboard_views, medical_record_views, physical_exam_views, \
    medical_history_views, laboratory_views, diagnosis_views, prescription_views, medication_views

urlpatterns = [
    url(r'^home/$', dashboard_views.DashboardView.as_view(), name='home'),

    url(r'^record_patient/$', patient_views.PatientFormView.as_view(), name='record_patient'),
    url(r'^record_exam/$', physical_exam_views.PhysicalExamFormView.as_view(), name='record_exam'),
    url(r'^record_medical/$', medical_record_views.MedicalRecordFormView.as_view(), name='record_medical'),
    url(r'^record_history/$', medical_history_views.MedicalHistoryFormView.as_view(), name='record_history'),
    url(r'^record_laboratory/$', laboratory_views.LaboratoryFormView.as_view(), name='record_laboratory'),
    url(r'^record_diagnosis/$', diagnosis_views.DiagnosisFormView.as_view(), name='record_diagnosis'),
    url(r'^record_prescription/$', prescription_views.PrescriptionFormView.as_view(), name='record_prescription'),
    url(r'^record_medication/$', medication_views.MedicationFormView.as_view(), name='record_medication'),

    url(r'^search_patient/$', patient_views.PatientSearchListView.as_view(), name='search_patient'),
    url(r'^search_exam/$', physical_exam_views.PhysicalExamSearchListView.as_view(), name='search_exam'),
    url(r'^search_medical/$', medical_record_views.MedicalRecordSearchListView.as_view(), name='search_medical'),
    url(r'^search_diagnosis/$', diagnosis_views.DiagnosisSearchListView.as_view(), name='search_diagnosis'),
    url(r'^search_laboratory/$', laboratory_views.LaboratorySearchListView.as_view(), name='search_laboratory'),
    url(r'^search_prescription/$', prescription_views.PrescriptionSearchListView.as_view(), name='search_prescription'),

    url(r'^profile/(?P<id>[0-9]+)/$', patient_views.PatientProfileDetailView.as_view(), name='profile'),
    url(r'^medical/(?P<id>[0-9]+)/$', medical_record_views.MedicalRecordDetailView.as_view(), name='medical'),
    url(r'^exam/(?P<id>[0-9]+)/$', physical_exam_views.PhysicalExamDetailView.as_view(), name='exam'),
    url(r'^history/(?P<id>[0-9]+)/$', medical_history_views.MedicalHistoryDetailView.as_view(), name='history'),
    url(r'^laboratory/(?P<id>[0-9]+)/$', laboratory_views.LaboratoryDetailView.as_view(), name='laboratory'),
    url(r'^diagnosis/(?P<id>[0-9]+)/$', diagnosis_views.DiagnosisDetailView.as_view(), name='diagnosis'),
    url(r'^prescription/(?P<id>[0-9]+)/$', prescription_views.PrescriptionDetailView.as_view(), name='prescription'),
    url(r'^medication/(?P<id>[0-9]+)/$', medication_views.MedicationDetailView.as_view(), name='medication'),

    url(r'^list_exam/$', physical_exam_views.PhysicalExamListView.as_view(), name='list_exam'),
    url(r'^list_medical/$', medical_record_views.MedicalRecordListView.as_view(), name='list_medical'),
    url(r'^list_laboratory/$', laboratory_views.LaboratoryListView.as_view(), name='list_laboratory'),
    url(r'^list_diagnosis/$', diagnosis_views.DiagnosisListView.as_view(), name='list_diagnosis'),
    url(r'^list_prescription/$', prescription_views.PrescriptionListView.as_view(), name='list_prescription'),
    url(r'^list_lab_test/$', laboratory_views.LaboratoryTestDetailView.as_view(), name='list_lab_test'),

    url(r'^edit_profile/(?P<id>[0-9]+)/$', patient_views.PatientEditFormView.as_view(), name='edit_profile'),
    url(r'^edit_medical/(?P<id>[0-9]+)/$', medical_record_views.MedicalRecordEditFormView.as_view(),
        name='edit_medical'),
    url(r'^edit_exam/(?P<id>[0-9]+)/$', physical_exam_views.PhysicalExamEditFormView.as_view(),
        name='edit_exam'),
    url(r'^edit_history/(?P<id>[0-9]+)/$', medical_history_views.MedicalHistoryFormView.as_view(),
        name='edit_history'),
    url(r'^edit_diagnosis/(?P<id>[0-9]+)/$', diagnosis_views.DiagnosisFormView.as_view(),
        name='edit_diagnosis'),
    url(r'^edit_prescription/(?P<id>[0-9]+)/$', prescription_views.PrescriptionFormView.as_view(),
        name='edit_prescription'),
    url(r'^edit_medication/(?P<id>[0-9]+)/$', medication_views.MedicationFormView.as_view(),
        name='edit_medication'),
    url(r'^edit_laboratory/(?P<id>[0-9]+)/$', laboratory_views.LaboratoryFormView.as_view(),
        name='edit_laboratory'),

]
