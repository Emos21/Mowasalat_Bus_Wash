from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

@admin.register(Site, Location, TypeofWash, Timestamp, Task, WorkDoneDamages,Profile,Configurations)
class ViewAdmin(ImportExportModelAdmin):
    pass
