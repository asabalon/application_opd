# from python library
import logging

# form third-party applications
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django.forms import ModelForm, BooleanField, CharField, HiddenInput

# from main application
from opd_application.models.prescription_models import PrescriptionEntry
from opd_application.widgets import FixedInputWidget
from opd_application.functions import log_start_time, log_end_time

logger = logging.getLogger(__name__)


class PrescriptionEntryForm(ModelForm):
    """
    Form for creating a new diagnosis entry record for a specific diagnosis record
    """

    prescribe = BooleanField(required=False)
    medicine_label = CharField(max_length=50, widget=FixedInputWidget())

    class Meta:
        model = PrescriptionEntry
        fields = [
            'medicine',
            'dosage',
            'package',
            'frequency',
            'designated_time',
        ]
        widgets = {
            'medicine': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PrescriptionEntryForm, self).__init__(*args, **kwargs)
        self.fields['dosage'].label = ''
        self.fields['package'].label = ''
        self.fields['frequency'].label = ''
        self.fields['designated_time'].label = ''
        self.fields['prescribe'].label = ''
        self.fields['medicine_label'].label = ''

        self.helper = PrescriptionEntryFormHelper()


class PrescriptionEntryFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PrescriptionEntryFormHelper, self).__init__(*args, **kwargs)

        log_start_time()

        self.form_class = 'form-horizontal'
        self.form_tag = False
        self.layout = Layout(
            Div(
                Div(
                    Div(
                        Div('prescribe', css_class='col-xs-1'),
                        Div('medicine_label', css_class='col-xs-10'),
                        css_class='row'),
                    css_class='container col-xs-3'),
                Div('dosage', css_class='col-xs-1'),
                Div('package', css_class='col-xs-offset-1 col-xs-1'),
                Div('frequency', css_class='col-xs-offset-1 col-xs-2'),
                Div('designated_time', css_class='col-xs-offset-1 col-xs-2'),
                css_class='form-group row'
            ),
            'medicine',
        )
        self.render_required_fields = True

        log_end_time()
