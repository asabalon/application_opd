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
from opd_application.constants import DASHBOARD_PAGE_NAME, PRESCRIPTION_FORM_TEMPLATE, LOGIN_PAGE_NAME, \
    PRESCRIPTION_PROFILE_TEMPLATE, PRESCRIPTION_EDIT_PAGE_NAME, PRESCRIPTION_LIST_TEMPLATE, DIAGNOSIS_FORM_PAGE_NAME, \
    DIAGNOSIS_PAGE_ICON, PHYSICAL_EXAM_LIST_PAGE_NAME, PRESCRIPTION_LIST_PAGE_NAME, PHYSICAL_EXAM_PAGE_ICON, \
    PRESCRIPTION_PAGE_ICON, DIAGNOSIS_LIST_PAGE_NAME, GENERAL_SEARCH_TYPE_LABEL, PRESCRIPTION_SEARCH_PAGE_NAME, \
    PRESCRIPTION_SEARCH_LIST_TEMPLATE
from opd_application.forms.prescription_forms import PrescriptionEntryForm
from opd_application.models.prescription_models import Medicine, Prescription, PrescriptionEntry
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.functions import log_end_time, log_start_time, log_enter_atomic_trans, log_exit_atomic_trans
from opd_application.views.general_views import GeneralListView, GeneralSearchListView

logger = logging.getLogger(__name__)


class PrescriptionFormView(FormView):
    """
    View for handling prescription entry creation. Uses GET function to initially fill the form with patient
    details. POST function handles saving of prescription entries record using a prescription record.
    """

    form_class = PrescriptionEntryForm
    template_name = PRESCRIPTION_FORM_TEMPLATE

    medicine_count = Medicine.objects.count()
    PrescriptionFormSet = formset_factory(form_class, max_num=medicine_count)

    def get(self, request, *args, **kwargs):
        """
        Retrieves medicine records from database then creates a formset depending on the number of retrieved rows. Pre-
        fills patient field using relationship between retrieved value of [medical] argument from URI
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        initial = []

        logger.info('Retrieving medicine records for form creation')
        medicines = Medicine.objects.all()

        logger.info('Retrieving medical record ID from request URI')
        medical_record_id = request.GET.get('medical')

        logger.info('Retrieving prescription record ID from request URI')
        prescription_id = kwargs.get('id')

        if medical_record_id:
            logger.info('Retrieved medical record ID value [%s]' % medical_record_id)
            medical_record = MedicalRecord.objects.get(pk=medical_record_id)

            logger.info('Creating initial medicine and medicine_label for each form in formset')
            for medicine in medicines:
                initial.append({'medicine': medicine, 'medicine_label': medicine})

            formset = self.PrescriptionFormSet(initial=initial)

            response = render(request, self.template_name,
                              {'formset': formset, 'medical_record': medical_record, 'submit_label': 'Record'})
        elif prescription_id:
            logger.info('Retrieved prescription record ID value [%s]' % prescription_id)
            prescription = Prescription.objects.get(pk=prescription_id)

            logger.info('Creating')
            for medicine in medicines:
                prescription_entry = PrescriptionEntry.objects.filter(prescription=prescription, medicine=medicine,
                                                                      is_deleted=False)

                if prescription_entry.count() > 1:
                    logger.warn('Prescription entry count is greater than expected for medicine [%s]' % medicine)
                    logger.info('Defaulting to first retrieved item')
                    initial.append({'medicine': prescription_entry.first().medicine,
                                    'medicine_label': prescription_entry.first().medicine,
                                    'dosage': prescription_entry.first().dosage,
                                    'package': prescription_entry.first().package,
                                    'frequency': prescription_entry.first().frequency,
                                    'designated_time': prescription_entry.first().designated_time,
                                    'prescribe': True, })
                elif prescription_entry.count() < 1:
                    logger.info('No related prescription entry for medicine [%s]' % medicine)
                    initial.append({'medicine': medicine,
                                    'medicine_label': medicine, })
                else:
                    logger.info('Successful prescription entry retrieval for medicine [%s]' % medicine)
                    initial.append({'medicine': prescription_entry.last().medicine,
                                    'medicine_label': prescription_entry.last().medicine,
                                    'dosage': prescription_entry.last().dosage,
                                    'package': prescription_entry.last().package,
                                    'frequency': prescription_entry.last().frequency,
                                    'designated_time': prescription_entry.last().designated_time,
                                    'prescribe': True, })

            formset = self.PrescriptionFormSet(initial=initial)

            response = render(request, self.template_name,
                              {'formset': formset, 'medical_record': prescription.medical_record,
                               'submit_label': 'Update', 'prescription': prescription})
        else:
            logger.warn('Did not receive value for required medical parameter')
            response = redirect(DASHBOARD_PAGE_NAME, permanent=True)

        log_end_time()
        return response

    def post(self, request, *args, **kwargs):
        """
        Validates formset data. Creates a new prescription record then saves prescription entry records with
        prescribe value set to True.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        if 'cancel' in request.POST:
            logger.info('User clicked cancel')
            return HttpResponseRedirect(reverse_lazy(DASHBOARD_PAGE_NAME))
        else:
            logger.info('User clicked submit')

        logger.info('Retrieving POST data')
        formset = self.PrescriptionFormSet(request.POST)
        prescription_id = request.POST.get('prescription')
        medical_record = MedicalRecord.objects.get(pk=int(request.POST.get('medical_record')))

        logger.info('Validating formset values')
        if formset.is_valid():
            logger.info('Received valid formset data')

            if prescription_id:
                logger.info('Retrieved prescription record as foreign key for prescription entry records')
                prescription = Prescription.objects.get(pk=prescription_id)
            else:
                logger.info('Created prescription record as foreign key for prescription entry records')
                prescription = Prescription(medical_record=medical_record, recorded_by=request.user,
                                            recorded_date=localtime(now()))

            with atomic():
                log_enter_atomic_trans()
                for idx, form in enumerate(formset):
                    data = form.cleaned_data
                    if prescription_id:
                        logger.info(
                            'Retrieving latest prescription entry for prescription record [%s] and medicine [%s]' % (
                                prescription_id, form.instance.medicine))
                        prescription_entry = PrescriptionEntry.objects.filter(prescription=prescription,
                                                                              medicine=form.instance.medicine,
                                                                              is_deleted=False).order_by(
                            '-id').first()
                    else:
                        logger.info(
                            'Creating latest prescription entry for prescription record [%s] and medicine category [%s]' % (
                                prescription_id, form.instance.medicine))
                        prescription_entry = form.save(commit=False)

                    if prescription_entry:
                        if prescription_id and data['prescribe']:
                            logger.info('Updating details of prescription entry')
                            prescription_entry.dosage = form.instance.dosage
                            prescription_entry.package = form.instance.package
                            prescription_entry.frequency = form.instance.frequency
                            prescription_entry.designated_time = form.instance.designated_time
                        elif prescription_id and not data['prescribe']:
                            logger.info('Removing details of prescription entry')
                            prescription_entry.is_deleted = True
                        elif data['prescribe']:
                            logger.info('Saving details of new prescription entry')
                            prescription.save()
                            prescription_entry.prescription = prescription
                        else:
                            logger.info('Skipping prescription entry for [%s]' % form.instance.medicine)
                            continue
                    else:
                        logger.warn('No value for prescription_entry variable. Using value from form')
                        if data['prescribe']:
                            prescription.save()
                            prescription_entry = form.save(commit=False)
                            prescription_entry.prescription = prescription
                        else:
                            logger.info('Skipping prescription entry for [%s]' % form.instance.medicine)
                            continue

                    prescription_entry.updated_by = request.user
                    prescription_entry.updated_date = localtime(now())
                    prescription_entry.save()

            log_exit_atomic_trans()

            logger.info('Redirecting to prescription profile page')
            response = redirect(prescription)
        else:
            logger.warn('Received invalid formset data')
            response = render(request, self.template_name, {'formset': formset, 'medical_record': medical_record})

        log_end_time()
        return response

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PrescriptionFormView, self).dispatch(request, *args, **kwargs)


