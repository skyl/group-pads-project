from pads.models import Pad, TextArea, TextAreaRevision
from django.contrib import admin

class PadAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'modified', 'created')
admin.site.register(Pad, PadAdmin)

class TextAreaAdmin(admin.ModelAdmin):
    list_display = ('pad', 'content', 'editor', 'edit_time')
admin.site.register(TextArea, TextAreaAdmin)

class TextAreaRevisionAdmin(admin.ModelAdmin):
    list_display = ('pad_guid', 'content', 'editor', 'edit_time')
admin.site.register(TextAreaRevision, TextAreaRevisionAdmin)


