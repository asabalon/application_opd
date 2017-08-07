# from python library
import logging

# from third-party applications
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

# from main application
from opd_application.constants import DASHBOARD_PAGE_NAME, DASHBOARD_TEMPLATE, DEFAULT_SEARCH_CATEGORY, LIST_OFFSET, \
    LOGIN_PAGE_NAME, PAGE_ICONS, PAGE_LABELS, PATIENT_SEARCH_TYPE_LABEL, GENERAL_SEARCH_TYPE_LABEL, SEARCH_VIEW_LINKS, \
    PATIENT_FORM_PAGE_NAME
from opd_application.forms.general_forms import GeneralSearchForm
from opd_application.functions import log_start_time, log_end_time
from opd_application.constants import DEFAULT_SEARCH_TYPE

logger = logging.getLogger(__name__)


class DashboardView(TemplateView):
    """
    View for rendering a page that contains links to different types of records and registrations.
    """

    view_link = reverse_lazy(DASHBOARD_PAGE_NAME)
    template_name = DASHBOARD_TEMPLATE

    def get(self, request, *args, **kwargs):
        """
        Packages page icons and page labels for links available in the dashboard page
        :param request: HttpRequest instance
        :param args:    variable arguments
        :param kwargs:  named arguments
        :return:        HttpResponse instance
        """
        log_start_time()

        icons_labels_zip = zip(PAGE_ICONS, PAGE_LABELS)

        # will default to searching Patient
        if request.GET.get('search_category'):
            search_category = request.GET.get('search_category')
        else:
            search_category = DEFAULT_SEARCH_CATEGORY

        if search_category == DEFAULT_SEARCH_CATEGORY:
            search_type_labels = PATIENT_SEARCH_TYPE_LABEL
        else:
            search_type_labels = GENERAL_SEARCH_TYPE_LABEL

        log_end_time()

        return render(request, self.template_name,
                      {'form': GeneralSearchForm(
                          placeholder='Search ' + PAGE_LABELS[int(search_category) - LIST_OFFSET],
                          form_action=SEARCH_VIEW_LINKS.get(search_category),
                          act_search_type_label_var_name='act_search_type_label',
                          search_key_values_var_name='search_type_labels'),
                          'act_search_type_label': search_type_labels.get(DEFAULT_SEARCH_TYPE),
                          'icons_labels_zip': icons_labels_zip, 'view_link': self.view_link,
                          'search_category': int(search_category),
                          'search_type_labels': search_type_labels,
                          'add_link': reverse_lazy(PATIENT_FORM_PAGE_NAME),
                          'search_category_param': '?search_category='})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)
