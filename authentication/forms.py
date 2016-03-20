from authentication import messages, constants
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Reset
from datetime import timedelta
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.timezone import localtime, now

from .models import User


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.layout = Layout(
        Fieldset(
            'User Registration',
            'first_name',
            'middle_name',
            'last_name',
            'birth_date',
            'email',
            'password',
            'confirm_password',
        ),
        FormActions(
            Submit('submit', 'Register', css_class='btn btn-primary'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
        )
    )

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'birth_date', 'email', 'password']
        widgets = {
            'birth_date': DateTimePicker(options={
                'format': 'MM/DD/YYYY',
                'pickSeconds': False
            }),
            'password': forms.PasswordInput,
        }

    # class Media:
    #    js = {'custom/js/form_event_actions.js'}

    def clean_birth_date(self):
        sent_date = self.cleaned_data['birth_date']
        current_date = localtime(now()).date()

        if (sent_date - current_date) > timedelta(seconds=1):
            raise forms.ValidationError(messages.INVALID_BIRTH_DATE_VALUE)
        # TODO: Create Legal Age Validator
        else:
            pass

        return sent_date

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if (password != confirm_password):
            raise forms.ValidationError(messages.PASSWORD_MISMATCH)
        else:
            pass

        return password

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


class LoginForm(AuthenticationForm):
    helper = FormHelper()
    helper.form_method = "POST"
    helper.form_action = ''
    helper.layout = Layout(
        Fieldset(
            'User Login',
            'username',
            'password',
        ),
        FormActions(
            Submit('submit', 'Login', css_class='btn btn-primary'),
            Reset('reset', 'Clear', css_class='btn btn-default'),
        )
    )

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.EmailInput,
        }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Email Address"
