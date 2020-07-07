from django.contrib import admin
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from .views import *


urlpatterns = [url('^emails/$',
                   staff_member_required(EdxNewslettersEmails.as_view()),
                   name='email'),
               url('^suscribe/$',
                   staff_member_required(EdxNewslettersSuscribe.as_view()),
                   name='suscribe'),
               url('^unsuscribe/$',
                   staff_member_required(EdxNewslettersUnsuscribe.as_view()),
                   name='unsuscribe'),
               ]
