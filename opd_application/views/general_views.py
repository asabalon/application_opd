# from python library
import logging
import urllib.parse

# from third-party applications
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.urls.exceptions import NoReverseMatch
from django.views.generic import ListView

# from main application
from opd_application.forms.general_forms import GeneralSearchForm
from opd_application.constants import MAX_LIST_ITEMS_PER_PAGE, MAX_PAGINATE_NUMBER, DEFAULT_SEARCH_TYPE, \
    DASHBOARD_PAGE_NAME, LOGIN_PAGE_NAME, MEDICAL_RECORD_PAGE_ICON
from opd_application.models.patient_models import Patient
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.messages import EMPTY_SEARCH_RESULT, INVALID_SEARCH_TYPE, INVALID_SEARCH_PARAMETER_VALUE
from opd_application.functions import log_start_time, log_end_time

logger = logging.getLogger(__name__)

DISABLED_LINK_CLASS = 'disabled'
PAGE_PARAMETER_SUFFIX = '&page='


def modify_page_links(view, paginator):
    """
    Function for setting links and classes for paginator buttons in list view.
    :param view:        View instance
    :param paginator:   Paginator instance
    :return:            None
    """

    log_start_time()

    search_link = view.search_link + PAGE_PARAMETER_SUFFIX

    if int(view.current_page) < int(paginator.num_pages):
        logger.info('Paginator number of pages is greater than current page value')
        view.next_link = search_link + str(view.current_page + 1)
        view.next_link_class = ''
    else:
        logger.info('Paginator number of pages is less than current page value')
        view.next_link = None
        view.next_link_class = DISABLED_LINK_CLASS

    if int(paginator.num_pages) < MAX_PAGINATE_NUMBER:
        logger.info('Limiting links to number of paginator pages')
        end_page = paginator.num_pages
        start_page = 1
    elif int(view.current_page) > MAX_PAGINATE_NUMBER:
        logger.info('Changing lower limit for paginator links')
        end_page = view.current_page
        start_page = view.current_page - MAX_PAGINATE_NUMBER + 1
    else:
        logger.info('Number of paginator pages is greater than default number of search pages')
        end_page = MAX_PAGINATE_NUMBER
        start_page = 1

    if view.current_page <= 1:
        logger.info('Current page is the lower limit for paginator links')
        view.previous_link = None
        view.previous_link_class = DISABLED_LINK_CLASS
    else:
        logger.info('Changing previous link button class to show previous batch of results')
        view.previous_link = search_link + str(view.current_page - 1)
        view.previous_link_class = ''

    view.pages = list(range(start_page, end_page + 1))

    log_end_time()


def validate_response(view):
    """
    Function that performs all validation on view instance and sets error messages accordingly
    :param view:    View instance
    :return:        None
    """
    log_start_time()

    if view.search_count < 1:
        logger.info('Search returned an emtpy list')
        view.error_message = EMPTY_SEARCH_RESULT
    else:
        logger.info('Records found for received search category and search parameter')

    log_end_time()


def select_search_results(view, request, paginator):
    """
    Function for retrieving value of [page] parameter in URI.
    :param view:        View instance
    :param request:     HttpRequest instance
    :param paginator:   Paginator instance
    :return:            None
    """

    log_start_time()

    if request.POST:
        logger.info('Defaulting to first page because of POST request')
        view.current_page = 1
        view.searches = paginator.page(1)
    elif request.GET.get('page'):
        logger.info('Retrieved value for page parameter')
        page = request.GET.get('page')
        try:
            logger.info('Retrieving results based on retrieved page value')
            view.searches = paginator.page(page)
            view.current_page = int(page)
        except PageNotAnInteger:
            logger.warn('Provided value for page parameter cannot be converted to int')
            view.error_message = INVALID_SEARCH_PARAMETER_VALUE
            view.searches = paginator.page(1)
        except EmptyPage:
            logger.warn('Provided value for page parameter is out of bounds for paginator')
            view.error_message = INVALID_SEARCH_PARAMETER_VALUE
            view.searches = paginator.page(paginator.num_pages)
    else:
        logger.info('Did not receive page parameter')
        view.current_page = 1
        view.searches = paginator.page(1)

    log_end_time()


