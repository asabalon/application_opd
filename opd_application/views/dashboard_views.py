import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from opd_application.constants import *
from opd_application.forms import *
from opd_application.views import general_views

# TODO: Add Python Documentation
# TODO: Add Logging

logger = logging.getLogger(__name__)

class DashboardView(TemplateView):
    view_link = reverse_lazy(DASHBOARD_PAGE_NAME)
    template_name = DASHBOARD_TEMPLATE

    def get(self, request, *args, **kwargs):
        icons_labels_zip = zip(PAGE_ICONS, PAGE_LABELS)

        if request.GET.get('search_category'):
            search_category = request.GET.get('search_category')
        else:
            search_category = DEFAULT_SEARCH_CATEGORY

        if search_category == DEFAULT_SEARCH_CATEGORY:
            search_type_labels = general_views.PATIENT_SEARCH_TYPE_LABEL
        else:
            search_type_labels = general_views.GENERAL_SEARCH_TYPE_LABEL

        return render(request, self.template_name,
                      {'form': GeneralSearchForm(
                          placeholder='Search ' + PAGE_LABELS[int(search_category) - LIST_OFFSET],
                          form_action=general_views.SEARCH_VIEW_LINKS.get(search_category),
                          act_search_type_label_var_name='act_search_type_label',
                          search_key_values_var_name='search_type_labels'),
                          'act_search_type_label': search_type_labels.get(general_views.DEFAULT_SEARCH_TYPE),
                          'icons_labels_zip': icons_labels_zip, 'view_link': self.view_link,
                          'search_category': int(search_category),
                          'search_type_labels': search_type_labels})

    @method_decorator(login_required(login_url=LOGIN_PAGE_NAME))
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)
