import logging, math

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Model
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from opd_application.forms import *

# TODO: Add Python Documentation
# TODO: Modify Pagination to show 5 page links instead of only 1
# TODO: Add Logging

logger = logging.getLogger(__name__)


def calculate_offset(self, request):
    if request.GET.get('current'):
        self.current_page = int(request.GET.get('current'))
        added_offset = MAX_LIST_ITEMS_PER_PAGE * (self.current_page - 1)
    else:
        self.current_page = 1
        added_offset = 0

    return added_offset


def modify_page_links(self):
    # check if there are still records to show
    if len(self.searches) > MAX_LIST_ITEMS_PER_PAGE:
        self.next_link = self.search_link + str(self.current_page + 1)
        self.next_link_class = ''
    else:
        self.next_link = ''
        self.next_link_class = 'disabled'

    # Limit number of pages if search count is less than default number of pages
    if self.search_count < (MAX_LIST_ITEMS_PER_PAGE * MAX_PAGINATE_NUMBER):
        end_page = math.ceil(self.search_count / MAX_LIST_ITEMS_PER_PAGE)
        start_page = 1
    # Check if current page is greater than default page numbers
    elif self.current_page > MAX_PAGINATE_NUMBER:
        end_page = self.current_page
        start_page = self.current_page - MAX_PAGINATE_NUMBER + 1
    else:
        end_page = MAX_PAGINATE_NUMBER
        start_page = 1

    self.pages = list(range(start_page, end_page + 1))

    # check to see if there are previous records to show
    if self.current_page <= 1:
        self.previous_link = ''
        self.previous_link_class = 'disabled'
    else:
        self.previous_link = self.search_link + str(self.current_page - 1)
        self.previous_link_class = ''


def validate_response(self):
    if self.search_count == 0:
        self.error_message = EMPTY_SEARCH_RESULT
    else:
        pass


def create_search_link(self):
    self.search_link += '?search_param=' + self.search_param + '&search_type=' + self.search_type + '&page='


class GeneralSearchListView(ListView):
    # need initialisation
    model = Model
    template_name = ''
    page_icon = ''
    page_title = ''
    search_link = ''
    error_message = ''

    search_type = DEFAULT_SEARCH_TYPE
    search_param = ''
    search_count = 0
    search_labels = {}
    current_page = 1
    searches = []

    pages = []
    next_link = ''
    next_link_class = ''
    previous_link = ''
    previous_link_class = ''

    def initialise_form(self, request):
        if request.POST:
            data = request.POST
        elif request.GET:
            data = request.GET
        else:
            return None

        return GeneralSearchForm(data=data,
                                 placeholder='Search ' + self.page_title,
                                 form_action=self.search_link,
                                 act_search_type_label_var_name='act_search_type_label',
                                 search_key_values_var_name='search_type_labels')

    def return_values(self, request, form):
        validate_response(self)

        return render(request, self.template_name,
                      {'form': form,
                       'search_link': self.search_link,
                       'searches': self.searches,
                       'search_type_labels': self.search_labels,
                       'act_search_type_label': self.search_labels.get(self.search_type),
                       'pages': self.pages,
                       'page_title': self.page_title,
                       'page_icon': self.page_icon,
                       'current_page': self.current_page,
                       'error_message': self.error_message,
                       'next_link': self.next_link,
                       'next_link_class': self.next_link_class,
                       'previous_link': self.previous_link,
                       'previous_link_class': self.previous_link_class,
                       })

    def search_matches(self, search_type, search_param):
        if self.model == Patient:
            search_query = {
                '1': self.model.objects.filter(last_name__icontains=search_param).order_by('first_name'),
                '2': self.model.objects.filter(first_name__icontains=search_param).order_by('last_name'),
                '3': self.model.objects.filter(birth_date__iexact=search_param).order_by('last_name'),
            }
        elif self.model == MedicalRecord:
            search_query = {
                '1': self.model.objects.filter(patient__last_name__icontains=search_param).order_by('-recorded_date'),
                '2': self.model.objects.filter(recorded_by__last_name__icontains=search_param).order_by(
                    '-recorded_date'),
                '3': self.model.objects.filter(recorded_date__iexact=search_param).order_by('-recorded_date')
            }
        else:
            search_query = {
                '1': self.model.objects.filter(medical_record__patient__last_name__icontains=search_param).order_by(
                    '-recorded_date'),
                '2': self.model.objects.filter(recorded_by__last_name__icontains=search_param).order_by(
                    '-recorded_date'),
                '3': self.model.objects.filter(recorded_date__iexact=search_param).order_by('-recorded_date')
            }

        try:
            query_set = search_query.get(search_type)
            self.search_count = query_set.count()

            return query_set
        except KeyError:
            self.error_message = INVALID_SEARCH_TYPE
            return None

    def get(self, request, *args, **kwargs):
        form = self.initialise_form(request)

        if form is not None and form.is_valid():
            self.search_type = form.cleaned_data['search_type']
            self.search_param = form.cleaned_data['search_param']

            create_search_link(self)

            if self.search_param:
                results = self.search_matches(self.search_type, self.search_param)
            else:
                results = self.model.objects.all().order_by('-id')

            paginator = Paginator(results, MAX_LIST_ITEMS_PER_PAGE)

            if request.GET.get('page'):
                page = request.GET.get('page')
                try:
                    self.searches = paginator.page(page)
                    self.current_page = int(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    self.searches = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    self.searches = paginator.page(paginator.num_pages)
            else:
                self.current_page = 1
                self.searches = paginator.page(1)

            modify_page_links(self)

            return self.return_values(request, form)
        else:
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

    def post(self, request, *args, **kwargs):
        form = self.initialise_form(request)

        if form.is_valid() and not None:
            self.current_page = 1
            self.search_type = form.cleaned_data['search_type']
            self.search_param = form.cleaned_data['search_param']

            create_search_link(self)

            if self.search_param:
                self.searches = self.search_matches(self.search_type, self.search_param)[:MAX_LIST_ITEMS_PER_PAGE]
            else:
                self.searches = self.model.objects.all().order_by('-recorded_date')[:MAX_LIST_ITEMS_PER_PAGE]

            modify_page_links(self)

            return self.return_values(request, form)
        else:
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

    def __init__(self, model, page_icon, page_title, search_link, template_name, search_labels, **kwargs):
        super(GeneralSearchListView, self).__init__(**kwargs)

        self.model = model
        self.page_icon = page_icon
        self.page_title = page_title
        self.search_link = search_link
        self.template_name = template_name
        self.search_labels = search_labels

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(GeneralSearchListView, self).dispatch(request, *args, **kwargs)
