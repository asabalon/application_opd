# form python library
import logging
import datetime

# form third-party applications
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Reset
from django.forms import ModelForm, ValidationError
from django_countries.widgets import CountrySelectWidget
from django.utils.timezone import localtime, now

# from main application
from opd_application.messages import INVALID_BIRTH_DATE_VALUE
from opd_application.models.patient_models import Patient
from opd_application.widgets import SubmitButton, CustomPhoneNumberPrefixWidget

logger = logging.getLogger(__name__)


class PatientForm(ModelForm):
    """
        Form for new patient registration.
    """

    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.layout = Layout(
        Fieldset(
            'Patient Registration',
            'photo',
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
            Submit('submit', 'Register'),
            Reset('reset', 'Clear', css_class='btn-default'),
            SubmitButton('cancel', 'Cancel', css_class='btn-default'),
        )
    )

    class Meta:
        model = Patient
        fields = [
            'photo',
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
                layout="""
                    <div class="media">
                        <div class="media-left">
                            <img class="country-select-flag" id="{flag_id}" style="margin: 6px 4px 0" src="{country.flag}">
                        </div>
                        <div class="media-body">
                            {widget}
                        </div>
                    </div>
                """),
            'contact_number': CustomPhoneNumberPrefixWidget(initial='PH', ),
        }

    # class Media:
    #    js = {'custom/js/form_event_actions.js'}

    def clean_birth_date(self):
        """
            Checks if birth_date value is not a future date
            :raises:    ValidationError
            :return:   valid birth_date
        """

        sent_date = self.cleaned_data['birth_date']
        current_date = localtime(now()).date()

        if (sent_date - current_date) > datetime.timedelta(seconds=1):
            raise ValidationError(INVALID_BIRTH_DATE_VALUE)
        else:
            return sent_date

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.fields['address_street'].label = 'Street Address'
        self.fields['address_district'].label = 'Barangay/District'
        self.fields['address_city'].label = 'City/Municipality'
        self.fields['address_province'].label = 'Province'
        self.fields['address_postal'].label = 'Postal/Zip Code'
        self.fields['address_country'].label = 'Country'


class PatientEditForm(PatientForm):
    """
        Form for updating an existing patient's information.
    """
    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.layout = Layout(
        Fieldset(
            'Patient Update',
            'photo',
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
            Submit('submit', 'Update'),
            SubmitButton('cancel', 'Cancel', css_class='btn-default'),
        )
    )
