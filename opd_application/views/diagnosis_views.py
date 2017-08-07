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
from opd_application.constants import DASHBOARD_PAGE_NAME, DIAGNOSIS_FORM_TEMPLATE, LOGIN_PAGE_NAME, \
    DIAGNOSIS_PROFILE_TEMPLATE, DIAGNOSIS_EDIT_PAGE_NAME, DIAGNOSIS_LIST_TEMPLATE, DIAGNOSIS_FORM_PAGE_NAME, \
    DIAGNOSIS_PAGE_ICON, LABORATORY_LIST_PAGE_NAME, PRESCRIPTION_LIST_PAGE_NAME, LABORATORY_PAGE_ICON, \
    PRESCRIPTION_PAGE_ICON, DIAGNOSIS_LIST_PAGE_NAME, GENERAL_SEARCH_TYPE_LABEL, DIAGNOSIS_SEARCH_PAGE_NAME, \
    DIAGNOSIS_SEARCH_LIST_TEMPLATE
from opd_application.forms.diagnosis_forms import DiagnosisEntryForm
from opd_application.models.diagnosis_models import DiagnosisCategory, Diagnosis, DiagnosisEntry
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.functions import log_end_time, log_start_time, log_enter_atomic_trans, log_exit_atomic_trans
from opd_application.views.general_views import GeneralListView, GeneralSearchListView

logger = logging.getLogger(__name__)


class DiagnosisFormView(FormView):
    """
    View for handling diagnosis entry creation. Uses GET function to initially fill the form with patient
    details. POST function handles saving of diagnosis entries record using a diagnosis record.
    """

    form_class = DiagnosisEntryForm
    template_name = DIAGNOSIS_FORM_TEMPLATE

    diagnosis_category_count = DiagnosisCategory.objects.count()
    DiagnosisFormSet = formset_factory(form_class, max_num=diagnosis_category_count)

    def get(self, request, *args, **kwargs):
        """
        Retrieves diagnosis category records from database then creates a formset depending on the
        number of retrieved rows. Pre-fills patient field using relationship between retrieved value of
        [medical] argument from URI
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        initial = []

        logger.info('Retrieving diagnosis categories for form creation')
        diagnosis_categories = DiagnosisCategory.objects.all()

        logger.info('Retrieving medical record ID from request URI')
        medical_record_id = request.GET.get('medical')

        logger.info('Retrieving diagnosis record ID from request URI')
        diagnosis_id = kwargs.get('id')

        if medical_record_id:
            logger.info('Retrieved medical record ID value [%s]' % medical_record_id)
            medical_record = MedicalRecord.objects.get(pk=medical_record_id)

            logger.info('Creating initial diagnosis_category and value for each form in formset')
            for category in diagnosis_categories:
                initial.append({'diagnosis_category': category,
                                'value': '', })

            formset = self.DiagnosisFormSet(initial=initial)

            response = render(request, self.template_name,
                              {'formset': formset, 'medical_record': medical_record, 'submit_label': 'Record'})
        elif diagnosis_id:
            logger.info('Retrieved diagnosis record ID value [%s]' % diagnosis_id)
            diagnosis = Diagnosis.objects.get(pk=diagnosis_id)

            for category in diagnosis_categories:
                diagnosis_entry = DiagnosisEntry.objects.filter(diagnosis=diagnosis, diagnosis_category=category)

                if diagnosis_entry.count() > 1:
                    logger.warn('Diagnosis entry count is greater than expected for category [%s]' % category)
                    logger.info('Defaulting to first retrieved item')
                    initial.append({'diagnosis_category': diagnosis_entry.first().diagnosis_category,
                                    'value': diagnosis_entry.first().value,
                                    'remark': diagnosis_entry.first().remark if diagnosis_entry.first().remark else ''})
                elif diagnosis_entry.count() < 1:
                    logger.info('No related diagnosis entry for category [%s]' % category)
                    initial.append({'diagnosis_category': category,
                                    'value': '', })
                else:
                    logger.info('Successful diagnosis entry retrieval for category [%s]' % category)
                    initial.append({'diagnosis_category': diagnosis_entry.last().diagnosis_category,
                                    'value': diagnosis_entry.last().value,
                                    'remark': diagnosis_entry.last().remark if diagnosis_entry.last().remark else ''})

            formset = self.DiagnosisFormSet(initial=initial)

            response = render(request, self.template_name,
                              {'formset': formset, 'medical_record': diagnosis.medical_record,
                               'submit_label': 'Update', 'diagnosis': diagnosis})
        else:
            logger.warn('Did not receive value for required medical parameter')
            response = redirect(DASHBOARD_PAGE_NAME, permanent=True)

        log_end_time()
        return response

    def post(self, request, *args, **kwargs):
        """
        Validates formset data. Creates a new diagnosis record then saves diagnosis entry records with non-empty value.
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
        formset = self.DiagnosisFormSet(request.POST)
        diagnosis_id = request.POST.get('diagnosis')
        medical_record = MedicalRecord.objects.get(pk=int(request.POST.get('medical_record')))

        logger.info('Validating formset values')
        if formset.is_valid():
            logger.info('Received valid formset data')

            if diagnosis_id:
                logger.info('Retrieved diagnosis record as foreign key for diagnosis entry records')
                diagnosis = Diagnosis.objects.get(pk=diagnosis_id)
            else:
                logger.info('Created diagnosis record as foreign key for diagnosis entry records')
                diagnosis = Diagnosis(medical_record=medical_record, recorded_by=request.user,
                                      recorded_date=localtime(now()))

            with atomic():
                log_enter_atomic_trans()
                for idx, form in enumerate(formset):
                    if diagnosis_id:
                        logger.info(
                            'Retrieving latest diagnosis entry for diagnosis record [%s] and diagnosis category [%s]' % (
                                diagnosis_id, form.instance.diagnosis_category))
                        diagnosis_entry = DiagnosisEntry.objects.filter(diagnosis=diagnosis,
                                                                        diagnosis_category=form.instance.diagnosis_category).order_by(
                            '-id').first()
                    else:
                        logger.info(
                            'Creating latest diagnosis entry for diagnosis record [%s] and diagnosis category [%s]' % (
                                diagnosis_id, form.instance.diagnosis_category))
                        diagnosis_entry = form.save(commit=False)

                    if diagnosis_entry and diagnosis_entry.value:
                        if diagnosis_id:
                            logger.info('Updating details of diagnosis entry')
                            diagnosis_entry.value = form.instance.value
                            diagnosis_entry.remark = form.instance.remark
                        else:
                            logger.info('Saving details of new diagnosis entry')
                            diagnosis.save()
                            diagnosis_entry.diagnosis = diagnosis

                        diagnosis_entry.recorded_by = request.user
                        diagnosis_entry.recorded_date = localtime(now())
                        diagnosis_entry.save()
                    else:
                        logger.info('Value for [%s] is empty')
            log_exit_atomic_trans()

            logger.info('Redirecting to diagnosis profile page')
            response = redirect(diagnosis)
        else:
            logger.warn('Received invalid formset data')
            response = render(request, self.template_name, {'formset': formset, 'medical_record': medical_record})

        log_end_time()
        return response

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(DiagnosisFormView, self).dispatch(request, *args, **kwargs)


