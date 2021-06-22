#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch, Mock, MagicMock
from collections import namedtuple
from django.urls import reverse
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User
from urllib.parse import parse_qs
from common.djangoapps.student.tests.factories import UserFactory
from xmodule.modulestore import ModuleStoreEnum
import re
import json
import urllib.parse
from .views import EdxNewslettersSuscribe, EdxNewslettersUnsuscribe, EdxNewslettersEmails
from .models import EdxNewslettersUnsuscribed
# Create your tests here.


class TestEdxNewslettersSuscribe(TestCase):

    def setUp(self):
        with patch('common.djangoapps.student.models.cc.User.save'):
            # staff user
            self.client = Client()
            self.user = UserFactory(
                username='testuser',
                password='12345',
                email='staff@edx.org',
                is_staff=True)
            self.client.login(username='testuser', password='12345')
            # student user
            self.st_client = Client()
            self.st_user = UserFactory(
                username='testuser2',
                password='12345',
                email='student@edx.org')
            self.st_client.login(username='testuser2', password='12345')

    def test_get_suscribed(self):
        """
            Test suscribe get normal process
        """
        response = self.client.get(reverse('edxnewsletters-data:suscribe'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/subscribe/')

    def test_get_suscribed_student(self):
        """
            Test suscribe with student user
        """
        response = self.st_client.get(reverse('edxnewsletters-data:suscribe'))
        request = response.request
        self.assertEqual(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/subscribe/')

    def test_suscribed_staff_post(self):
        """
            Test suscribed normal process
        """
        post_data = {
            'emails': self.user.email
        }
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_not_found\"" not in response._container[0].decode())
        self.assertTrue(
            "id=\"email_modify\"" in response._container[0].decode())
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)

    def test_suscribed_staff_post_exists(self):
        """
            Test suscribed with exists email db
        """
        post_data = {
            'emails': self.st_user.email
        }
        EdxNewslettersUnsuscribed.objects.create(user_email=self.st_user)
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 1)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_not_found\"" not in response._container[0].decode())
        self.assertTrue(
            "id=\"email_modify\"" in response._container[0].decode())
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)

    def test_suscribed_staff_post_multipe_emails(self):
        """
            Test suscribed with multiple email
        """
        post_data = {
            'emails': '{}\n{}'.format(self.st_user.email, self.user.email)}
        EdxNewslettersUnsuscribed.objects.create(user_email=self.st_user)
        EdxNewslettersUnsuscribed.objects.create(user_email=self.user)
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 2)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_modify\"" in response._container[0].decode())
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)

    def test_suscribed_staff_post_no_email(self):
        """
            Test suscribed with no email
        """
        post_data = {
            'emails': ''
        }
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id=\"no_email\"" in response._container[0].decode())
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)

    def test_suscribed_staff_post_wrong_email(self):
        """
            Test suscribed with wrong email
        """
        post_data = {
            'emails': 'adsdsad'
        }
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_malos\"" in response._container[0].decode())
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)

    def test_post_student_suscribed(self):
        """
            Test suscribe post with student user
        """
        post_data = {
            'emails': self.user.email
        }
        EdxNewslettersUnsuscribed.objects.create(user_email=self.user)
        response = self.st_client.get(reverse('edxnewsletters-data:suscribe'))
        request = response.request
        self.assertEqual(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/subscribe/')
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 1)
        self.assertEqual(emails_scb[0].user_email, self.user)

