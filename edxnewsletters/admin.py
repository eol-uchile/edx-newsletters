
from django.contrib import admin

# Register your models here.
from .models import EdxNewslettersSuscribed


class EdxNewslettersSuscribedAdmin(admin.ModelAdmin):
    list_display = ('email', 'suscribed')
    search_fields = ['email', 'suscribed']


admin.site.register(EdxNewslettersSuscribed, EdxNewslettersSuscribedAdmin)
