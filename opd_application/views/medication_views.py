# from python library
import logging

# from third-party applications
from django.db.transaction import atomic
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, DetailView

# from main application
from opd_application.constants import DASHBOARD_PAGE_NAME, MEDICATION_FORM_TEMPLATE, LOGIN_PAGE_NAME, \
    MEDICATION_EDIT_PAGE_NAME, MEDICATION_PROFILE_TEMPLATE
from opd_application.forms.medication_forms import MedicationForm
from opd_application.messages import CANNOT_DELETE_ALL_FORMS, MINIMUM_REQUIRED_NUMBER_OF_FORMS
from opd_application.models.medication_models import MedicationEntry, Medication
from opd_application.models.patient_models import Patient
from opd_application.functions import log_end_time, log_start_time, log_enter_atomic_trans, log_exit_atomic_trans

logger = logging.getLogger(__name__)


def extract_form_data(initial_formset):
    """
    Returns an array of initial data from formset argument
    :param initial_formset: Dict of formset
    :return:                Array of initial formset data
    """
    log_start_time()

    initial = []

    for form in initial_formset:
        data = {}
        for field in form.fields:
            data[field] = form[field].value()
        initial.append(data)

    log_end_time()
    return initial


class MedicationFormView(FormView):
    """
    View for handling medication record creation. Uses GET function to initially fill the form with patient
    details. POST function handles saving of medication record. Add and Remove capabilities are also added in the POST
    function to update form number.
    """

    form_class = MedicationForm
    template_name = MEDICATION_FORM_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Creates a formset for creating medication entry records for a specified patient. Value for [patient] is taken
        from request URI. If a medication ID is provided in URI, retrieves medication entries from database for update
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        logger.info('Retrieving patient ID from request URI')
        patient_id = request.GET.get('patient')

        logger.info('Retrieving medication record ID from request URI')
        medication_id = kwargs.get('id')

        if patient_id:
            logger.info('Retrieved patient ID value [%s]' % patient_id)
            patient = Patient.objects.get(pk=int(patient_id))

            logger.info('Creating formset with 1 extra form')
            MedicationFormSet = formset_factory(self.form_class)
            formset = MedicationFormSet()

            response = render(request, self.template_name,
                              {'formset': formset, 'patient': patient, 'submit_label': 'Record'})
        elif medication_id:
            logger.info('Retrieved medication record ID value [%s]' % medication_id)
            medication = Medication.objects.get(pk=medication_id)

            logger.info('Retrieving medication entries using medication record ID [%s]' % medication.id)
            medication_entries = MedicationEntry.objects.filter(medication=medication)

            initial = []
            logger.info('Pre-filling formset using medication entry records retrieved from database')
            for entry in medication_entries:
                initial.append({'description': entry.description, 'dosage': entry.dosage, 'package': entry.package,
                                'frequency': entry.frequency, 'designated_time': entry.designated_time})

            logger.info('Creating formset with no additional forms')
            MedicationFormSet = formset_factory(self.form_class, extra=0)
            formset = MedicationFormSet(initial=initial)
            response = render(request, self.template_name,
                              {'formset': formset, 'patient': medication.patient, 'submit_label': 'Record'})
        else:
            logger.warn('Did not receive value for required medical parameter')
            response = redirect(DASHBOARD_PAGE_NAME, permanent=True)

        log_end_time()
        return response

    def post(self, request, *args, **kwargs):
        """
        Validates formset data. Creates a new medication record even for updates then saves medication entry records
        with non-empty description value.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        error_message = None

        logger.info('Retrieving medication ID from POST data')
        medication_id = request.POST.get('medication')

        logger.info('Retrieving patient ID from POST data')
        patient = Patient.objects.get(pk=int(request.POST.get('patient')))

        if medication_id:
            logger.info('Updating medication record')
            submit_label = 'Update'
        else:
            logger.info('Creating new medication record')
            submit_label = 'Record'

        if 'cancel' in request.POST:
            logger.info('User clicked cancel - Redirecting to [%s]' % DASHBOARD_PAGE_NAME)
            response = HttpResponseRedirect(reverse_lazy(DASHBOARD_PAGE_NAME))
        elif 'add' in request.POST:
            logger.info('User clicked add - Creating formset with 1 extra form and delete functionality')
            MedicationFormSet = formset_factory(self.form_class, can_delete=True, extra=1)
            initial_formset = MedicationFormSet(request.POST)

            logger.info('Retrieving form data from POST request for formset pre-fill')

            formset = MedicationFormSet(initial=extract_form_data(initial_formset))
            response = render(request, self.template_name,
                              {'formset': formset, 'patient': patient, 'submit_label': submit_label})
        elif 'delete' in request.POST:
            logger.info('User clicked delete - Removing deleted forms from formset')
            MedicationFormSet = formset_factory(self.form_class, can_delete=True, extra=0)
            initial_formset = MedicationFormSet(request.POST)

            if len(initial_formset.deleted_forms) >= len(initial_formset):
                logger.warn('Number of deleted forms is equal to total number of forms')
                error_message = CANNOT_DELETE_ALL_FORMS
                formset = MedicationFormSet(initial=extract_form_data(initial_formset))
            else:
                logger.info('Removing deleted forms from initial formset')
                initial = []
                for form in initial_formset:
                    data = {}
                    for field in form.fields:
                        data[field] = form[field].value()

                    if not data['DELETE']:
                        logger.info('Form is removed from formset')
                        initial.append(data)
                    else:
                        logger.info('Form is included in formset')

                formset = MedicationFormSet(initial=initial)

            response = render(request, self.template_name,
                              {'formset': formset, 'patient': patient, 'submit_label': submit_label,
                               'error_message': error_message})
        else:
            logger.info('User clicked submit - Validating forms')
            MedicationFormSet = formset_factory(self.form_class, can_delete=True, extra=0)
            formset = MedicationFormSet(request.POST)

            logger.info('Validating formset values')
            if formset.is_valid():
                logger.info('Received valid formset data')
                medication = Medication(patient=patient, recorded_by=request.user,
                                        recorded_date=localtime(now()))
                with atomic():
                    log_enter_atomic_trans()
                    for idx, form in enumerate(formset):
                        if None in form.cleaned_data:
                            pass
                        else:
                            break
                        medication.save()
                        medication_entry = form.save(commit=False)
                        medication_entry.medication = medication
                        medication_entry.save()
                log_exit_atomic_trans()

                if medication.id:
                    logger.info('Redirecting to medication profile page')
                    response = redirect(medication)
                else:
                    logger.info('Did not receive any valid form')
                    error_message = MINIMUM_REQUIRED_NUMBER_OF_FORMS
                    MedicationFormSet = formset_factory(self.form_class)
                    response = render(request, self.template_name,
                                      {'formset': MedicationFormSet(), 'patient': patient, 'submit_label': submit_label,
                                       'error_message': error_message})
            else:
                logger.warn('Received invalid formset data')
                response = render(request, self.template_name,
                                  {'formset': formset, 'patient': patient, 'submit_label': submit_label})

        log_end_time()
        return response

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicationFormView, self).dispatch(request, *args, **kwargs)


class MedicationDetailView(DetailView):
    """
    View for displaying patient's maintenance medication record information. Uses only GET function to display related
    medication entry records for latest medication record entry.
    """

    model = Medication
    template_name = MEDICATION_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Retrieves prescription entry records from database for display
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        logger.info('Retrieving medication id from request URI')
        medication = self.model.objects.get(pk=kwargs.get('id'))
        medication_entries = MedicationEntry.objects.filter(medication=medication)

        log_end_time()

        return render(request, self.template_name,
                      {'medication': medication, 'medication_entries': medication_entries,
                       'max_column_width': -12,
                       'max_cell_width': -6, 'edit_link': reverse_lazy(MEDICATION_EDIT_PAGE_NAME,
                                                                       kwargs={'id': medication.id})})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicationDetailView, self).dispatch(request, *args, **kwargs)
