from django.contrib import admin
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from .views import *


urlpatterns = [url('^emails/$',
                   staff_member_required(EdxNewslettersEmails.as_view()),
                   name='email'),
               url('^subscribe/$',
                   staff_member_required(EdxNewslettersSuscribe.as_view()),
                   name='suscribe'),
               url('^unsubscribe/$',
                   EdxNewslettersUnsuscribe.as_view(),
                   name='unsuscribe'),
               ]
