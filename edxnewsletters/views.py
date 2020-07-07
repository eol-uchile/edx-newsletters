#!/usr/bin/env python
# -- coding: utf-8 --

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.http import HttpResponse
from urllib.parse import urlencode
from itertools import cycle
from .models import EdxNewslettersSuscribed
import json
import requests
import uuid
import logging
import sys
import unicodecsv as csv
import re

logger = logging.getLogger(__name__)
regex = r'^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$'


class Content(object):
    def validate_data(self, request, lista_email, context):
        """
            Validate if the entered data is valid
        """
        email_malos = ""
        # validacion de los email
        for email in lista_email:
            try:
                if not re.match(regex, email):
                    email_malos += email + " - "
            except Exception:
                email_malos += email + " - "

        email_malos = email_malos[:-3]

        # si existe email malo
        if email_malos != "":
            context['email_malos'] = email_malos

        # si no se ingreso email
        if not lista_email:
            context['no_email'] = ''

        return context

    def get_or_create_EdxNewslettersSuscribed(self, email):
        """
            Get or create EdxNewslettersSuscribed
        """
        try:
            edx_email = EdxNewslettersSuscribed.objects.get(email=email)
        except EdxNewslettersSuscribed.DoesNotExist:
            edx_email = EdxNewslettersSuscribed.objects.create(email=email)
        return edx_email

    def suscribe_email(self, lista_email, suscribed):
        """
            Suscribe(True) or Unsuscribe email(False)
        """
        email_suscribed = ""
        # guarda el form
        with transaction.atomic():
            for email in lista_email:
                edx_email = self.get_or_create_EdxNewslettersSuscribed(email)
                edx_email.suscribed = suscribed
                edx_email.save()
                email_suscribed += email + " - "

        email_suscribed = email_suscribed[:-3]
        return {
            'emails': '',
            'saved': 'saved',
            'suscribed': suscribed,
            'email_suscribed': email_suscribed}


class EdxNewslettersSuscribe(Content, View):
    """
        Suscribe email
    """

    def get(self, request):
        context = {'emails': '', 'suscribed': True}
        return render(request, 'edxnewsletters/staff.html', context)

    def post(self, request):
        lista_email = request.POST.get("emails", "").split('\n')
        # limpieza de los email ingresados
        lista_email = [email.lower() for email in lista_email]
        lista_email = [email.strip() for email in lista_email]
        lista_email = [email for email in lista_email if email]

        context = {
            'emails': request.POST.get('emails'), 'suscribed': True
        }
        # validacion de datos
        context = self.validate_data(request, lista_email, context)
        # retorna si hubo al menos un error
        if len(context) > 2:
            return render(request, 'edxnewsletters/staff.html', context)
        context = self.suscribe_email(lista_email, True)
        return render(request, 'edxnewsletters/staff.html', context)


class EdxNewslettersUnsuscribe(Content, View):
    """
        Unsuscribe email
    """

    def get(self, request):
        context = {'emails': '', 'suscribed': False}
        return render(request, 'edxnewsletters/staff.html', context)

    def post(self, request):
        lista_email = request.POST.get("emails", "").split('\n')
        # limpieza de los email ingresados
        lista_email = [email.lower() for email in lista_email]
        lista_email = [email.strip() for email in lista_email]
        lista_email = [email for email in lista_email if email]

        context = {
            'emails': request.POST.get('emails'), 'suscribed': False
        }
        # validacion de datos
        context = self.validate_data(request, lista_email, context)
        # retorna si hubo al menos un error
        if len(context) > 2:
            return render(request, 'edxnewsletters/staff.html', context)
        context = self.suscribe_email(lista_email, False)
        return render(request, 'edxnewsletters/staff.html', context)


class EdxNewslettersEmails(View):
    """
        Export all emails suscribed to csv file
    """

    def get(self, request):
        data = [[]]
        users = User.objects.all().order_by(
            'email').values('email')
        unsuscribed = EdxNewslettersSuscribed.objects.filter(
            suscribed=False).values('email')
        un_email = [email['email'] for email in unsuscribed]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="emails.csv"'
        writer = csv.writer(
            response,
            delimiter=';',
            dialect='excel',
            encoding='utf-8')

        data[0] = ['Email']
        i = 1
        aux = [[user['email']]
               for user in users if user['email'] not in un_email]
        data.extend(aux)
        writer.writerows(data)

        return response