class DiagnosisDetailView(DetailView):
    """
    View for displaying patient's diagnosis record information for a specific medical record. Uses only GET function
    to display related diagnosis entry records for every diagnosis category.
    """

    model = Diagnosis
    template_name = DIAGNOSIS_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Retrieves diagnosis category records from database. These categories will be used to fetch records for
        patient's diagnosis record. Categories will be used to group and order diagnosis entry records within a zip
        list.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        category_list = []
        diagnosis_entry_per_category_list = []

        logger.info('Retrieving diagnosis id from request URI')
        diagnosis = self.model.objects.get(pk=kwargs.get('id'))
        diagnosis_categories = DiagnosisCategory.objects.all().order_by('order')

        for category in diagnosis_categories:
            logger.info('Retrieving diagnosis entry records for category [%s]' % category)
            category_list.append(category)
            diagnosis_entry = DiagnosisEntry.objects.filter(diagnosis=diagnosis, diagnosis_category=category)

            if diagnosis_entry.count() > 1:
                logger.warn('Diagnosis entry count is greater than expected for category [%s]' % category)
                logger.info('Defaulting to first retrieved item')
                diagnosis_entry_per_category_list.append(diagnosis_entry.first())
            elif diagnosis_entry.count() < 1:
                logger.info('No related diagnosis entry for category [%s]' % category)
                diagnosis_entry_per_category_list.append(None)
            else:
                logger.info('Successful diagnosis entry retrieval for category [%s]' % category)
                diagnosis_entry_per_category_list.append(diagnosis_entry.last())

        category_entry_zip = zip(category_list, diagnosis_entry_per_category_list)

        log_end_time()
        return render(request, self.template_name,
                      {'diagnosis': diagnosis, 'category_entry_zip': category_entry_zip, 'max_column_width': -12,
                       'max_cell_width': -6, 'edit_link': reverse_lazy(DIAGNOSIS_EDIT_PAGE_NAME,
                                                                       kwargs={'id': diagnosis.id})})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(DiagnosisDetailView, self).dispatch(request, *args, **kwargs)


class DiagnosisListView(GeneralListView):
    """
    View for displaying all patient's diagnosis record information for a specific medical record. Uses only GET
    function to display all diagnosis records for chosen medical record. Extends GeneralListView.
    """

    def __init__(self):
        logger.info('Instantiating GeneralListView super class')
        super(DiagnosisListView, self).__init__(model=Diagnosis,
                                                template_name=DIAGNOSIS_LIST_TEMPLATE,
                                                add_page_name=DIAGNOSIS_FORM_PAGE_NAME,
                                                left_link_page_name=LABORATORY_LIST_PAGE_NAME,
                                                left_link_name='Laboratory Results',
                                                left_link_icon=LABORATORY_PAGE_ICON,
                                                right_link_page_name=PRESCRIPTION_LIST_PAGE_NAME,
                                                right_link_name='Prescriptions',
                                                right_link_icon=PRESCRIPTION_PAGE_ICON,
                                                page_icon=DIAGNOSIS_PAGE_ICON,
                                                page_title='Diagnosis Results',
                                                list_page_name=DIAGNOSIS_LIST_PAGE_NAME)


class DiagnosisSearchListView(GeneralSearchListView):
    """
    View for displaying all diagnosis record information for a specific search query. Uses POST
    function to display initial diagnosis records search results. GET function is used to display results for a given
    page number. Extends GeneralSearchListView.
    """

    def __init__(self, **kwargs):
        logger.info('Instantiating GeneralSearchListView super class')
        super(DiagnosisSearchListView, self).__init__(Diagnosis, DIAGNOSIS_PAGE_ICON, 'Diagnoses',
                                                      DIAGNOSIS_SEARCH_PAGE_NAME,
                                                      DIAGNOSIS_SEARCH_LIST_TEMPLATE, GENERAL_SEARCH_TYPE_LABEL,
                                                      **kwargs)
