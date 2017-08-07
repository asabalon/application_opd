from django.core.urlresolvers import reverse_lazy

# String Constants
DEFAULT_SEARCH_CATEGORY = '1'
DEFAULT_SEARCH_TYPE = '1'

LOGIN_PAGE_NAME = 'auth:login'

DASHBOARD_PAGE_NAME = 'opd:home'
DASHBOARD_TEMPLATE = 'dashboard.html'

PATIENT_PAGE_ICON = 'fa-user'
PATIENT_FORM_TEMPLATE = 'patient_form.html'
PATIENT_PROFILE_TEMPLATE = 'patient_profile.html'
PATIENT_SEARCH_LIST_TEMPLATE = 'patient_list.html'
PATIENT_FORM_PAGE_NAME = 'opd:record_patient'
PATIENT_PROFILE_PAGE_NAME = 'opd:profile'
PATIENT_SEARCH_LIST_PAGE_NAME = 'opd:search_patient'

MEDICAL_RECORD_PAGE_ICON = 'fa-list-alt'
MEDICAL_RECORD_FORM_TEMPLATE = 'medical_record_form.html'
MEDICAL_RECORD_LIST_TEMPLATE = 'medical_record_list.html'
MEDICAL_RECORD_PROFILE_TEMPLATE = 'medical_record_profile.html'
MEDICAL_RECORD_SEARCH_LIST_TEMPLATE = 'medical_record_search_list.html'
MEDICAL_RECORD_FORM_PAGE_NAME = 'opd:record_medical'
MEDICAL_RECORD_LIST_PAGE_NAME = 'opd:list_medical'
MEDICAL_RECORD_PROFILE_PAGE_NAME = 'opd:medical'
MEDICAL_RECORD_SEARCH_LIST_PAGE_NAME = 'opd:search_medical'

PHYSICAL_EXAM_PAGE_ICON = 'fa-heartbeat'
PHYSICAL_EXAM_FORM_TEMPLATE = 'physical_exam_form.html'
PHYSICAL_EXAM_LIST_TEMPLATE = 'physical_exam_list.html'
PHYSICAL_EXAM_PROFILE_TEMPLATE = 'physical_exam_profile.html'
PHYSICAL_EXAM_SEARCH_LIST_TEMPLATE = 'physical_exam_search_list.html'
PHYSICAL_EXAM_FORM_PAGE_NAME = 'opd:record_exam'
PHYSICAL_EXAM_LIST_PAGE_NAME = 'opd:list_exam'
PHYSICAL_EXAM_PROFILE_PAGE_NAME = 'opd:exam'
PHYSICAL_EXAM_SEARCH_LIST_PAGE_NAME = 'opd:search_exam'

MEDICAL_HISTORY_PAGE_ICON = 'fa-history'
MEDICAL_HISTORY_EDIT_PAGE_NAME = 'opd:edit_history'
MEDICAL_HISTORY_FORM_PAGE_NAME = 'opd:record_history'
MEDICAL_HISTORY_PROFILE_PAGE_NAME = 'opd:history'
MEDICAL_HISTORY_FORM_TEMPLATE = 'medical_history_form.html'
MEDICAL_HISTORY_PROFILE_TEMPLATE = 'medical_history_profile.html'

LABORATORY_PAGE_ICON = 'fa-flask'
LABORATORY_PROFILE_PAGE_NAME = 'opd:laboratory'
LABORATORY_FORM_TEMPLATE = 'laboratory_form.html'
LABORATORY_PROFILE_TEMPLATE = 'laboratory_profile.html'
LABORATORY_LIST_TEMPLATE = 'laboratory_list.html'
LABORATORY_FORM_PAGE_NAME = 'opd:record_laboratory'
LABORATORY_LIST_PAGE_NAME = 'opd:list_laboratory'
LABORATORY_SEARCH_PAGE_NAME = 'opd:laboratory_diagnosis'
LABORATORY_SEARCH_LIST_TEMPLATE = 'laboratory_search_list.html'
LABORATORY_EDIT_PAGE_NAME = 'opd:edit_laboratory'
LABORATORY_TEST_LIST_PAGE_NAME = 'opd:list_lab_test'
LABORATORY_TEST_LIST_TEMPLATE = 'laboratory_test_list.html'

