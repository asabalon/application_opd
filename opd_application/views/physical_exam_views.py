import collections
import logging

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.constants import PHYSICAL_EXAM_FORM_PAGE_NAME, PHYSICAL_EXAM_FORM_TEMPLATE, DASHBOARD_PAGE_NAME, \
    PHYSICAL_EXAM_PROFILE_TEMPLATE, PHYSICAL_EXAM_LIST_PAGE_NAME, PHYSICAL_EXAM_PAGE_ICON, \
    PHYSICAL_EXAM_PROFILE_PAGE_NAME, PHYSICAL_EXAM_LIST_TEMPLATE, PHYSICAL_EXAM_SEARCH_LIST_PAGE_NAME, \
    PHYSICAL_EXAM_SEARCH_LIST_TEMPLATE, LOGIN_PAGE_NAME, GENERAL_SEARCH_TYPE_LABEL, PRESCRIPTION_LIST_PAGE_NAME, \
    PRESCRIPTION_PAGE_ICON, LABORATORY_PAGE_ICON, LABORATORY_LIST_PAGE_NAME
from opd_application.forms.physical_exam_forms import PhysicalExamForm
from opd_application.models.physical_exam_models import PhysicalExam, MedicalRecord, PhysicalExamKey, PhysicalExamDetail
from opd_application.views.general_views import GeneralSearchListView, modify_page_links, \
    validate_response, GeneralListView

logger = logging.getLogger(__name__)


class PhysicalExamFormView(FormView):
    form_class = PhysicalExamForm
    template_name = PHYSICAL_EXAM_FORM_TEMPLATE

    def get(self, request, *args, **kwargs):
        if request.GET.get('medical'):
            medical_record = MedicalRecord.objects.get(pk=request.GET.get('medical'))
            form = self.form_class(initial={'medical_record': medical_record.id})

            return render(request, self.template_name, {'form': form})
        else:
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.form_class(data=request.POST)
        if form.is_valid():
            medical_record = MedicalRecord.objects.get(pk=form.cleaned_data['medical_record'])
            physical_exam = PhysicalExam(medical_record=medical_record, recorded_by=request.user,
                                         recorded_date=localtime(now()))
            physical_exam.save()
            for field in form.fields:
                # Retrieve Physical Exam Keys (Limit Result)
                key = list(PhysicalExamKey.objects.filter(key_value__iexact=field)[:1])
                if key:
                    # Check if there is available data for current Physical Exam Key
                    if form.cleaned_data[field]:
                        values = form.cleaned_data[field]
                        # Check if value is Iterable and not String before saving
                        if isinstance(values, collections.Iterable) and not isinstance(values, str):
                            for value in values:
                                if isinstance(value, str):
                                    real_value = value
                                else:
                                    real_value = value.id
                                physical_exam_detail = PhysicalExamDetail(physical_exam=physical_exam, key=key[0],
                                                                          real_value=real_value, str_value=value)
                                physical_exam_detail.save()
                        elif not isinstance(values, str) and not isinstance(values, bool):
                            physical_exam_detail = PhysicalExamDetail(physical_exam=physical_exam, key=key[0],
                                                                      real_value=values.id, str_value=values)
                            physical_exam_detail.save()
                        else:
                            physical_exam_detail = PhysicalExamDetail(physical_exam=physical_exam, key=key[0],
                                                                      real_value=values, str_value=values)
                            physical_exam_detail.save()
                    else:
                        pass
                else:
                    pass

            return redirect(physical_exam)
        else:
            context.update({'form': form})

        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamFormView, self).dispatch(request, *args, **kwargs)


class PhysicalExamDetailView(DetailView):
    model = PhysicalExam
    template_name = PHYSICAL_EXAM_PROFILE_TEMPLATE

    def get(self, request, *args, **kwargs):
        physical_exam = self.model.objects.get(pk=kwargs.get('id'))
        next_exam_record = self.model.objects.filter(medical_record=physical_exam.medical_record,
                                                     id__gt=physical_exam.id).order_by('id').first()
        prev_exam_record = self.model.objects.filter(medical_record=physical_exam.medical_record,
                                                     id__lt=physical_exam.id).order_by('-id').first()

        keys = list(PhysicalExamKey.objects.all().order_by('id'))
        key_list = []
        detail_list = []
        link_dict = {}

        if next_exam_record is not None:
            link_dict.update(
                {'next_link': reverse_lazy(PHYSICAL_EXAM_PROFILE_PAGE_NAME, kwargs={'id': str(next_exam_record.id)})})
        if prev_exam_record is not None:
            link_dict.update(
                {'prev_link': reverse_lazy(PHYSICAL_EXAM_PROFILE_PAGE_NAME, kwargs={'id': str(prev_exam_record.id)})})

        for key in keys:
            key_list.append(key.display_value)
            value_list = []
            values = list(
                PhysicalExamDetail.objects.filter(physical_exam=physical_exam, key=key))
            for value in values:
                value_list.append(value.str_value)
            detail_list.append(value_list)

        key_detail_zip = zip(key_list, detail_list)

        return render(request, self.template_name,
                      {'physical_exam': physical_exam, 'patient': physical_exam.medical_record.patient,
                       'key_detail_zip': key_detail_zip, 'link_dict': link_dict})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamDetailView, self).dispatch(request, *args, **kwargs)


