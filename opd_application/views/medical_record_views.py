from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.constants import *
from opd_application.forms import MedicalRecordForm, GeneralSearchForm
from opd_application.models import MedicalRecord, PhysicalExam, Laboratory, Diagnosis, Prescription, Patient
from opd_application.views.views import GeneralSearchListView


class MedicalRecordFormView(FormView):
    form_class = MedicalRecordForm
    template_name = 'medical_record_form.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('patient'):
            patient = Patient.objects.get(pk=request.GET.get('patient'))
            form = self.form_class(initial={'patient_name': patient, 'patient': patient.id})

            return render(request, self.template_name, {'form': form})
        else:
            return redirect('opd:home', permanent=True)

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

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordFormView, self).dispatch(request, *args, **kwargs)


class MedicalRecordDetailView(DetailView):
    model = MedicalRecord
    template_name = 'medical_record_profile.html'

    def get(self, request, *args, **kwargs):
        medical_record = self.model.objects.get(pk=kwargs.get('id'))
        physical_exam_count = PhysicalExam.objects.filter(medical_record=medical_record).count()
        laboratory_count = Laboratory.objects.filter(medical_record=medical_record).count()
        diagnosis_count = Diagnosis.objects.filter(medical_record=medical_record).count()
        prescription_count = Prescription.objects.filter(medical_record=medical_record).count()

        return render(request, self.template_name,
                      {'medical_record': medical_record, 'complaints': medical_record.complaint.all(),
                       'physical_exam_count': physical_exam_count, 'laboratory_count': laboratory_count,
                       'diagnosis_count': diagnosis_count, 'prescription_count': prescription_count})

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordDetailView, self).dispatch(request, *args, **kwargs)


class MedicalRecordListView(ListView):
    model = MedicalRecord
    template_name = 'medical_record_list.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('patient'):
            patient = Patient.objects.get(pk=request.GET.get('patient'))

            if request.GET.get('current'):
                current_page = int(request.GET.get('current'))
                added_offset = MAX_LIST_ITEMS_PER_PAGE * (current_page - 1)
            else:
                current_page = 1
                added_offset = 0

            medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-recorded_date')[
                              0 + added_offset:MAX_LIST_ITEMS_PER_PAGE + added_offset + 1]

            link = reverse_lazy('opd:list_medical') + '?patient=' + str(patient.id) + '&current='

            # check if there are still records to show
            if medical_records.count() > MAX_LIST_ITEMS_PER_PAGE:
                next_link = link + str(current_page + 1)
                next_link_class = ''
            else:
                next_link = ''
                next_link_class = 'disabled'

            # check to see if there are previous records to show
            if current_page <= 1:
                previous_link = ''
                previous_link_class = 'disabled'
            else:
                previous_link = link + str(current_page - 1)
                previous_link_class = ''

            return render(request, self.template_name,
                          {'medical_records': medical_records[0:MAX_LIST_ITEMS_PER_PAGE],
                           'patient': patient,
                           'left_link': patient.get_absolute_url(),
                           'left_link_icon': 'fa fa-user fa-1x',
                           'left_link_name': 'Patient Profile',
                           'right_link': '',
                           'right_link_icon': 'fa fa-history fa-1x',
                           'right_link_name': 'Patient History',
                           'page_title': 'Medical Records',
                           'page_icon': 'fa-list-alt',
                           'add_link': reverse_lazy('opd:record_medical') + '?patient=' + str(patient.id),
                           'current_page': current_page,
                           'next_link': next_link,
                           'next_link_class': next_link_class,
                           'previous_link': previous_link,
                           'previous_link_class': previous_link_class,
                           })
        else:
            return redirect('opd:home', permanent=True)

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordListView, self).dispatch(request, *args, **kwargs)


class MedicalRecordSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(MedicalRecordSearchListView, self).__init__(MedicalRecord, 'fa-list-alt', 'Medical Records',
                                                          reverse_lazy('opd:search_medical'),
                                                          'medical_record_search_list.html', **kwargs)

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalRecordSearchListView, self).dispatch(request, *args, **kwargs)