class TestEdxNewslettersUnsuscribe(TestCase):

    def setUp(self):
        with patch('common.djangoapps.student.models.cc.User.save'):
            # staff user
            self.client = Client()
            self.user = UserFactory(
                username='testuser',
                password='12345',
                email='staff@edx.org',
                is_staff=True)
            self.client.login(username='testuser', password='12345')
            # student user
            self.st_client = Client()
            self.st_user = UserFactory(
                username='testuser2',
                password='12345',
                email='student@edx.org')
            self.st_client.login(username='testuser2', password='12345')

    def test_get_unsuscribed(self):
        """
            Test unsuscribe get normal process
        """
        response = self.client.get(reverse('edxnewsletters-data:unsuscribe'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/unsubscribe/')

    def test_get_unsuscribed_student(self):
        """
            Test unsuscribe with student user
        """
        response = self.st_client.get(
            reverse('edxnewsletters-data:unsuscribe'))
        request = response.request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/unsubscribe/')

    def test_unsuscribed_student_post(self):
        """
            Test unsuscribed student post with email not found
        """
        post_data = {
            'emails': 'four0four@edx.org'
        }
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.st_client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_not_found\"" not in response._container[0].decode())
        self.assertTrue(
            "id=\"email_modify\"" not in response._container[0].decode())
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)

    def test_unsuscribed_staff_post_exists(self):
        """
            Test unsuscribed with exists email db
        """
        post_data = {
            'emails': self.st_user.email
        }
        EdxNewslettersUnsuscribed.objects.create(user_email=self.st_user)
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 1)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_not_found\"" not in response._container[0].decode())
        self.assertTrue(
            "id=\"email_modify\"" in response._container[0].decode())
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 1)
        self.assertEqual(emails_scb[0].user_email, self.st_user)

    def test_unsuscribed_staff_post_multipe_emails(self):
        """
            Test unsuscribed with multiple email
        """
        post_data = {
            'emails': '{}\n{}'.format(self.st_user.email, self.user.email)}
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_not_found\"" not in response._container[0].decode())
        self.assertTrue(
            "id=\"email_modify\"" in response._container[0].decode())
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 2)
        self.assertEqual(emails_scb[0].user_email, self.st_user)
        self.assertEqual(emails_scb[1].user_email, self.user)

    def test_unsuscribed_staff_post_no_email(self):
        """
            Test unsuscribed with no email
        """
        post_data = {
            'emails': ''
        }
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id=\"no_email\"" in response._container[0].decode())
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)

    def test_unsuscribed_staff_post_wrong_email(self):
        """
            Test unsuscribed with wrong email
        """
        post_data = {
            'emails': 'adsdsad'
        }
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_malos\"" in response._container[0].decode())
        emails_scb = EdxNewslettersUnsuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)


class TestEdxNewslettersEmails(TestCase):

    def setUp(self):
        with patch('common.djangoapps.student.models.cc.User.save'):
            # staff user
            self.client = Client()
            self.user = UserFactory(
                username='testuser',
                password='12345',
                email='staff@edx.org',
                is_staff=True)
            self.client.login(username='testuser', password='12345')
            # student user
            self.st_client = Client()
            self.st_user = UserFactory(
                username='testuser2',
                password='12345',
                email='student@edx.org')
            self.st_client.login(username='testuser2', password='12345')
            self.anm_client = Client()

    def test_staff_export(self):
        """
            Test normal process
        """
        response = self.client.get(
            reverse('edxnewsletters-data:email'))
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Email")
        self.assertEqual(data[1], "staff@edx.org")
        self.assertEqual(data[2], "student@edx.org")

    def test_student_export(self):
        """
            Test export with student user
        """
        response = self.st_client.get(
            reverse('edxnewsletters-data:email'))
        request = response.request
        data = response.content.decode()
        self.assertEqual(data, "")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/emails/')

    def test_anonymous_export(self):
        """
            Test export with anonymous user
        """
        response = self.anm_client.get(
            reverse('edxnewsletters-data:email'))
        request = response.request
        data = response.content.decode()
        self.assertEqual(data, "")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/emails/')

    def test_staff_export_unsuscribed_email(self):
        """
            Test export email without unsuscribed email
        """
        EdxNewslettersUnsuscribed.objects.create(user_email=self.st_user)
        self.assertEqual(EdxNewslettersUnsuscribed.objects.all().count(), 1)
        response = self.client.get(
            reverse('edxnewsletters-data:email'))
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Email")
        self.assertEqual(data[1], "staff@edx.org")
        self.assertEqual(data[2], "")
