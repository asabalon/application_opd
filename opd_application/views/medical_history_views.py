# from python library
import logging

# from third-party applications
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, DetailView

# from main application
from opd_application.constants import DASHBOARD_PAGE_NAME, MEDICAL_HISTORY_FORM_TEMPLATE, LOGIN_PAGE_NAME, \
    MEDICAL_HISTORY_PROFILE_TEMPLATE, MEDICAL_HISTORY_EDIT_PAGE_NAME
from opd_application.forms.medical_history_forms import MedicalHistoryDetailForm
from opd_application.models.medical_history_models import Patient, MedicalHistoryCategoryDetail, MedicalHistory, \
    MedicalHistoryDetail, MedicalHistoryCategory

logger = logging.getLogger(__name__)


class MedicalHistoryFormView(FormView):
    """
    View for handling medical history detail creation. Uses GET function to initially fill the form with patient
    details. POST function handles saving of medical history detail record and medical history record.
    """

    form_class = MedicalHistoryDetailForm
    template_name = MEDICAL_HISTORY_FORM_TEMPLATE

    model_items = MedicalHistoryCategoryDetail.objects.count()
    MedicalHistoryFormSet = formset_factory(form_class, max_num=model_items)

    def get(self, request, *args, **kwargs):
        """
        Retrieves medical history category detail records from database then creates a formset depending on the
        number of retrieved rows. Pre-fills patient field using value of [patient] argument from URI
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        logger.info('Retrieving patient ID from request URI')
        patient_id = request.GET.get('patient') or kwargs.get('id')

        if patient_id:
            logger.info('Retrieved patient ID value [%s]' % patient_id)
            initial = []
            patient = Patient.objects.get(pk=patient_id)
            medical_history_category_details = MedicalHistoryCategoryDetail.objects.all()
            patient_latest_medical_history = MedicalHistory.objects.filter(patient=patient).order_by('-id').first()

            for category_detail in medical_history_category_details:
                logger.info('Creating display labels for [%s]' % category_detail)
                display = '%s: %s' % (str(category_detail.medical_history_category), category_detail.description)
                medical_history_details = None

                if category_detail.medical_history_category_unit.is_displayable:
                    display += ' (%s)' % category_detail.medical_history_category_unit

                logger.info('Created display is [%s]' % display)

                if patient_latest_medical_history:
                    try:
                        logger.info('Retrieving patient [%s] latest medical history record' % patient)
                        medical_history_details = MedicalHistoryDetail.objects.get(
                            medical_history=patient_latest_medical_history,
                            medical_history_category_detail=category_detail)
                        logger.info('Latest medical history record found')
                    except MedicalHistoryDetail.DoesNotExist:
                        logger.info('No recorded medical history found')

                initial.append({'medical_history_category_detail_display': display,
                                'medical_history_category_detail': category_detail,
                                'value': medical_history_details.value if medical_history_details else ''})

            formset = self.MedicalHistoryFormSet(initial=initial)

            return render(request, self.template_name, {'formset': formset, 'patient': patient})

        else:
            logger.warn('Did not receive value for required patient parameter')
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

    def post(self, request, *args, **kwargs):
        """
        Validates formset data. Creates a new medical history record for tracking purposes. Saves medical history detail
        records with non-empty value.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        if 'cancel' in request.POST:
            logger.info('User clicked cancel')
            return HttpResponseRedirect(reverse_lazy(DASHBOARD_PAGE_NAME))

        logger.info('Retrieving POST data')
        formset = self.MedicalHistoryFormSet(request.POST)
        patient = Patient.objects.get(pk=int(request.POST.get('patient')))

        logger.info('Validating formset values')
        if formset.is_valid():
            logger.info('Received valid formset data')
            medical_history = MedicalHistory(patient=patient, recorded_by=request.user,
                                             recorded_date=localtime(now()))
            logger.info('Created medical history record as foreign key for medical history detail records')

            for form in formset:
                medical_history_detail = form.save(commit=False)

                if medical_history_detail.value:
                    medical_history.save()
                    medical_history_detail.medical_history = medical_history
                    medical_history_detail.save()

            logger.info('Redirecting to medical history profile page')
            return redirect(medical_history)
        else:
            logger.warn('Received invalid formset data')
            return render(request, self.template_name, {'formset': formset, 'patient': patient})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalHistoryFormView, self).dispatch(request, *args, **kwargs)


class MedicalHistoryDetailView(DetailView):
    """
    View for displaying patient's medical history record information. Uses only GET function to display related medical
    history detail records for every medical history category.
    """

    model = MedicalHistory
    template_name = MEDICAL_HISTORY_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Retrieves medical history category records from database. These categories will be used to fetch records for
        patient's medical history record. Categories will be used to group and order medical history detail records in
        within a zip list.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        logger.info('Retrieving medical history id from request URI')
        category_list = []
        medical_history_details_per_category_list = []
        medical_history = self.model.objects.get(pk=kwargs.get('id'))
        medical_history_categories = MedicalHistoryCategory.objects.all().order_by('order')

        for category in medical_history_categories:
            logger.info('Retrieving medical history category detail records for category [%s]' % category)
            medical_history_details = []
            category_list.append(category)
            medical_history_category_details = MedicalHistoryCategoryDetail.objects.filter(
                medical_history_category=category).order_by('order')

            for category_detail in medical_history_category_details:
                logger.info('Retrieving medical history detail records for category detail [%s]' % category_detail)
                result_set = MedicalHistoryDetail.objects.filter(medical_history=medical_history,
                                                                 medical_history_category_detail=category_detail)
                if result_set:
                    for medical_history_detail in result_set:
                        medical_history_details.append(medical_history_detail)

            medical_history_details_per_category_list.append(medical_history_details)

        category_details_zip = zip(category_list, medical_history_details_per_category_list)

        return render(request, self.template_name,
                      {'medical_history': medical_history, 'category_details_zip': category_details_zip,
                       'edit_link': reverse_lazy(MEDICAL_HISTORY_EDIT_PAGE_NAME,
                                                 kwargs={'id': medical_history.patient.id})})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(MedicalHistoryDetailView, self).dispatch(request, *args, **kwargs)
