# from python library
import logging
import urllib.parse

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
from opd_application.constants import DASHBOARD_PAGE_NAME, LABORATORY_FORM_TEMPLATE, LOGIN_PAGE_NAME, \
    LABORATORY_PROFILE_TEMPLATE, LABORATORY_LIST_TEMPLATE, PHYSICAL_EXAM_LIST_PAGE_NAME, LABORATORY_FORM_PAGE_NAME, \
    LABORATORY_PAGE_ICON, PHYSICAL_EXAM_PAGE_ICON, LABORATORY_LIST_PAGE_NAME, DIAGNOSIS_LIST_PAGE_NAME, \
    DIAGNOSIS_PAGE_ICON, LABORATORY_SEARCH_LIST_TEMPLATE, LABORATORY_SEARCH_PAGE_NAME, GENERAL_SEARCH_TYPE_LABEL, \
    LABORATORY_EDIT_PAGE_NAME, MEDICAL_RECORD_PROFILE_PAGE_NAME, LABORATORY_TEST_LIST_TEMPLATE, \
    LABORATORY_TEST_LIST_PAGE_NAME
from opd_application.forms.laboratory_forms import LaboratoryResultForm
from opd_application.functions import log_start_time, log_end_time, log_exit_atomic_trans, log_enter_atomic_trans
from opd_application.models.laboratory_models import LaboratoryTestDetail, Laboratory, LaboratoryResult, LaboratoryTest
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.models.patient_models import Patient
from opd_application.views.general_views import GeneralListView, GeneralSearchListView

logger = logging.getLogger(__name__)


