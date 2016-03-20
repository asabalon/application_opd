from django.db.models import Model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView

from opd_application.constants import *
from opd_application.forms import *

DEFAULT_SEARCH_TYPE = '1'

GENERAL_SEARCH_LABEL = {
    '1': 'by Patient Last Name',
    '2': 'by Encoder Last Name',
    '3': 'by Recorded Date',
}

PATIENT_SEARCH_LABEL = {
    '1': 'by Last Name',
    '2': 'by First Name',
    '3': 'by Birth Date',
}

SEARCH_LINKS = {
    '1': reverse_lazy('opd:search_patient'),
    '2': reverse_lazy('opd:search_medical'),
    '3': reverse_lazy('opd:search_exam'),
    '4': reverse_lazy('opd:search_laboratory'),
    '5': reverse_lazy('opd:search_diagnosis'),
    '6': reverse_lazy('opd:search_prescription'),
}


class DashboardView(TemplateView):
    link = reverse_lazy('opd:home')
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        icons = ['fa-user', 'fa-list-alt', 'fa-heartbeat', 'fa-flask', 'fa-stethoscope', 'fa-file-text-o']
        labels = ['Patients', 'Medical Records', 'Physical Exams', 'Laboratory Results', 'Diagnoses', 'Prescriptions']
        icons_labels_zip = zip(icons, labels)

        if request.GET.get('search_category'):
            search_category = request.GET.get('search_category')
        else:
            search_category = '1'

        if search_category == '1':
            search_label = PATIENT_SEARCH_LABEL
        else:
            search_label = GENERAL_SEARCH_LABEL

        return render(request, self.template_name,
                      {'form': GeneralSearchForm(placeholder='Search ' + labels[int(search_category) - 1],
                                                 search_type_value=DEFAULT_SEARCH_TYPE,
                                                 search_link=SEARCH_LINKS.get(search_category)),
                       'icons_labels_zip': icons_labels_zip, 'link': self.link,
                       'search_category': int(search_category),
                       'search_label': search_label,
                       'label': search_label.get(DEFAULT_SEARCH_TYPE)})

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class GeneralSearchListView(ListView):
    # need initialisation
    model = Model
    template_name = ''
    page_icon = ''
    page_title = ''
    search_link = ''

    search_type = ''
    search_param = ''
    search_labels = {}
    current_page = 1
    searches = []

    next_link = ''
    next_link_class = ''
    previous_link = ''
    previous_link_class = ''

    def return_values(self, request):
        return render(request, self.template_name,
                      {'form': GeneralSearchForm(placeholder='Search ' + self.page_title, search_link=self.search_link,
                                                 search_type_value=DEFAULT_SEARCH_TYPE,
                                                 initial={'search_type': self.search_type,
                                                          'search_param': self.search_param}),
                       'searches': self.searches[0:MAX_LIST_ITEMS_PER_PAGE],
                       'label': self.search_labels.get(self.search_type),
                       'search_label': self.search_labels,
                       'page_title': self.page_title,
                       'page_icon': self.page_icon,
                       'current_page': self.current_page,
                       'next_link': self.next_link,
                       'next_link_class': self.next_link_class,
                       'previous_link': self.previous_link,
                       'previous_link_class': self.previous_link_class,
                       })

    def modify_page_links(self):
        self.search_link += '?search_param=' + self.search_param + '&search_type=' + self.search_type + '&current='

        # check if there are still records to show
        if len(self.searches) > MAX_LIST_ITEMS_PER_PAGE:
            self.next_link = self.search_link + str(self.current_page + 1)
            self.next_link_class = ''
        else:
            self.next_link = ''
            self.next_link_class = 'disabled'

        # check to see if there are previous records to show
        if self.current_page <= 1:
            self.previous_link = ''
            self.previous_link_class = 'disabled'
        else:
            self.previous_link = self.search_link + str(self.current_page - 1)
            self.previous_link_class = ''

    def search_matches(self, search_type, search_param, offset, limit):
        if self.model == Patient:
            if search_type == '1':
                return self.model.objects.filter(last_name__icontains=search_param).order_by('first_name')[offset:limit]
            elif search_type == '2':
                return self.model.objects.filter(first_name__icontains=search_param).order_by('last_name')[offset:limit]
            elif search_type == '3':
                return self.model.objects.filter(birth_date__iexact=search_param).order_by('last_name')[offset:limit]
            else:
                return None
        else:
            if search_type == '1':
                return self.model.objects.filter(patient__last_name__icontains=search_param).order_by('-recorded_date')[
                       offset:limit],
            elif search_type == '2':
                return self.model.objects.filter(recorded_by__last_name__icontains=search_param).order_by(
                    '-recorded_date')[offset:limit],
            elif search_type == '3':
                return self.model.objects.filter(recorded_date__iexact=search_param).order_by('-recorded_date')[
                       offset:limit],
            else:
                return None

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

            self.searches = self.search_matches(self.search_type, self.search_param, 0 + added_offset,
                                                MAX_LIST_ITEMS_PER_PAGE + added_offset + 1)

            self.modify_page_links()

            return self.return_values(request)
        else:
            return redirect('opd:home', permanent=True)

    def post(self, request, *args, **kwargs):
        if request.POST.get('search_type'):
            search_type_value = request.POST.get('search_type')
        else:
            search_type_value = DEFAULT_SEARCH_TYPE

        form = GeneralSearchForm(data=request.POST, placeholder='', search_link=self.search_link,
                                 search_type_value=search_type_value)

        if form.is_valid():
            self.current_page = 1
            self.search_type = form.cleaned_data['search_type']
            self.search_param = form.cleaned_data['search_param']

            limit = MAX_LIST_ITEMS_PER_PAGE + 1

            if self.search_param:
                self.searches = self.search_matches(self.search_type, self.search_param, 0, limit)
            else:
                self.searches = self.model.objects.all().order_by('-recorded_date')[0:limit]

            self.modify_page_links()

            return self.return_values(request)
        else:
            return redirect('opd:home', permanent=True)

    def __init__(self, model, page_icon, page_title, search_link, template_name, search_labels, **kwargs):
        super(GeneralSearchListView, self).__init__(**kwargs)

        self.model = model
        self.page_icon = page_icon
        self.page_title = page_title
        self.search_link = search_link
        self.template_name = template_name
        self.search_labels = search_labels

    @method_decorator(login_required(login_url='auth:login'))
    def dispatch(self, request, *args, **kwargs):
        return super(GeneralSearchListView, self).dispatch(request, *args, **kwargs)
