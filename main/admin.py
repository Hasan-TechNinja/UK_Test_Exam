from django.contrib import admin
from . models import Theory, TheoryCategory

# Register your models here.

class TheoryModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'description', 'created', 'updated'
    )
admin.site.register(Theory, TheoryModelAdmin)

class TheoryCategoryModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'description', 'created'
    )
admin.site.register(TheoryCategory, TheoryCategoryModelAdmin)