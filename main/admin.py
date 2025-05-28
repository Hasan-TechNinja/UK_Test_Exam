from django.contrib import admin
from . models import Theory

# Register your models here.

class TheoryModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'description', 'created', 'updated'
    )
admin.site.register(Theory, TheoryModelAdmin)