def create_link(page_name, arg_value_pair):
    """
    Function for creating a link using a page name. Query string will be appended if provided
    :param page_name:       valid and registered page name
    :param arg_value_pair:  key-value pair inside a dictionary
    :return:                created link in string
    """

    log_start_time()

    link = ''

    try:
        logger.info('Creating link for [%s]' % page_name)
        if page_name:
            link = reverse_lazy(page_name)
            logger.info('Created link is [%s]' % link)
        else:
            logger.info('Received empty value for page_name')

        if arg_value_pair and isinstance(arg_value_pair, dict):
            logger.info('Creating query string using arg_value_pair')
            link += '?%s' % urllib.parse.urlencode(arg_value_pair)
        else:
            logger.info('No value for arg_value_pair found')
    except NoReverseMatch:
        logger.warn('Cannot create link for [%s]' % page_name)
        link = ''

    logger.info('Full link created [%s]' % link)
    log_end_time()
    return link


def initialise_form(view, request):
    """
    Function for instantiating GeneralSearchForm
    :param view:    View instance
    :param request: HttpRequest instance
    :return:        GeneralSearchForm instance
    """

    log_start_time()

    if request.POST:
        logger.info('Received a POST request')
        data = request.POST
    elif request.GET:
        logger.info('Received a GET request')
        data = request.GET
    else:
        logger.info('Did not receive a GET or a POST request')
        return None

    log_end_time()

    return GeneralSearchForm(data=data,
                             placeholder='Search ' + view.page_title,
                             form_action=view.search_link,
                             act_search_type_label_var_name='act_search_type_label',
                             search_key_values_var_name='search_type_labels')


def search_matches(view, search_type, search_param):
    """
    Function for retrieving records based on model type and search parameters.
    :param view:
    :param search_type:
    :param search_param:
    :return:
    """

    log_start_time()

    query_set = None

    if view.model == Patient:
        search_query = {
            '1': view.model.objects.filter(last_name__icontains=search_param).order_by('first_name'),
            '2': view.model.objects.filter(first_name__icontains=search_param).order_by('last_name'),
            '3': view.model.objects.filter(birth_date__icontains=search_param).order_by('last_name'),
        }
    elif view.model == MedicalRecord:
        search_query = {
            '1': view.model.objects.filter(patient__last_name__icontains=search_param).order_by('-recorded_date'),
            '2': view.model.objects.filter(recorded_by__last_name__icontains=search_param).order_by(
                '-recorded_date'),
            '3': view.model.objects.filter(recorded_date__icontains=search_param).order_by('-recorded_date')
        }
    else:
        search_query = {
            '1': view.model.objects.filter(medical_record__patient__last_name__icontains=search_param).order_by(
                '-recorded_date'),
            '2': view.model.objects.filter(recorded_by__last_name__icontains=search_param).order_by(
                '-recorded_date'),
            '3': view.model.objects.filter(recorded_date__icontains=search_param).order_by('-recorded_date')
        }

    try:
        logger.info('Retrieving record for model [%s] with search type [%s] and search parameter [%s]' % (
            view.model, search_type, search_param))
        query_set = search_query.get(search_type)
        view.search_count = query_set.count()
    except KeyError:
        logger.warn('Received invalid search type and search parameter')
        view.error_message = INVALID_SEARCH_TYPE

    return query_set


