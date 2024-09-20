from django.contrib import admin
from .models import Film, Genre, Genesummary, Genecounts, Transcriptcounts
#from import_export.admin import ImportExportModelAdmin
#from .resource import ReportResource  

admin.site.register(Film)
admin.site.register(Genre)

#class ReportAdmin(ImportExportModelAdmin):
#     resource_class = ReportResource      
#admin.site.register(GeneSummary, ReportAdmin)


@admin.register(Genesummary)
class GenesummaryAdmin(admin.ModelAdmin):
   list_display=['geneName','totalNum','novelNum']

@admin.register(Genecounts)
class GenecountsAdmin(admin.ModelAdmin):
   list_display=['sampleID','geneName','counts', 'group', 'sex']

@admin.register(Transcriptcounts)
class TranscriptcountsAdmin(admin.ModelAdmin):
   list_display=['sampleID','geneName','isoform','counts', 'group', 'sex']
