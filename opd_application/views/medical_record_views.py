import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.constants import *
from opd_application.forms.medical_record_forms import MedicalRecordForm, MedicalRecordEditForm
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.models.physical_exam_models import PhysicalExam
from opd_application.models.models import Patient
from opd_application.models.prescription_models import Prescription
from opd_application.models.diagnosis_models import Diagnosis
from opd_application.models.laboratory_models import Laboratory
from opd_application.views.general_views import GeneralSearchListView, GeneralListView

logger = logging.getLogger(__name__)


class MedicalRecordFormView(FormView):
    form_class = MedicalRecordForm
    template_name = MEDICAL_RECORD_FORM_TEMPLATE

    def get(self, request, *args, **kwargs):
        if request.GET.get('patient'):
            patient = Patient.objects.get(pk=request.GET.get('patient'))
            form = self.form_class(initial={'patient_name': patient, 'patient': patient.id})

            return render(request, self.template_name, {'form': form})
        else:
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.form_class(data=request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.recorded_date = localtime(now())
            record.save()
            form.save_m2m()

            return redirect(record)
        else:
            context.update({'form': form})

        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordFormView, self).dispatch(request, *args, **kwargs)


class MedicalRecordDetailView(DetailView):
    model = MedicalRecord
    template_name = MEDICAL_RECORD_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        medical_record = self.model.objects.get(pk=kwargs.get('id'))
        edit_link = reverse_lazy('opd:edit_medical', kwargs={'id': medical_record.id})
        physical_exam_count = PhysicalExam.objects.filter(medical_record=medical_record).count()
        laboratory_count = Laboratory.objects.filter(medical_record=medical_record).count()
        diagnosis_count = Diagnosis.objects.filter(medical_record=medical_record).count()
        prescription_count = Prescription.objects.filter(medical_record=medical_record).count()

        return render(request, self.template_name,
                      {'medical_record': medical_record, 'complaints': medical_record.complaint.all(),
                       'physical_exam_count': physical_exam_count, 'laboratory_count': laboratory_count,
                       'diagnosis_count': diagnosis_count, 'prescription_count': prescription_count,
                       'edit_link': edit_link})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordDetailView, self).dispatch(request, *args, **kwargs)


class MedicalRecordListView(GeneralListView):
    """
    View for displaying all patient's physical exam record information for a specific medical record. Uses only GET
    function to display all physical exam records for chosen medical record. Extends GeneralListView.
    """

    def __init__(self):
        logger.info('Instantiating GenaralListView super class')
        super(MedicalRecordListView, self).__init__(model=MedicalRecord,
                                                    template_name=MEDICAL_RECORD_LIST_TEMPLATE,
                                                    add_page_name=MEDICAL_RECORD_FORM_PAGE_NAME,
                                                    left_link_page_name=None,
                                                    left_link_name=None,
                                                    left_link_icon=None,
                                                    right_link_page_name=None,
                                                    right_link_name=None,
                                                    right_link_icon=None,
                                                    page_icon=MEDICAL_RECORD_PAGE_ICON,
                                                    page_title='Medical Record Results',
                                                    list_page_name=MEDICAL_RECORD_LIST_PAGE_NAME)


class MedicalRecordSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(MedicalRecordSearchListView, self).__init__(MedicalRecord, MEDICAL_RECORD_PAGE_ICON,
                                                          'Medical Records',
                                                          MEDICAL_RECORD_SEARCH_LIST_PAGE_NAME,
                                                          MEDICAL_RECORD_SEARCH_LIST_TEMPLATE,
                                                          GENERAL_SEARCH_TYPE_LABEL,
                                                          **kwargs)


class MedicalRecordEditFormView(FormView):
    form_class = MedicalRecordEditForm
    template_name = MEDICAL_RECORD_FORM_TEMPLATE

    def get(self, request, *args, **kwargs):
        medical_record = MedicalRecord.objects.get(pk=kwargs.get('id'))
        form = self.form_class(initial={'patient_name': medical_record.patient}, instance=medical_record)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        context = {}
        medical_record = MedicalRecord.objects.get(pk=kwargs.get('id'))
        form = self.form_class(data=request.POST, instance=medical_record)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.recorded_date = localtime(now())
            record.save()
            form.save_m2m()

            return redirect(record)
        else:
            context.update({'form': form})

        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordEditFormView, self).dispatch(request, *args, **kwargs)
