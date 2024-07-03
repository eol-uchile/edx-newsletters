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
from .models import EdxNewslettersUnsuscribed
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
                    email_malos += email + " / "
            except Exception:
                email_malos += email + " / "

        email_malos = email_malos[:-3]

        # si existe email malo
        if email_malos != "":
            context['email_malos'] = email_malos

        # si no se ingreso email
        if not lista_email:
            context['no_email'] = ''

        return context

class EdxNewslettersSuscribe(Content, View):
    """
        Suscribe email
    """

    def get(self, request):
        context = {'emails': '', 'suscribed': True, 'staff': True}
        return render(request, 'edxnewsletters/staff.html', context)

    def post(self, request):
        
        lista_email = request.POST.get("emails", "").split('\n')
        # limpieza de los email ingresados
        lista_email = [email.lower() for email in lista_email]
        lista_email = [email.strip() for email in lista_email]
        lista_email = [email for email in lista_email if email]
        lista_email = lista_email[:50]
        context = {
            'emails': request.POST.get('emails'), 'suscribed': True, 'staff': True
        }
        # validacion de datos
        context = self.validate_data(request, lista_email, context)
        # retorna si hubo al menos un error
        if len(context) > 3:
            return render(request, 'edxnewsletters/staff.html', context)
        context = self.suscribe_email(lista_email)
        return render(request, 'edxnewsletters/staff.html', context)

    def suscribe_email(self, lista_email):
        """
            Suscribe email - delete email in EdxNewslettersUnsuscribed
        """
        email_suscribed = ""
        email_not_found = ""
        # guarda el form
        with transaction.atomic():
            for email in lista_email:
                try:
                    edx_email = EdxNewslettersUnsuscribed.objects.get(user_email__email=email)
                    edx_email.delete()
                    email_suscribed += email + " / "
                except EdxNewslettersUnsuscribed.DoesNotExist:
                    try:
                        user = User.objects.get(email=email)
                        email_suscribed += email + " / "
                    except User.DoesNotExist:
                        email_not_found += email + " / "
        email_suscribed = email_suscribed[:-3]
        email_not_found = email_not_found[:-3]
        return {
            'emails': '',
            'saved': 'saved',
            'staff': True,
            'suscribed': True,
            'email_modify': email_suscribed,
            'email_not_found': email_not_found}

class EdxNewslettersUnsuscribe(Content, View):
    """
        Unsuscribe email
    """

    def get(self, request):
        context = {'emails': '', 'suscribed': False, 'staff': request.user.is_staff}
        return render(request, 'edxnewsletters/staff.html', context)

    def post(self, request):
        access = request.user.is_staff
        if access:
            lista_email = request.POST.get("emails", "").split('\n')
            # limpieza de los email ingresados
            lista_email = [email.lower() for email in lista_email]
            lista_email = [email.strip() for email in lista_email]
            lista_email = [email for email in lista_email if email]
            lista_email = lista_email[:50]
        else:
            lista_email = [request.POST.get("emails", "").lower().strip()]
        context = {
            'emails': request.POST.get('emails'), 'suscribed': False, 'staff': access
        }
        # validacion de datos
        context = self.validate_data(request, lista_email, context)
        # retorna si hubo al menos un error
        if len(context) > 3:
            return render(request, 'edxnewsletters/staff.html', context)
        context = self.unsuscribe_email(lista_email, access)
        return render(request, 'edxnewsletters/staff.html', context)

    def unsuscribe_email(self, lista_email, access):
        """
            Unsuscribe email - Add email in EdxNewslettersUnsuscribed
        """
        email_unsuscribed = ""
        email_not_found = ""
        # guarda el form
        with transaction.atomic():
            for email in lista_email:
                try:
                    edx_email = EdxNewslettersUnsuscribed.objects.get(user_email__email=email)                    
                    email_unsuscribed += email + " / "
                except EdxNewslettersUnsuscribed.DoesNotExist:
                    try:
                        user = User.objects.get(email=email)
                        EdxNewslettersUnsuscribed.objects.create(user_email=user)
                        email_unsuscribed += email + " / "
                    except User.DoesNotExist:
                        email_not_found += email + " / "

        email_unsuscribed = email_unsuscribed[:-3]
        email_not_found = email_not_found[:-3]
        return {
            'emails': '',
            'staff': access,
            'saved': 'saved',
            'suscribed': False,
            'email_modify': email_unsuscribed,
            'email_not_found': email_not_found}

class EdxNewslettersEmails(View):
    """
        Export all emails suscribed to csv file
    """

    def get(self, request):
        data = [[]]
        users = User.objects.filter(is_active=True).exclude(id__in=EdxNewslettersUnsuscribed.objects.all().values('user_email')).order_by(
            'email').values('email')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="emails.csv"'
        writer = csv.writer(
            response,
            delimiter=';',
            dialect='excel',
            encoding='utf-8')

        data[0] = ['Email']
        aux = [[user['email']] for user in users]
        data.extend(aux)
        writer.writerows(data)

        return response
