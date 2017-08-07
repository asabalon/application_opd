# from python library
import logging

# form third-party applications
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django.forms import ModelForm

# from main application
from opd_application.models.medication_models import MedicationEntry
from opd_application.functions import log_start_time, log_end_time
from opd_application.widgets import SubmitButton

logger = logging.getLogger(__name__)


class MedicationForm(ModelForm):
    """
    Form for creating a new diagnosis entry record for a specific diagnosis record
    """

    class Meta:
        model = MedicationEntry
        fields = [
            'description',
            'dosage',
            'package',
            'frequency',
            'designated_time',
        ]

    def __init__(self, *args, **kwargs):
        super(MedicationForm, self).__init__(*args, **kwargs)
        self.fields['dosage'].label = ''
        self.fields['package'].label = ''
        self.fields['frequency'].label = ''
        self.fields['designated_time'].label = ''
        self.fields['description'].label = ''

        self.helper = MedicationFormHelper()


class MedicationFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(MedicationFormHelper, self).__init__(*args, **kwargs)

        log_start_time()

        self.form_class = 'form-horizontal'
        self.form_tag = False
        self.layout = Layout(
            Div(
                Div('description', css_class='col-xs-3'),
                Div('dosage', css_class='col-xs-offset-0-2-5 col-xs-1'),
                Div('package', css_class='col-xs-offset-0-2-5 col-xs-1'),
                Div('frequency', css_class='col-xs-offset-0-2-5 col-xs-2'),
                Div('designated_time', css_class='col-xs-offset-0-2-5 col-xs-2'),
                Div('DELETE', css_class='col-xs-offset-0-2-5 col-xs-1'),
                css_class='form-group row'
            ),
        )
        self.render_required_fields = True

        log_end_time()
