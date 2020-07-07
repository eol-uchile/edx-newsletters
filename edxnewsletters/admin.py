
from django.contrib import admin

# Register your models here.
from .models import EdxNewslettersUnsuscribed


class EdxNewslettersUnsuscribedAdmin(admin.ModelAdmin):
    list_display = ('get_mail',)
    search_fields = ['user_email__email']
    def get_mail(self, obj):
        return obj.user_email.email
    get_mail.admin_order_field  = 'user_email__email'  #Allows column order sorting
    get_mail.short_description = 'Correo Usuario'  #Renames column head
admin.site.register(EdxNewslettersUnsuscribed, EdxNewslettersUnsuscribedAdmin)
