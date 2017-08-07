# form python library
import logging

# form third-party applications
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Reset
from django.forms import ModelForm, CharField, TextInput, HiddenInput, Textarea, CheckboxSelectMultiple

# from main application
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.widgets import SubmitButton

logger = logging.getLogger(__name__)


class MedicalRecordForm(ModelForm):
    """
        Form for creating a medical record for a particular patient
    """

    # a read-only input field for display purposes only
    patient_name = CharField(max_length=100, widget=TextInput(attrs={'readonly': 'readonly'}),
                             required=False)

    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Fieldset(
            'Medical Record Creation',
        ),
        'patient_name',
        'patient',
        'complaint',
        'additional_info',
        FormActions(
            Submit('submit', 'Record'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
            SubmitButton('cancel', 'Cancel', css_class='btn-default'),
        )
    )

    class Meta:
        model = MedicalRecord
        fields = [
            'patient',
            'complaint',
            'additional_info',
        ]
        widgets = {
            'patient': HiddenInput,
            'complaint': CheckboxSelectMultiple,
            'additional_info': Textarea(attrs={'style': 'height: 5em;', }),
        }

    def __init__(self, *args, **kwargs):
        super(MedicalRecordForm, self).__init__(*args, **kwargs)
        self.fields['complaint'].label = "Chief Complaint"
        self.fields['additional_info'].label = "Additional Information"


class MedicalRecordEditForm(MedicalRecordForm):
    """
        Form for updating one of an existing patient's medical records
    """
    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Fieldset(
            'Medical Record Update',
        ),
        'patient_name',
        'patient',
        'complaint',
        'additional_info',
        FormActions(
            Submit('submit', 'Save Changes'),
            SubmitButton('cancel', 'Cancel', css_class='btn-default'),
        )
    )
