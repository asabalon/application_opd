# form python library
import logging

# from third-party applications
from crispy_forms.bootstrap import Div, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
from django.forms import Form, CharField, HiddenInput, ValidationError

# from main application
from opd_application.constants import VALID_SEARCH_TYPES, DEFAULT_SEARCH_TYPE
from opd_application.messages import INVALID_SEARCH_TYPE

logger = logging.getLogger(__name__)


class GeneralSearchForm(Form):
    """
        Form for handling general search queries.
    """

    # search_type value determines what kind of search to be made
    search_type = CharField(max_length=1, required=True,
                            widget=HiddenInput(attrs={'name': 'search_type', 'value': DEFAULT_SEARCH_TYPE}))

    # search_param value is used to make queries depending on search_type value
    search_param = CharField(max_length=100, required=False, widget=InlineField(
        attrs={'name': 'search_param'}), label='')

    def __init__(self, placeholder, form_action, act_search_type_label_var_name,
                 search_key_values_var_name, *args, **kwargs):
        super(GeneralSearchForm, self).__init__(*args, **kwargs)

        self.fields['search_param'].widget.attrs['placeholder'] = placeholder

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Submit('submit', 'Search', css_class='btn'),
                    HTML
                    ("""
                        <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
                                aria-haspopup="true" aria-expanded="false">
                            <span id="search_type_label">{{""" + act_search_type_label_var_name + """}}</span>
                            <span class="caret"></span>
                        </button>
                        <ol id="search_type_list" class="dropdown-menu">
                            {% for key, value in """ + search_key_values_var_name + """.items %}
                            <li id="search_type_item_{{ key }}">
                                <a href="#" onclick="change_search_type('{{ key }}', '{{ value }}', 'search_type_item_{{ key }}')">{{ value }}</a>
                            </li>
                            {% empty %}
                                <li>NONE</li>
                            {% endfor %}
                        </ol>
                    """),
                    css_class='input-group-btn'),
                'search_param',
                css_class='input-group'),
            'search_type',
        )

    def clean_search_type(self):
        """
            Checks if search_type value is valid
            :raises:    ValidationError
            :returns:   valid search_type
        """

        search_type = self.cleaned_data['search_type']

        if search_type not in VALID_SEARCH_TYPES:
            logger.exception('Invalid search_type value passed.')
            raise ValidationError(INVALID_SEARCH_TYPE)
        else:
            logger.info('Valid search_type value passed.')
            return search_type