class GeneralListView(ListView):
    """
    View for displaying all patient's record information for a specified record type. Requires a related medical record
    for retrieval. Uses only GET function to display all records for chosen medical record.
    """

    pages = []
    searches = []
    current_page = 1
    error_message = None
    search_link = ''
    search_count = 0
    next_link = None
    next_link_class = None
    previous_link = None
    previous_link_class = None

    # subclass-supplied properties
    left_link_page_name = None
    left_link_icon = None
    left_link_name = None
    right_link_page_name = None
    right_link_icon = None
    right_link_name = None
    add_page_name = None
    page_icon = None
    page_title = None
    list_page_name = None

    def get(self, request, *args, **kwargs):
        """
        Retrieves records from database using value of [medical] argument from URI. Uses a default list
        page template.
        :param request: HttpRequest
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse
        """

        log_start_time()

        context = {}

        logger.info('Retrieving medical record id from request URI')
        patient_id = request.GET.get('patient')
        medical_record_id = request.GET.get('medical')

        if medical_record_id:
            medical_record = MedicalRecord.objects.get(pk=request.GET.get('medical'))
            patient = medical_record.patient
            logger.info('Retrieving records using medical record id value [%s]' % medical_record.id)
            result_list = self.model.objects.filter(medical_record=medical_record).order_by('-recorded_date')
            self.search_link = create_link(self.list_page_name, {'medical': medical_record.id})
            context.update({'left_link': create_link(self.left_link_page_name, {'medical': medical_record.id}),
                            'left_link_icon': self.left_link_icon,
                            'left_link_name': self.left_link_name,
                            'center_link': medical_record.get_absolute_url(),
                            'center_link_icon': MEDICAL_RECORD_PAGE_ICON,
                            'center_link_name': 'Medical Record',
                            'right_link': create_link(self.right_link_page_name, {'medical': medical_record.id}),
                            'right_link_icon': self.right_link_icon,
                            'right_link_name': self.right_link_name,
                            'add_link': create_link(self.add_page_name, {'medical': medical_record.id}),
                            })
        elif patient_id:
            patient = Patient.objects.get(pk=request.GET.get('patient'))
            logger.info('Retrieving records using patient id value [%s]' % patient.id)
            result_list = self.model.objects.filter(patient=patient).order_by('-recorded_date')
            self.search_link = create_link(self.list_page_name, {'patient': patient.id})
            context.update({'add_link': create_link(self.add_page_name, {'patient': patient.id}), })
        else:
            logger.warn('Did not receive value for required medical parameter')
            return redirect(DASHBOARD_PAGE_NAME, permanent=True)

        paginator = Paginator(result_list, MAX_LIST_ITEMS_PER_PAGE)
        self.search_count = result_list.count()

        logger.info('Calling common functions for listing results')
        select_search_results(self, request, paginator)
        modify_page_links(self, paginator)
        validate_response(self)

        context.update({'searches': self.searches,
                        'patient': patient,
                        'pages': self.pages,
                        'search_link': self.search_link,
                        'error_message': self.error_message,
                        'page_title': self.page_title,
                        'page_icon': self.page_icon,
                        'current_page': self.current_page,
                        'next_link': self.next_link,
                        'next_link_class': self.next_link_class,
                        'previous_link': self.previous_link,
                        'previous_link_class': self.previous_link_class, })

        log_end_time()

        return render(request, self.template_name, context)

    def __init__(self, model, template_name, left_link_page_name, left_link_icon, left_link_name, right_link_page_name,
                 right_link_icon, right_link_name, add_page_name, page_icon, page_title, list_page_name, **kwargs):
        super(GeneralListView, self).__init__(**kwargs)
        self.model = model
        self.template_name = template_name
        self.left_link_page_name = left_link_page_name
        self.left_link_icon = left_link_icon
        self.left_link_name = left_link_name
        self.right_link_page_name = right_link_page_name
        self.right_link_icon = right_link_icon
        self.right_link_name = right_link_name
        self.add_page_name = add_page_name
        self.page_icon = page_icon
        self.page_title = page_title
        self.list_page_name = list_page_name

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(GeneralListView, self).dispatch(request, *args, **kwargs)


class GeneralSearchListView(GeneralListView):
    """
    View for displaying all record information for a specific search query. Uses POST
    function to display initial search results. GET function is used to display results for a given
    page number. Extends GeneralListView.
    """

    search_type = DEFAULT_SEARCH_TYPE
    search_param = ''
    search_labels = {}

    def process_search(self, request):
        """
        Receives either POST or GET request then proceeds to search records depending on search query
        :param request: HttpRequest instance
        :return:        HttpResponse instance
        """
        log_start_time()

        form = initialise_form(self, request)

        if form is not None and form.is_valid():
            logger.info('Received a valid form')
            self.search_type = form.cleaned_data['search_type']
            self.search_param = form.cleaned_data['search_param']

            logger.info('Creating search link using page name [%s]' % self.list_page_name)
            self.search_link = create_link(self.list_page_name,
                                           {'search_param': self.search_param, 'search_type': self.search_type})

            if self.search_param:
                logger.info('Received a non-empty search parameter')
                results = search_matches(self, self.search_type, self.search_param)
            else:
                logger.info('Did not receive a valid search parameter')
                results = self.model.objects.all().order_by('-id')

            paginator = Paginator(results, MAX_LIST_ITEMS_PER_PAGE)

            logger.info('Calling common functions for listing records')
            select_search_results(self, request, paginator)
            modify_page_links(self, paginator)
            validate_response(self)

            response = render(request, self.template_name,
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
        else:
            response = redirect(DASHBOARD_PAGE_NAME, permanent=True)

        log_end_time()
        return response

    def get(self, request, *args, **kwargs):
        logger.info('Processing GET request')
        return self.process_search(request)

    def post(self, request, *args, **kwargs):
        logger.info('Processing POST request')
        return self.process_search(request)

    def __init__(self, model, page_icon, page_title, list_page_name, template_name, search_labels, **kwargs):
        super(GeneralSearchListView, self).__init__(model, template_name, None, None, None, None, None, None, None,
                                                    page_icon, page_title, list_page_name, **kwargs)
        self.search_labels = search_labels


@method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
def dispatch(self, request, *args, **kwargs):
    return super(GeneralSearchListView, self).dispatch(request, *args, **kwargs)
