from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.constants import *
from opd_application.forms import MedicalRecordForm, MedicalRecordEditForm
from opd_application.models import MedicalRecord, PhysicalExam, Laboratory, Diagnosis, Prescription, Patient
from opd_application.views.general_views import GeneralSearchListView, calculate_offset, modify_page_links, \
    validate_response


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


class MedicalRecordListView(ListView):
    model = MedicalRecord
    template_name = MEDICAL_RECORD_LIST_TEMPLATE

    pages = []
    searches = []
    current_page = 1
    search_link = ''
    search_count = 0
    error_message = ''

    next_link = ''
    next_link_class = ''
    previous_link = ''
    previous_link_class = ''

    def get(self, request, *args, **kwargs):
        if request.GET.get('patient'):
            patient = Patient.objects.get(pk=request.GET.get('patient'))

            added_offset = calculate_offset(self, request)

            query_set = MedicalRecord.objects.filter(patient=patient).order_by('-recorded_date')

            self.search_count = query_set.count()
            self.searches = query_set[0 + added_offset:MAX_LIST_ITEMS_PER_PAGE + added_offset + 1]
            self.search_link = reverse_lazy(MEDICAL_RECORD_LIST_PAGE_NAME) + '?patient=' + str(
                patient.id) + '&current='

            modify_page_links(self)
            validate_response(self)

            return render(request, self.template_name,
                          {'searches': self.searches[0:MAX_LIST_ITEMS_PER_PAGE],
                           'patient': patient,
                           'pages': self.pages,
                           'error_message': self.error_message,
                           'search_link': self.search_link,
                           'left_link': patient.get_absolute_url(),
                           'left_link_icon': PATIENT_PAGE_ICON,
                           'left_link_name': 'Patient Profile',
                           'right_link': '',
                           'right_link_icon': MEDICAL_HISTORY_PAGE_ICON,
                           'right_link_name': 'Patient History',
                           'page_title': 'Medical Records',
                           'page_icon': MEDICAL_RECORD_PAGE_ICON,
                           'add_link': reverse_lazy(MEDICAL_RECORD_FORM_PAGE_NAME) + '?patient=' + str(patient.id),
                           'current_page': self.current_page,
                           'next_link': self.next_link,
                           'next_link_class': self.next_link_class,
                           'previous_link': self.previous_link,
                           'previous_link_class': self.previous_link_class,
                           })
        else:
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordListView, self).dispatch(request, *args, **kwargs)


class MedicalRecordSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(MedicalRecordSearchListView, self).__init__(MedicalRecord, MEDICAL_RECORD_PAGE_ICON,
                                                          'Medical Records',
                                                          reverse_lazy(MEDICAL_RECORD_SEARCH_LIST_PAGE_NAME),
                                                          MEDICAL_RECORD_SEARCH_LIST_TEMPLATE,
                                                          GENERAL_SEARCH_TYPE_LABEL,
                                                          **kwargs)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordSearchListView, self).dispatch(request, *args, **kwargs)


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