class PhysicalExamListView(GeneralListView):
    """
    View for displaying all patient's physical exam record information for a specific medical record. Uses only GET
    function to display all physical exam records for chosen medical record. Extends GeneralListView.
    """

    def __init__(self):
        logger.info('Instantiating GenaralListView super class')
        super(PhysicalExamListView, self).__init__(model=PhysicalExam,
                                                   template_name=PHYSICAL_EXAM_LIST_TEMPLATE,
                                                   add_page_name=PHYSICAL_EXAM_FORM_PAGE_NAME,
                                                   left_link_page_name=PRESCRIPTION_LIST_PAGE_NAME,
                                                   left_link_name='Prescriptions',
                                                   left_link_icon=PRESCRIPTION_PAGE_ICON,
                                                   right_link_page_name=LABORATORY_LIST_PAGE_NAME,
                                                   right_link_name='Laboratory Results',
                                                   right_link_icon=LABORATORY_PAGE_ICON,
                                                   page_icon=PHYSICAL_EXAM_PAGE_ICON,
                                                   page_title='Physical Exam Results',
                                                   list_page_name=PHYSICAL_EXAM_LIST_PAGE_NAME)


class PhysicalExamSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(PhysicalExamSearchListView, self).__init__(PhysicalExam, PHYSICAL_EXAM_PAGE_ICON, 'Physical Exams',
                                                         PHYSICAL_EXAM_SEARCH_LIST_PAGE_NAME,
                                                         PHYSICAL_EXAM_SEARCH_LIST_TEMPLATE,
                                                         GENERAL_SEARCH_TYPE_LABEL,
                                                         **kwargs)


class PhysicalExamEditFormView(FormView):
    form_class = PhysicalExamForm
    template_name = PHYSICAL_EXAM_FORM_TEMPLATE

    def get(self, request, *args, **kwargs):
        physical_exam = PhysicalExam.objects.get(pk=kwargs.get('id'))
        physical_exam_details = PhysicalExamDetail.objects.filter(physical_exam=physical_exam)

        print(physical_exam_details)
        initial = {}

        physical_exam_keys = PhysicalExamKey.objects.all()
        for key in physical_exam_keys:
            physical_exam_details = PhysicalExamDetail.objects.filter(physical_exam=physical_exam, key=key)
            if physical_exam_details.count() > 1:
                value_list = []
                for detail in physical_exam_details:
                    value_list.append(detail.real_value)
                initial.update({key.key_value: value_list})
            else:
                initial.update({key.key_value: physical_exam_details[0].real_value})
        initial.update({'medical_record': physical_exam.medical_record.id})

        print(initial)

        form = self.form_class(initial=initial)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.form_class(data=request.POST)
        if form.is_valid():
            medical_record = MedicalRecord.objects.get(pk=form.cleaned_data['medical_record'])
            physical_exam = PhysicalExam(medical_record=medical_record, recorded_by=request.user,
                                         recorded_date=localtime(now()))
            physical_exam.save()
            for field in form.fields:
                # Retrieve Physical Exam Keys (Limit Result)
                key = list(PhysicalExamKey.objects.filter(key_value__iexact=field)[:1])
                if key:
                    # Check if there is available data for current Physical Exam Key
                    if form.cleaned_data[field]:
                        values = form.cleaned_data[field]
                        physical_exam_detail = PhysicalExamDetail(physical_exam=physical_exam, key=key[0])
                        # Check if value is Iterable and not String before saving
                        if isinstance(values, collections.Iterable) and not isinstance(values, str):
                            for value in values:
                                physical_exam_detail.value = value.id
                        else:
                            physical_exam_detail.value = values
                        physical_exam_detail.save()
                    else:
                        pass
                else:
                    pass

            return redirect(physical_exam)
        else:
            context.update({'form': form})

        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamEditFormView, self).dispatch(request, *args, **kwargs)
