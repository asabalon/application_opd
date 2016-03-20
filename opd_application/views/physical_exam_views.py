from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.views.generic import FormView, ListView, DetailView

from opd_application.forms import PhysicalExamForm, PhysicalExamKey, PhysicalExamDetail
from opd_application.models import PhysicalExam, MedicalRecord

import collections


class PhysicalExamFormView(FormView):
    form_class = PhysicalExamForm
    template_name = 'physical_exam_form.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('medical'):
            medical_record = MedicalRecord.objects.get(pk=request.GET.get('medical'))
            form = self.form_class(initial={'medical_record': medical_record.id})

            return render(request, self.template_name, {'form': form})
        else:
            return redirect('opd:home', permanent=True)

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
                                physical_exam_detail.value = value
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

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamFormView, self).dispatch(request, *args, **kwargs)


class PhysicalExamDetailView(DetailView):
    model = PhysicalExam
    template_name = 'physical_exam_profile.html'

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
                value_list.append(value.value)
            detail_list.append(value_list)

        key_detail_zip = zip(key_list, detail_list)

        return render(request, self.template_name,
                      {'physical_exam': physical_exam, 'patient': physical_exam.medical_record.patient,
                       'key_detail_zip': key_detail_zip})

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamDetailView, self).dispatch(request, *args, **kwargs)


class PhysicalExamListView(ListView):
    model = PhysicalExam
    template_name = 'physical_exam_list.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('medical'):
            medical_record = MedicalRecord.objects.get(pk=request.GET.get('medical'))
            physical_exams = self.model.objects.filter(medical_record=medical_record).order_by('recorded_date')

            return render(request, self.template_name,
                          {'physical_exams': physical_exams, 'medical_record': medical_record,
                           'patient': medical_record.patient})
        else:
            return redirect('opd:home', permanent=True)

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(PhysicalExamListView, self).dispatch(request, *args, **kwargs)