class PrescriptionDetailView(DetailView):
    """
    View for displaying patient's prescription record information for a specific medical record. Uses only GET function
    to display related prescription entry records for every medicine.
    """

    model = Prescription
    template_name = PRESCRIPTION_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Retrieves prescription entry records from database for display
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        logger.info('Retrieving prescription id from request URI')
        prescription = self.model.objects.get(pk=kwargs.get('id'))
        prescription_entries = PrescriptionEntry.objects.filter(prescription=prescription, is_deleted=False).order_by(
            'medicine__order')

        log_end_time()

        return render(request, self.template_name,
                      {'prescription': prescription, 'prescription_entries': prescription_entries,
                       'max_column_width': -12,
                       'max_cell_width': -6, 'edit_link': reverse_lazy(PRESCRIPTION_EDIT_PAGE_NAME,
                                                                       kwargs={'id': prescription.id})})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PrescriptionDetailView, self).dispatch(request, *args, **kwargs)


class PrescriptionListView(GeneralListView):
    """
    View for displaying all patient's prescription record information for a specific medical record. Uses only GET
    function to display all prescription records for chosen medical record. Extends GeneralListView.
    """

    def __init__(self):
        logger.info('Instantiating GeneralListView super class')
        super(PrescriptionListView, self).__init__(model=Prescription,
                                                   template_name=PRESCRIPTION_LIST_TEMPLATE,
                                                   add_page_name=DIAGNOSIS_FORM_PAGE_NAME,
                                                   left_link_page_name=DIAGNOSIS_LIST_PAGE_NAME,
                                                   left_link_name='Diagnoses',
                                                   left_link_icon=DIAGNOSIS_PAGE_ICON,
                                                   right_link_page_name=PHYSICAL_EXAM_LIST_PAGE_NAME,
                                                   right_link_name='Physical Exam Results',
                                                   right_link_icon=PHYSICAL_EXAM_PAGE_ICON,
                                                   page_icon=PRESCRIPTION_PAGE_ICON,
                                                   page_title='Prescriptions',
                                                   list_page_name=PRESCRIPTION_LIST_PAGE_NAME)


class PrescriptionSearchListView(GeneralSearchListView):
    """
    View for displaying all prescription record information for a specific search query. Uses POST
    function to display initial prescription records search results. GET function is used to display results for a given
    page number. Extends GeneralSearchListView.
    """

    def __init__(self, **kwargs):
        logger.info('Instantiating GeneralSearchListView super class')
        super(PrescriptionSearchListView, self).__init__(Prescription, PRESCRIPTION_PAGE_ICON, 'Prescriptions',
                                                         PRESCRIPTION_SEARCH_PAGE_NAME,
                                                         PRESCRIPTION_SEARCH_LIST_TEMPLATE, GENERAL_SEARCH_TYPE_LABEL,
                                                         **kwargs)
