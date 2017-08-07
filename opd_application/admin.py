# from third-party applications
from django.contrib import admin

# from main application
from opd_application.models.diagnosis_models import DiagnosisCategory, DiagnosisCategoryChoice
from opd_application.models.laboratory_models import LaboratoryTest, LaboratoryTestDetail, LaboratoryMeasurementUnit, \
    LaboratoryTestDetailChoice
from opd_application.models.medical_record_models import Complaint
from opd_application.models.medical_history_models import MedicalHistoryCategory, MedicalHistoryCategoryDetail, \
    MedicalHistoryCategoryUnit
from opd_application.models.physical_exam_models import EENTChoice, LungChoice, RateChoice, RhythmChoice, AbdomenChoice, \
    ExtremitiesChoice, PhysicalExamKey
from opd_application.models.prescription_models import Medicine, DesignatedTime, Package, Frequency
from opd_application.models.models import Dosage, Package, Frequency, DesignatedTime

"""
Registering models to make them available in admin site
"""


@admin.register(Complaint)
class ComplainAdmin(admin.ModelAdmin):
    pass


@admin.register(EENTChoice)
class EENTChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(LungChoice)
class LungChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(RateChoice)
class RateChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(RhythmChoice)
class RhythmChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(AbdomenChoice)
class AbdomenChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ExtremitiesChoice)
class ExtremitiesChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(PhysicalExamKey)
class PhysicalExamKeyAdmin(admin.ModelAdmin):
    pass


@admin.register(MedicalHistoryCategory)
class MedicalHistoryCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(MedicalHistoryCategoryUnit)
class MedicalHistoryCategoryUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(MedicalHistoryCategoryDetail)
class MedicalHistoryCategoryDetailAdmin(admin.ModelAdmin):
    pass


@admin.register(LaboratoryTest)
class LaboratoryTestAdmin(admin.ModelAdmin):
    pass


@admin.register(LaboratoryTestDetail)
class LaboratoryTestDetailAdmin(admin.ModelAdmin):
    pass


@admin.register(LaboratoryMeasurementUnit)
class LaboratoryMeasurementUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(LaboratoryTestDetailChoice)
class LaboratoryTestDetailChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(DiagnosisCategory)
class DiagnosisCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(DiagnosisCategoryChoice)
class DiagnosisCategoryChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    pass


@admin.register(Dosage)
class DosageAdmin(admin.ModelAdmin):
    pass


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    pass


@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    pass


@admin.register(DesignatedTime)
class DesignatedTimeAdmin(admin.ModelAdmin):
    pass
