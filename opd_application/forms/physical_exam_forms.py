# from python library
import logging

# from third-party applications
from crispy_forms.bootstrap import FormActions, Div
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Reset
from django.forms import Form, CharField, HiddenInput, BooleanField, Textarea, ModelChoiceField, \
    ModelMultipleChoiceField, CheckboxSelectMultiple

# from main application
from opd_application.models.physical_exam_models import RateChoice, RhythmChoice, EENTChoice, LungChoice, AbdomenChoice, \
    ExtremitiesChoice
from opd_application.widgets import SubmitButton

logger = logging.getLogger(__name__)


class PhysicalExamForm(Form):
    """
        Form for creating a physical exam record for a specific medical record
    """
    medical_record = CharField(max_length=25, widget=HiddenInput)

    t_reading = CharField(max_length=25, required=False)
    bp_reading = CharField(max_length=25, required=False)
    pr_reading = CharField(max_length=25, required=False)
    rr_reading = CharField(max_length=25, required=False)

    pallor = BooleanField(required=False)

    heart_remarks = CharField(max_length=100, widget=Textarea(attrs={'style': 'height: 5em;', }),
                              required=False)

    rate_results = ModelChoiceField(queryset=RateChoice.objects.all(), required=False)

    rhythm_results = ModelChoiceField(queryset=RhythmChoice.objects.all(), required=False)

    eent_results = ModelMultipleChoiceField(widget=CheckboxSelectMultiple,
                                            queryset=EENTChoice.objects.all(), required=False)

    lung_results = ModelMultipleChoiceField(widget=CheckboxSelectMultiple,
                                            queryset=LungChoice.objects.all(), required=False)
    lung_remarks = CharField(max_length=100, widget=Textarea(attrs={'style': 'height: 5em;', }),
                             required=False)

    abdomen_results = ModelMultipleChoiceField(widget=CheckboxSelectMultiple,
                                               queryset=AbdomenChoice.objects.all(), required=False)
    abdomen_remarks = CharField(max_length=100, widget=Textarea(attrs={'style': 'height: 5em;', }),
                                required=False)

    extremities_results = ModelMultipleChoiceField(widget=CheckboxSelectMultiple,
                                                   queryset=ExtremitiesChoice.objects.all(), required=False)
    extremities_remarks = CharField(max_length=100, widget=Textarea(attrs={'style': 'height: 15em;', }),
                                    required=False)

    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Fieldset(
            'Physical Exam Record Creation',
        ),
        'medical_record',
        Div(
            Div('bp_reading', css_class='col-xs-offset-1 col-xs-4'),
            Div('pr_reading', css_class='col-xs-offset-2 col-xs-4'),
            css_class='form-group row'
        ),
        Div(
            Div('rr_reading', css_class='col-xs-offset-1 col-xs-4'),
            Div('t_reading', css_class='col-xs-offset-2 col-xs-4'),
            css_class='form-group row'
        ),
        'heart_remarks',
        'rate_results',
        'rhythm_results',
        'pallor',
        'eent_results',
        Div(
            Div('lung_results', css_class='col-xs-6'),
            Div('lung_remarks', css_class='col-xs-6'),
            css_class='form-group row'
        ),
        Div(
            Div('abdomen_results', css_class='col-xs-6'),
            Div('abdomen_remarks', css_class='col-xs-6'),
            css_class='form-group row'
        ),
        Div(
            Div('extremities_results', css_class='col-xs-6'),
            Div('extremities_remarks', css_class='col-xs-6'),
            css_class='form-group row'
        ),
        FormActions(
            Submit('submit', 'Record'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
            SubmitButton('cancel', 'Cancel', css_class='btn-default'),
        )
    )

    # class Media:
    #    js = {'custom/js/form_event_actions.js'}

    def __init__(self, *args, **kwargs):
        super(PhysicalExamForm, self).__init__(*args, **kwargs)
        self.fields['bp_reading'].label = "Blood Pressure (mm Hg)"
        self.fields['pr_reading'].label = "PR Reading (unit)"
        self.fields['rr_reading'].label = "RR Reading (unit)"
        self.fields['t_reading'].label = "T Reading (unit)"
        self.fields['eent_results'].label = "EENT Findings"
        self.fields['lung_results'].label = "Lung Findings"
        self.fields['lung_remarks'].label = "Remarks"
        self.fields['heart_remarks'].label = "Heart Findings"
        self.fields['rate_results'].label = "Rate Findings"
        self.fields['rhythm_results'].label = "Rhythm Findings"
        self.fields['abdomen_results'].label = "Abdomen Findings"
        self.fields['abdomen_remarks'].label = "Remarks"
        self.fields['extremities_results'].label = "Extremities Findings"
        self.fields['extremities_remarks'].label = "Remarks"
