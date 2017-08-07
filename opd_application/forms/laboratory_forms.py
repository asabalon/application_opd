# form python library
import logging

# form third-party applications
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django.forms import ModelForm, HiddenInput, CharField, ValidationError, Select

# from main application
from opd_application.messages import INVALID_LABORATORY_RESULT_VALUE
from opd_application.models.laboratory_models import LaboratoryResult, LaboratoryTestDetailChoice
from opd_application.widgets import FixedInputWidget

logger = logging.getLogger(__name__)


class LaboratoryResultForm(ModelForm):
    """
    Form for creating a new laboratory result record for a specific laboratory record
    """
    laboratory_test_detail_display = CharField(max_length=100, widget=FixedInputWidget(), required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_tag = False
    helper.layout = Layout(
        Div(
            Div('laboratory_test_detail_display', css_class='col-xs-4'),
            Div('value', css_class='col-xs-offset-2 col-xs-5'),
            css_class='form-group row'
        ),
        'laboratory_test_detail',
    )

    class Meta:
        model = LaboratoryResult
        fields = [
            'laboratory_test_detail',
            'value',
        ]
        widgets = {
            'laboratory_test_detail': HiddenInput(),
        }

    def clean_value(self):
        """
        Checks if value given is valid for given category unit
        :raises:    ValidationError
        :returns:   valid value
        """

        input_value = self.cleaned_data['value']
        laboratory_test_detail = self.cleaned_data['laboratory_test_detail']

        if not input_value:
            logger.info('Skipping validation due to blank input')
            return input_value

        logger.info('Checking if input value needs to be validated')
        if laboratory_test_detail.laboratory_measurement_unit.is_validatable:
            logger.info('Validating input value [%s]' % input_value)
            try:
                int(input_value)

                logger.info('Input value [%s] passed validation' % input_value)
                return input_value
            except ValueError:
                logger.exception(INVALID_LABORATORY_RESULT_VALUE)
                raise ValidationError(INVALID_LABORATORY_RESULT_VALUE)
        else:
            logger.info('Input value [%s] does not require validation', input_value)
            return input_value

    def __init__(self, *args, **kwargs):
        """
        Retrieves initial data for laboratory test detail choice retrieval. During validation, data is retrieved from
        [data] in kwargs
        :param args:    variable arguments
        :param kwargs:  named arguments
        """
        choice_list = None

        if kwargs.get('data'):
            laboratory_test_detail = kwargs.get('data')['%s-laboratory_test_detail' % kwargs.get('prefix')]
        elif kwargs.get('initial'):
            laboratory_test_detail = kwargs.get('initial')['laboratory_test_detail']
        else:
            laboratory_test_detail = None

        if laboratory_test_detail:
            choice_list = LaboratoryTestDetailChoice.objects.filter(
                laboratory_test_detail=laboratory_test_detail).values_list('description',
                                                                           'description')

        super(LaboratoryResultForm, self).__init__(*args, **kwargs)

        self.fields['laboratory_test_detail_display'].label = ""
        self.fields['value'].label = ""

        if choice_list:
            self.fields['value'].widget = Select(choices=list(choice_list))
