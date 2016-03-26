from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_record_management import settings
from opd_application.constants import *
from opd_application.forms import PatientForm, PatientEditForm
from opd_application.messages import *
from opd_application.models import Patient
from opd_application.views.general_views import GeneralSearchListView


# TODO: Add Python Documentation
# TODO:

class PatientFormView(FormView):
    form_class = PatientForm
    template_name = PATIENT_FORM_TEMPLATE

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

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientFormView, self).dispatch(request, *args, **kwargs)


class PatientSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(PatientSearchListView, self).__init__(Patient, PATIENT_PAGE_ICON, 'Patients',
                                                    reverse_lazy(PATIENT_SEARCH_LIST_PAGE_NAME),
                                                    PATIENT_SEARCH_LIST_TEMPLATE, PATIENT_SEARCH_TYPE_LABEL, **kwargs)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientSearchListView, self).dispatch(request, *args, **kwargs)


class PatientProfileDetailView(DetailView):
    model = Patient
    template_name = PATIENT_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        patient = self.model.objects.get(pk=kwargs.get('id'))
        sex = patient.sex
        marital_status = patient.marital_status
        edit_link = reverse_lazy('opd:edit_profile', kwargs={'id': patient.id})

        print(edit_link)

        for i, s in enumerate(self.model.SEX_CHOICES):
            if s[0] == sex:
                sex = s[1]

        for i, m in enumerate(self.model.MARITAL_CHOICES):
            if m[0] == marital_status:
                marital_status = m[1]

        print(settings.MEDIA_ROOT)

        return render(request, self.template_name,
                      {'patient': patient, 'sex': sex, 'marital_status': marital_status, 'edit_link': edit_link})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientProfileDetailView, self).dispatch(request, *args, **kwargs)


class PatientEditFormView(FormView):
    form_class = PatientEditForm
    template_name = PATIENT_FORM_TEMPLATE

    def get(self, request, *args, **kwargs):
        patient = Patient.objects.get(pk=kwargs.get('id'))
        form = self.form_class(instance=patient)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.form_class(request.POST, request.FILES, instance=Patient.objects.get(pk=kwargs.get('id')))
        if form.is_valid():
            patient = form.save(commit=False)
            patient.last_updated_by = request.user
            patient.last_updated = localtime(now())
            patient.save()

            return redirect(patient)
        else:
            context.update({'form': form})

            return render(request, self.template_name, context)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PatientEditFormView, self).dispatch(request, *args, **kwargs)