class LaboratoryFormView(FormView):
    """
    View for handling laboratory results creation. Uses GET function to initially fill the form with patient
    details. POST function handles saving of laboratory result record and laboratory record.
    """

    form_class = LaboratoryResultForm
    template_name = LABORATORY_FORM_TEMPLATE

    model_items = LaboratoryTestDetail.objects.count()
    LaboratoryFormSet = formset_factory(form_class, max_num=model_items)

    def get(self, request, *args, **kwargs):
        """
        Retrieves laboratory test detail records from database then creates a formset depending on the
        number of retrieved rows. Pre-fills patient field using relationship between retrieved value of
        [medical] argument from URI
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        initial = []

        logger.info('Retrieving medical record ID from request URI')
        medical_record_id = request.GET.get('medical')
        logger.info('Retrieving laboratory record ID from request URI')
        laboratory_id = kwargs.get('id')

        laboratory_test_details = LaboratoryTestDetail.objects.all()

        if medical_record_id:
            logger.info('Retrieved medical record ID value [%s]' % medical_record_id)
            medical_record = MedicalRecord.objects.get(pk=int(medical_record_id))

            for test_detail in laboratory_test_details:
                logger.info('Creating display labels for [%s]' % test_detail)
                display = '%s: %s' % (str(test_detail.laboratory_test), test_detail.description)

                if test_detail.laboratory_measurement_unit.is_displayable:
                    display += ' (%s)' % test_detail.laboratory_measurement_unit

                logger.info('Created display is [%s]' % display)
                initial.append({'laboratory_test_detail_display': display,
                                'laboratory_test_detail': test_detail,
                                'value': ''})

            formset = self.LaboratoryFormSet(initial=initial)
            response = render(request, self.template_name,
                              {'formset': formset, 'medical_record': medical_record, 'submit_label': 'Record'})
        elif laboratory_id:
            logger.info('Retrieved laboratory record ID value [%s]' % laboratory_id)
            laboratory = Laboratory.objects.get(pk=int(laboratory_id))

            for test_detail in laboratory_test_details:
                logger.info(
                    'Retrieving non-deleted laboratory results for laboratory record [%s] and test detail [%s]' % (
                        laboratory_id, test_detail))
                laboratory_result = LaboratoryResult.objects.filter(laboratory=laboratory,
                                                                    laboratory_test_detail=test_detail,
                                                                    is_deleted=False)
                logger.info('Creating display labels for [%s]' % test_detail)
                display = '%s: %s' % (str(test_detail.laboratory_test), test_detail.description)

                if test_detail.laboratory_measurement_unit.is_displayable:
                    display += ' (%s)' % test_detail.laboratory_measurement_unit

                logger.info('Created display is [%s]' % display)

                if laboratory_result.count() > 1:
                    logger.warn('Laboratory result count is greater than expected for test detail [%s]' % test_detail)
                    logger.info('Defaulting to first retrieved item')
                    initial.append({'laboratory_test_detail_display': display,
                                    'laboratory_test_detail': laboratory_result.first().laboratory_test_detail,
                                    'value': laboratory_result.first().value, })
                elif laboratory_result.count() < 1:
                    logger.info('No related laboratory result record for test detail [%s]' % test_detail)
                    initial.append({'laboratory_test_detail_display': display,
                                    'laboratory_test_detail': test_detail,
                                    'value': '', })
                else:
                    logger.info('Successful laboratory result retrieval for test detail [%s]' % test_detail)
                    initial.append({'laboratory_test_detail_display': display,
                                    'laboratory_test_detail': laboratory_result.last().laboratory_test_detail,
                                    'value': laboratory_result.last().value, })

            formset = self.LaboratoryFormSet(initial=initial)

            response = render(request, self.template_name,
                              {'formset': formset, 'medical_record': laboratory.medical_record,
                               'submit_label': 'Update', 'laboratory': laboratory})
        else:
            logger.warn('Did not receive value for required patient parameter')
            response = redirect(DASHBOARD_PAGE_NAME, permanent=True)

        log_end_time()
        return response

    def post(self, request, *args, **kwargs):
        """
        Validates formset data. Creates a new laboratory record then saves laboratory result records with
        non-empty value.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        logger.info('Retrieving laboratory record ID from POST data')
        laboratory_id = request.POST.get('laboratory')
        logger.info('Retrieving medical record from database using medical record ID from POST data')
        medical_record = MedicalRecord.objects.get(pk=int(request.POST.get('medical_record')))

        if 'cancel' in request.POST:
            logger.info('User clicked cancel')
            if medical_record:
                logger.info('Redirecting to medical record page')
                return HttpResponseRedirect(
                    reverse_lazy(MEDICAL_RECORD_PROFILE_PAGE_NAME, kwargs={'id': medical_record.id}))
            else:
                logger.info('Redirecting to home page')
                return HttpResponseRedirect(reverse_lazy(DASHBOARD_PAGE_NAME))
        else:
            logger.info('User clicked submit')

        logger.info('Retrieving POST data')
        formset = self.LaboratoryFormSet(request.POST)

        logger.info('Validating formset values')
        if formset.is_valid():
            logger.info('Received valid formset data')

            if laboratory_id:
                logger.info('Retrieved laboratory record as foreign key for laboratory result records')
                laboratory = Laboratory.objects.get(pk=int(laboratory_id))
            else:
                logger.info('Created laboratory record as foreign key for laboratory result records')
                laboratory = Laboratory(medical_record=medical_record, recorded_by=request.user,
                                        recorded_date=localtime(now()))
            with atomic():
                log_enter_atomic_trans()
                for form in formset:
                    if laboratory_id:
                        logger.info(
                            'Retrieving latest laboratory result for laboratory record [%s] and test detail [%s]' % (
                                laboratory_id, form.instance.laboratory_test_detail))
                        laboratory_result = LaboratoryResult.objects.filter(laboratory=laboratory,
                                                                            laboratory_test_detail=form.instance.laboratory_test_detail,
                                                                            is_deleted=False).order_by(
                            '-id').first()
                    else:
                        logger.info(
                            'Creating latest laboratory result for laboratory record [%s] and test detail [%s]' % (
                                laboratory_id, form.instance.laboratory_test_detail))
                        laboratory_result = form.save(commit=False)

                    if laboratory_result:
                        logger.info('Received a non-empty instance for laboratory result')
                        if laboratory_id and form.instance.value:
                            if form.instance.value == laboratory_result.value:
                                logger.info('No change was detected')
                            else:
                                logger.info('Updating details of laboratory laboratory')
                                laboratory_result.value = form.instance.value
                        elif laboratory_id and not form.instance.value:
                            logger.info('Removing details of laboratory result')
                            laboratory_result.is_deleted = True
                        elif laboratory_result.value:
                            logger.info('Saving details of new laboratory result for new laboratory record')
                            laboratory.save()
                            laboratory_result.laboratory = laboratory
                        else:
                            logger.info('Skipping laboratory result for [%s]' % form.instance.laboratory_test_detail)
                            continue
                    else:
                        logger.info('No value for laboratory_result variable. Using value from form')
                        if form.instance.value:
                            logger.info('Saving details of new laboratory result for previous laboratory record')
                            laboratory.save()
                            laboratory_result = form.save(commit=False)
                            laboratory_result.laboratory = laboratory
                        else:
                            logger.info('Skipping laboratory result for [%s]' % form.instance.laboratory_test_detail)
                            continue

                    laboratory_result.updated_by = request.user
                    laboratory_result.updated_date = localtime(now())
                    laboratory_result.save()

            log_exit_atomic_trans()

            logger.info('Redirecting to laboratory profile page')
            response = redirect(laboratory)
        else:
            logger.warn('Received invalid formset data')
            response = render(request, self.template_name, {'formset': formset, 'medical_record': medical_record})

        log_end_time()
        return response

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(LaboratoryFormView, self).dispatch(request, *args, **kwargs)


