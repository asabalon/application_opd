from django.contrib import admin

from .models import *


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

@admin.register(MedicalHistoryCategoryDetailKey)
class MedicalHistoryCategoryDetailKeyAdmin(admin.ModelAdmin):
    pass
