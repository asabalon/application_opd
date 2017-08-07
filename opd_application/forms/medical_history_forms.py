# form python library
import logging

# form third-party applications
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django.forms import ModelForm, HiddenInput, CharField, ValidationError

# from main application
from opd_application.messages import INVALID_MEDICAL_HISTORY_DETAIL_VALUE
from opd_application.models.medical_history_models import MedicalHistoryDetail
from opd_application.widgets import FixedInputWidget

logger = logging.getLogger(__name__)


class MedicalHistoryDetailForm(ModelForm):
    """
    Form for creating a new medical history detail record for a specific medical history record
    """
    medical_history_category_detail_display = CharField(max_length=100, widget=FixedInputWidget(), required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_tag = False
    helper.layout = Layout(
        Div(
            Div('medical_history_category_detail_display', css_class='col-xs-4'),
            Div('value', css_class='col-xs-offset-2 col-xs-5'),
            css_class='form-group row'
        ),
        'medical_history_category_detail',
    )

    class Meta:
        model = MedicalHistoryDetail
        fields = [
            'medical_history_category_detail',
            'value',
        ]
        widgets = {
            'medical_history_category_detail': HiddenInput(),
        }

    def clean_value(self):
        """
        Checks if value given is valid for given category unit
        :raises:    ValidationError
        :returns:   valid value
        """

        input_value = self.cleaned_data['value']
        medical_history_category_detail = self.cleaned_data['medical_history_category_detail']

        if not input_value:
            logger.info('Skipping validation due to blank input')
            return input_value

        logger.info('Checking if input value needs to be validated')
        if medical_history_category_detail.medical_history_category_unit.is_validatable:
            logger.info('Validating input value [%s]' % input_value)
            try:
                int(input_value)

                logger.info('Input value [%s] passed validation' % input_value)
                return input_value
            except ValueError:
                logger.exception(INVALID_MEDICAL_HISTORY_DETAIL_VALUE)
                raise ValidationError(INVALID_MEDICAL_HISTORY_DETAIL_VALUE)
        else:
            logger.info('Input value [%s] does not require validation', input_value)
            return input_value

    def __init__(self, *args, **kwargs):
        super(MedicalHistoryDetailForm, self).__init__(*args, **kwargs)
        self.fields['medical_history_category_detail_display'].label = ""
        self.fields['value'].label = ""