class LaboratoryDetailView(DetailView):
    """
    View for displaying patient's laboratory record information for a specific medical record. Uses only GET function
    to display related laboratory result records for every laboratory test.
    """

    model = Laboratory
    template_name = LABORATORY_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Retrieves laboratory test records from database. These tests will be used to fetch records for
        patient's laboratory record. Tests will be used to group and order laboratory result records within a zip list.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        logger.info('Retrieving laboratory id from request URI')
        test_list = []
        laboratory_result_per_test_list = []
        laboratory = self.model.objects.get(pk=kwargs.get('id'))
        laboratory_tests = LaboratoryTest.objects.all().order_by('order')

        for test in laboratory_tests:
            logger.info('Retrieving laboratory test detail records for test [%s]' % test)
            laboratory_results = []
            test_list.append(test)
            laboratory_test_details = LaboratoryTestDetail.objects.filter(laboratory_test=test).order_by('order')

            for test_detail in laboratory_test_details:
                logger.info('Retrieving laboratory results records for test detail [%s]' % test_detail)
                result_set = LaboratoryResult.objects.filter(laboratory=laboratory,
                                                             laboratory_test_detail=test_detail, is_deleted=False)
                if result_set:
                    for laboratory_result in result_set:
                        laboratory_results.append(laboratory_result)

            laboratory_result_per_test_list.append(laboratory_results)

        test_results_zip = zip(test_list, laboratory_result_per_test_list)

        return render(request, self.template_name,
                      {'laboratory': laboratory, 'test_results_zip': test_results_zip,
                       'list_link': '%s?%s&test_detail=' % (
                           reverse_lazy(LABORATORY_TEST_LIST_PAGE_NAME),
                           urllib.parse.urlencode({'patient': laboratory.medical_record.patient.id})),
                       'edit_link': reverse_lazy(LABORATORY_EDIT_PAGE_NAME, kwargs={'id': laboratory.id})})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(LaboratoryDetailView, self).dispatch(request, *args, **kwargs)


class LaboratoryTestDetailView(DetailView):
    """
    View for displaying patient's laboratory record information for a specific medical record. Uses only GET function
    to display related laboratory result records for every laboratory test.
    """

    model = LaboratoryResult
    template_name = LABORATORY_TEST_LIST_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Retrieves laboratory test records from database. These tests will be used to fetch records for
        patient's laboratory record. Tests will be used to group and order laboratory result records within a zip list.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        logger.info('Retrieving patient id from request URI')
        patient = Patient.objects.get(pk=request.GET.get('patient'))
        laboratory_test_detail = LaboratoryTestDetail.objects.get(pk=request.GET.get('test_detail'))
        laboratory_results = LaboratoryResult.objects.filter(laboratory_test_detail=laboratory_test_detail,
                                                             laboratory__medical_record__patient=patient,
                                                             is_deleted=False).order_by(
            '-updated_date')

        return render(request, self.template_name,
                      {'laboratory_results': laboratory_results, 'patient': patient,
                       'laboratory_test_detail': laboratory_test_detail})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(LaboratoryTestDetailView, self).dispatch(request, *args, **kwargs)


class LaboratoryListView(GeneralListView):
    """
    View for displaying all patient's laboratory record information for a specific medical record. Uses only GET
    function to display all laboratory records for chosen medical record. Extends GeneralListView.
    """

    def __init__(self):
        logger.info('Instantiating GenaralListView super class')
        super(LaboratoryListView, self).__init__(model=Laboratory,
                                                 template_name=LABORATORY_LIST_TEMPLATE,
                                                 add_page_name=LABORATORY_FORM_PAGE_NAME,
                                                 left_link_page_name=PHYSICAL_EXAM_LIST_PAGE_NAME,
                                                 left_link_name='Physical Exam Results',
                                                 left_link_icon=PHYSICAL_EXAM_PAGE_ICON,
                                                 right_link_page_name=DIAGNOSIS_LIST_PAGE_NAME,
                                                 right_link_name='Diagnoses',
                                                 right_link_icon=DIAGNOSIS_PAGE_ICON,
                                                 page_icon=LABORATORY_PAGE_ICON,
                                                 page_title='Laboratory Results',
                                                 list_page_name=LABORATORY_LIST_PAGE_NAME)


class LaboratorySearchListView(GeneralSearchListView):
    """
    View for displaying all laboratory record information for a specific search query. Uses POST
    function to display initial laboratory records search results. GET function is used to display results for a given
    page number. Extends GeneralSearchListView.
    """

    def __init__(self, **kwargs):
        logger.info('Instantiating GeneralSearchListView super class')
        super(LaboratorySearchListView, self).__init__(Laboratory, DIAGNOSIS_PAGE_ICON, 'Laboratory Results',
                                                       LABORATORY_SEARCH_PAGE_NAME,
                                                       LABORATORY_SEARCH_LIST_TEMPLATE, GENERAL_SEARCH_TYPE_LABEL,
                                                       **kwargs)