DIAGNOSIS_PAGE_ICON = 'fa-stethoscope'
DIAGNOSIS_FORM_TEMPLATE = 'diagnosis_form.html'
DIAGNOSIS_PROFILE_PAGE_NAME = 'opd:diagnosis'
DIAGNOSIS_PROFILE_TEMPLATE = 'diagnosis_profile.html'
DIAGNOSIS_EDIT_PAGE_NAME = 'opd:edit_diagnosis'
DIAGNOSIS_LIST_TEMPLATE = 'diagnosis_list.html'
DIAGNOSIS_LIST_PAGE_NAME = 'opd:list_diagnosis'
DIAGNOSIS_FORM_PAGE_NAME = 'opd:record_diagnosis'
DIAGNOSIS_SEARCH_PAGE_NAME = 'opd:search_diagnosis'
DIAGNOSIS_SEARCH_LIST_TEMPLATE = 'diagnosis_search_list.html'

PRESCRIPTION_LIST_PAGE_NAME = 'opd:list_prescription'
PRESCRIPTION_LIST_TEMPLATE = 'prescription_list.html'
PRESCRIPTION_PAGE_ICON = 'fa-file-text-o'
PRESCRIPTION_FORM_TEMPLATE = 'prescription_form.html'
PRESCRIPTION_PROFILE_TEMPLATE = 'prescription_profile.html'
PRESCRIPTION_EDIT_PAGE_NAME = 'opd:edit_prescription'
PRESCRIPTION_PROFILE_PAGE_NAME = 'opd:prescription'
PRESCRIPTION_SEARCH_PAGE_NAME = 'opd:search_prescription'
PRESCRIPTION_SEARCH_LIST_TEMPLATE = 'prescription_search_list.html'

MEDICATION_FORM_TEMPLATE = 'medication_form.html'
MEDICATION_PAGE_ICON = 'fa-medkit'
MEDICATION_PROFILE_TEMPLATE = 'medication_profile.html'
MEDICATION_EDIT_PAGE_NAME = 'opd:edit_medication'
MEDICATION_PROFILE_PAGE_NAME = 'opd:medication'
MEDICATION_FORM_PAGE_NAME = 'opd:record_medication'

# Numeric Constants
LIST_OFFSET = 1

MAX_PAGINATE_NUMBER = 5

MAX_LIST_ITEMS_PER_PAGE = 1

MIN_AGE_REQUIREMENT = 18

# Collection Constants
GENERAL_SEARCH_TYPE_LABEL = {
    '1': 'by Patient Last Name',
    '2': 'by Encoder Last Name',
    '3': 'by Recorded Date',
}

PATIENT_SEARCH_TYPE_LABEL = {
    '1': 'by Last Name',
    '2': 'by First Name',
    '3': 'by Birth Date',
}

SEARCH_VIEW_LINKS = {
    '1': reverse_lazy('opd:search_patient'),
    '2': reverse_lazy('opd:search_medical'),
    '3': reverse_lazy('opd:search_exam'),
    '4': reverse_lazy('opd:search_laboratory'),
    '5': reverse_lazy('opd:search_diagnosis'),
    '6': reverse_lazy('opd:search_prescription'),
}

PAGE_ICONS = [PATIENT_PAGE_ICON, MEDICAL_RECORD_PAGE_ICON, PHYSICAL_EXAM_PAGE_ICON, LABORATORY_PAGE_ICON,
              DIAGNOSIS_PAGE_ICON, PRESCRIPTION_PAGE_ICON]
PAGE_LABELS = ['Patients', 'Medical Records', 'Physical Exams', 'Laboratory Results', 'Diagnoses', 'Prescriptions']

VALID_SEARCH_TYPES = ['1', '2', '3']
