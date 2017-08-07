# from python library
import logging

# form third-party applications
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.forms import ModelForm, HiddenInput, Select, Textarea

# from main application
from opd_application.models.diagnosis_models import DiagnosisCategoryChoice, DiagnosisEntry, DiagnosisCategory
from opd_application.widgets import NonInputWidget
from opd_application.functions import log_start_time, log_end_time

logger = logging.getLogger(__name__)


class DiagnosisEntryForm(ModelForm):
    """
    Form for creating a new diagnosis entry record for a specific diagnosis record
    """

    class Meta:
        model = DiagnosisEntry
        fields = [
            'diagnosis_category',
            'value',
            'remark',
        ]
        widgets = {
            'diagnosis_category': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Retrieves initial data for diagnosis category choices during form creation. However, data is retrieved from
        [data] instead of [initial] in kwargs after performing form validation
        :param args:    variable arguments
        :param kwargs:  named arguments
        """

        super(DiagnosisEntryForm, self).__init__(*args, **kwargs)

        log_start_time()

        choice_list = None

        logger.info('Setting default label and widget for value and remark fields')
        self.fields['value'].label = ''
        self.fields['remark'].label = ''
        self.fields['value'].widget = NonInputWidget()
        self.fields['remark'].widget = NonInputWidget()

        logger.info('Retrieving diagnosis category')
        if kwargs.get('data'):
            logger.info('Performing initial form creation')
            diagnosis_category = DiagnosisCategory.objects.get(
                pk=kwargs.get('data')['%s-diagnosis_category' % kwargs.get('prefix')])
        elif kwargs.get('initial'):
            logger.info('Performed form validation')
            diagnosis_category = kwargs.get('initial')['diagnosis_category']
        else:
            logger.warn('Did not receive value for required diagnosis_category parameter')
            diagnosis_category = None

        if diagnosis_category:
            logger.info('Setting label for value field using [%s]' % diagnosis_category)
            self.fields['value'].label = diagnosis_category

            logger.info('Instantiating form helper for [%s]' % diagnosis_category)
            self.helper = DiagnosisCategoryFormHelper(diagnosis_category)

            logger.info('Retrieving choices from database for [%s]' % diagnosis_category)
            choice_list = DiagnosisCategoryChoice.objects.filter(
                diagnosis_category=diagnosis_category).order_by('order')
        else:
            logger.warn('diagnosis_category is none or empty')

        if choice_list:
            logger.info(
                'Creating dropdown widget for value field using retrieved choices for [%s]' % diagnosis_category)
            self.fields['value'].widget = Select(choices=list(choice_list.values_list('description',
                                                                                      'description')))

            logger.info('Checking if list for [%s] contains a general term' % diagnosis_category)
            for choice in choice_list:
                if choice.is_general_term:
                    logger.info('Setting CSS class and widget for [%s]' % choice)
                    self.fields['remark'].widget = Textarea(
                        attrs={'placeholder': 'Additional Information', 'style': 'height: 5em;', })
                else:
                    pass
        else:
            logger.info('No choice list found for [%s]' % diagnosis_category)

        log_end_time()


class DiagnosisCategoryFormHelper(FormHelper):
    """
    Form helper for DiagnosisEntryForm. This helper will be instantiated upon receiving initial or validated values from
    created formset.
    """

    MAX_BOOTSTRAP_COLUMN_WIDTH = 6

    def __init__(self, diagnosis_category, *args, **kwargs):
        """
        Initialises form helper depending on the level of DiagnosisCategory model instance.
        :param diagnosis_category:  DiagnosisCategory model instance
        :param args:                variable arguments
        :param kwargs:              named arguments
        """

        super(DiagnosisCategoryFormHelper, self).__init__(*args, **kwargs)

        log_start_time()

        logger.info('Creating form helper for [%s] with level [%s]' % (diagnosis_category, diagnosis_category.level))
        self.form_class = 'form-horizontal'
        self.label_class = 'inline_form_label col-xs-offset-%s col-xs-%s' % (
            diagnosis_category.level, self.MAX_BOOTSTRAP_COLUMN_WIDTH - int(diagnosis_category.level))
        self.field_class = 'col-xs-6'
        self.form_tag = False
        self.layout = Layout(
            'diagnosis_category',
            'value',
            'remark',
        )
        self.render_required_fields = True

        log_end_time()
