from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.constants import *
from opd_application.forms import PatientSearchForm, PatientForm
from opd_application.messages import *
from opd_application.models import Patient
from opd_application.views.views import GeneralSearchListView, PATIENT_SEARCH_LABEL


class PatientFormView(FormView):
    form_class = PatientForm
    template_name = 'patient_form.html'

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.form_class(data=request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.creation_date = localtime(now())
            patient.save()

            return redirect(patient)
        else:
            context.update({'form': form})

            return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientFormView, self).dispatch(request, *args, **kwargs)


class PatientSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(PatientSearchListView, self).__init__(Patient, 'fa-user', 'Patients', reverse_lazy('opd:search_patient'),
                                                    'patient_list.html', PATIENT_SEARCH_LABEL, **kwargs)

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientSearchListView, self).dispatch(request, *args, **kwargs)


class OldPatientSearchListView(ListView):
    model = Patient
    template_name = 'patient_list.html'

    search_type = ''
    search_param = ''
    current_page = 1
    patient_matches = []

    link = ''
    next_link = ''
    next_link_class = ''
    previous_link = ''
    previous_link_class = ''

    query_string = {
        '1': model.objects.filter(last_name__icontains=search_param),
        '2': model.objects.filter(first_name__icontains=search_param),
        '3': model.objects.filter(birth_date__iexact=search_param),
    }

    def return_values(self, request):
        return render(request, self.template_name,
                      {'form': PatientSearchForm(
                          initial={'search_type': self.search_type,
                                   'search_param': self.search_param}),
                          'patient_matches': self.patient_matches[0:MAX_LIST_ITEMS_PER_PAGE],
                          'label': PATIENT_SEARCH_LABEL.get(self.search_type),
                          'search_label': PATIENT_SEARCH_LABEL,
                          'page_title': 'Patient Records',
                          'page_icon': 'fa-user',
                          'add_link': reverse_lazy('opd:record_patient'),
                          'current_page': self.current_page,
                          'next_link': self.next_link,
                          'next_link_class': self.next_link_class,
                          'previous_link': self.previous_link,
                          'previous_link_class': self.previous_link_class,
                      })

    def process_search(self):
        self.link = reverse_lazy(
            'opd:search_patient') + '?search_param=' + self.search_param + '&search_type=' + self.search_type + '&current='

        # check if there are still records to show
        if len(self.patient_matches) > MAX_LIST_ITEMS_PER_PAGE:
            self.next_link = self.link + str(self.current_page + 1)
            self.next_link_class = ''
        else:
            self.next_link = ''
            self.next_link_class = 'disabled'

        # check to see if there are previous records to show
        if self.current_page <= 1:
            self.previous_link = ''
            self.previous_link_class = 'disabled'
        else:
            self.previous_link = self.link + str(self.current_page - 1)
            self.previous_link_class = ''

    def get(self, request, *args, **kwargs):
        if request.GET.get('search_param') and request.GET.get('search_type'):
            self.search_type = request.GET.get('search_type')
            self.search_param = request.GET.get('search_param')

            if request.GET.get('current'):
                self.current_page = int(request.GET.get('current'))
                added_offset = MAX_LIST_ITEMS_PER_PAGE * (self.current_page - 1)
            else:
                self.current_page = 1
                added_offset = 0

            self.patient_matches = self.query_string.get(self.search_type)[
                                   0 + added_offset:MAX_LIST_ITEMS_PER_PAGE + added_offset + 1]

            self.process_search()

            return self.return_values(request)
        else:
            return redirect('opd:home', permanent=True)

    def post(self, request, *args, **kwargs):
        form = PatientSearchForm(data=request.POST)

        if form.is_valid():
            self.current_page = 1
            self.search_type = form.cleaned_data['search_type']
            self.search_param = form.cleaned_data['search_param']

            limit = MAX_LIST_ITEMS_PER_PAGE + 1

            if self.search_param:
                self.patient_matches = self.query_string.get(self.search_type)[0:limit]
            else:
                self.patient_matches = self.model.objects.all().order_by('last_name')[0:limit]

            self.process_search()

            return self.return_values(request)
        else:
            return redirect('opd:home', permanent=True)

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(OldPatientSearchListView, self).dispatch(request, *args, **kwargs)


class PatientProfileDetailView(DetailView):
    model = Patient
    template_name = 'patient_profile.html'

    def get(self, request, *args, **kwargs):
        patient = self.model.objects.get(pk=kwargs.get('id'))
        sex = patient.sex
        marital_status = patient.marital_status

        for i, s in enumerate(self.model.SEX_CHOICES):
            if s[0] == sex:
                sex = s[1]

        for i, m in enumerate(self.model.MARITAL_CHOICES):
            if m[0] == marital_status:
                marital_status = m[1]

        return render(request, self.template_name, {'patient': patient, 'sex': sex, 'marital_status': marital_status})

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientProfileDetailView, self).dispatch(request, *args, **kwargs)
