from authentication import messages, constants
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import FormActions, InlineCheckboxes, Div, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Reset, Button, HTML
from datetime import timedelta
from django import forms
from django_countries.widgets import CountrySelectWidget
from django.utils.timezone import localtime, now
from opd_application import messages

from .models import *

class GeneralSearchForm(forms.Form):
    search_type = forms.CharField(max_length=1, required=True,
                                  widget=forms.HiddenInput(
                                      attrs={'name': 'search_type', 'id': 'search_type'}))
    search_param = forms.CharField(max_length=100, required=False, widget=InlineField(
            attrs={'name': 'search_param', 'id': 'search_param', 'class': 'form-control'}))

    def __init__(self, placeholder, search_link, search_type_value, *args, **kwargs):
        super(GeneralSearchForm, self).__init__(*args, **kwargs)
        self.fields['search_param'].label = ''
        self.fields['search_param'].widget.attrs['placeholder'] = placeholder
        self.fields['search_type'].widget.attrs['value'] = search_type_value

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = search_link
        self.helper.layout = Layout(
            Div(
                Div(
                    Submit('submit', 'Search', css_class='btn'),
                    HTML("""
                        <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
                                aria-haspopup="true" aria-expanded="false">
                            <span id="search_type_label">{{ label }}</span>
                            <span class="caret"></span>
                        </button>
                        <ul class="dropdown-menu">
                            {% for key, value in search_label.items %}
                            <li><a href="#" onclick="change_search_type('{{ key }}', '{{ value }}')">{{ value }}</a></li>
                            {% empty %}
                            <li>NONE</li>
                            {% endfor %}
                        </ul>
                    """),
                    css_class='input-group-btn'),
                'search_param',
                css_class='input-group'),
            'search_type',
        )

    def clean_search_type(self):
        search_type = self.cleaned_data['search_type']

        if int(search_type) not in [1, 2, 3]:
            raise forms.ValidationError(messages.INVALID_SEARCH_TYPE)
        else:
            return search_type


class PatientSearchForm(forms.Form):
    search_type = forms.CharField(max_length=1, required=True,
                                  widget=forms.HiddenInput(
                                      attrs={'name': 'search_type', 'id': 'search_type', 'value': 1}))
    search_param = forms.CharField(max_length=100, required=False, widget=InlineField(
        attrs={'name': 'search_param', 'id': 'search_param', 'class': 'form-control', 'placeholder': 'Search Patient'}))

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy('opd:search_patient')
    helper.layout = Layout(
        Div(
            Div(
                Submit('submit', 'Search', css_class='btn'),
                HTML("""
                    <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
                            aria-haspopup="true" aria-expanded="false">
                        <span id="search_type_label">{{ label }}</span>
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        {% for key, value in search_label.items %}
                        <li><a href="#" onclick="change_search_type('{{ key }}', '{{ value }}')">{{ value }}</a></li>
                        {% empty %}
                        <li>NONE</li>
                        {% endfor %}
                    </ul>
                """),
                css_class='input-group-btn'),
            'search_param',
            css_class='input-group'),
        'search_type',
    )

    def __init__(self, *args, **kwargs):
        super(PatientSearchForm, self).__init__(*args, **kwargs)
        self.fields['search_param'].label = ''

    def clean_search_type(self):
        search_type = self.cleaned_data['search_type']

        if int(search_type) not in [1, 2, 3]:
            raise forms.ValidationError(messages.INVALID_SEARCH_TYPE)
        else:
            return search_type


class PatientForm(forms.ModelForm):
    contact_number = forms.RegexField(
        regex=r'^\d{10}$',
        error_messages={'invalid': messages.INVALID_CONTACT_NUMBER, 'required': messages.REQUIRED_CONTACT_NUMBER}
    )

    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.layout = Layout(
        Fieldset(
            'Patient Registration',
            'first_name',
            'middle_name',
            'last_name',
            'birth_date',
            'sex',
            'marital_status',
            'address_street',
            'address_district',
            'address_city',
            'address_province',
            'address_postal',
            'address_country',
            'contact_number',
        ),
        FormActions(
            Submit('submit', 'Register', css_class='btn btn-primary'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
        )
    )

    class Meta:
        model = Patient
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'birth_date',
            'sex',
            'marital_status',
            'address_street',
            'address_district',
            'address_city',
            'address_province',
            'address_postal',
            'address_country',
            'contact_number',
        ]
        widgets = {
            'birth_date': DateTimePicker(options={
                'format': 'MM/DD/YYYY',
                'pickSeconds': False
            }),
            'address_country': CountrySelectWidget(
                layout='{widget}<img class="country-select-flag" id="{flag_id}" style="margin: 6px 4px 0" src="{country.flag}">'),
        }

    # class Media:
    #    js = {'custom/js/form_event_actions.js'}

    def clean_birth_date(self):
        sent_date = self.cleaned_data['birth_date']
        current_date = localtime(now()).date()

        if (sent_date - current_date) > timedelta(seconds=1):
            raise forms.ValidationError(messages.INVALID_BIRTH_DATE_VALUE)
        else:
            return sent_date

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.fields['address_street'].label = 'Street Address'
        self.fields['address_district'].label = 'Barangay/District'
        self.fields['address_city'].label = 'City/Municipality'
        self.fields['address_province'].label = 'Province'
        self.fields['address_postal'].label = 'Postal/Zip Code'


class PhysicalExamForm(forms.Form):
    medical_record = forms.CharField(max_length=25, widget=forms.HiddenInput)

    t_reading = forms.CharField(max_length=25, required=False)
    bp_reading = forms.CharField(max_length=25, required=False)
    pr_reading = forms.CharField(max_length=25, required=False)
    rr_reading = forms.CharField(max_length=25, required=False)

    pallor = forms.BooleanField(required=False)

    heart_remarks = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'style': 'height: 5em;',}),
                                    required=False)

    rate_results = forms.ModelChoiceField(queryset=RateChoice.objects.all(), required=False)

    rhythm_results = forms.ModelChoiceField(queryset=RhythmChoice.objects.all(), required=False)

    eent_results = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                  queryset=EENTChoice.objects.all(), required=False)

    lung_results = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                  queryset=LungChoice.objects.all(), required=False)
    lung_remarks = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'style': 'height: 5em;',}),
                                   required=False)

    abdomen_results = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                     queryset=AbdomenChoice.objects.all(), required=False)
    abdomen_remarks = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'style': 'height: 5em;',}),
                                      required=False)

    extremities_results = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                         queryset=ExtremitiesChoice.objects.all(), required=False)
    extremities_remarks = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'style': 'height: 15em;',}),
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
            Submit('submit', 'Record', css_class='btn btn-primary'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
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


class MedicalRecordForm(forms.ModelForm):
    patient_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}),
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
            Submit('submit', 'Record', css_class='btn btn-primary'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
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
            'patient': forms.HiddenInput,
            'complaint': forms.CheckboxSelectMultiple,
            'additional_info': forms.Textarea(attrs={'style': 'height: 5em;',}),
        }

    def __init__(self, *args, **kwargs):
        super(MedicalRecordForm, self).__init__(*args, **kwargs)
        self.fields['complaint'].label = "Chief Complaint"
        self.fields['additional_info'].label = "Additional Information"
