from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.constants import *
from opd_application.forms import PhysicalExamForm
from opd_application.models import PhysicalExam, MedicalRecord, PhysicalExamKey, PhysicalExamDetail
from opd_application.views.general_views import GeneralSearchListView, calculate_offset, modify_page_links, \
    validate_response

import collections


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
        keys = list(PhysicalExamKey.objects.all().order_by('id'))
        key_list = []
        detail_list = []
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
                       'key_detail_zip': key_detail_zip})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamDetailView, self).dispatch(request, *args, **kwargs)


class PhysicalExamListView(ListView):
    model = PhysicalExam
    template_name = PHYSICAL_EXAM_LIST_TEMPLATE

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
        if request.GET.get('medical'):
            medical_record = MedicalRecord.objects.get(pk=request.GET.get('medical'))

            added_offset = calculate_offset(self, request)

            query_set = self.model.objects.filter(medical_record=medical_record).order_by('recorded_date')

            self.search_count = query_set.count()
            self.searches = query_set[0 + added_offset:MAX_LIST_ITEMS_PER_PAGE + added_offset + 1]
            self.search_link = reverse_lazy(MEDICAL_RECORD_LIST_PAGE_NAME) + '?medical=' + str(
                medical_record.id) + '&current='

            modify_page_links(self)
            validate_response(self)

            return render(request, self.template_name,
                          {'searches': self.searches[0:MAX_LIST_ITEMS_PER_PAGE],
                           'patient': medical_record.patient,
                           'pages': self.pages,
                           'error_message': self.error_message,
                           'search_link': self.search_link,
                           'left_link': medical_record.get_absolute_url(),
                           'left_link_icon': MEDICAL_RECORD_PAGE_ICON,
                           'left_link_name': 'Medical Record',
                           'right_link': '',
                           'right_link_icon': LABORATORY_PAGE_ICON,
                           'right_link_name': 'Laboratory Results',
                           'page_title': 'Physical Exams',
                           'page_icon': PHYSICAL_EXAM_PAGE_ICON,
                           'add_link': reverse_lazy(PHYSICAL_EXAM_FORM_PAGE_NAME) + '?medical=' + str(
                               medical_record.id),
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
        return super(PhysicalExamListView, self).dispatch(request, *args, **kwargs)


class PhysicalExamSearchListView(GeneralSearchListView):
    def __init__(self, **kwargs):
        super(PhysicalExamSearchListView, self).__init__(PhysicalExam, PHYSICAL_EXAM_PAGE_ICON, 'Physical Exams',
                                                         reverse_lazy(PHYSICAL_EXAM_SEARCH_LIST_PAGE_NAME),
                                                         PHYSICAL_EXAM_SEARCH_LIST_TEMPLATE,
                                                         GENERAL_SEARCH_TYPE_LABEL,
                                                         **kwargs)

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamSearchListView, self).dispatch(request, *args, **kwargs)


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
                        print(values)
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
