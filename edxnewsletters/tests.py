#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch, Mock, MagicMock
from collections import namedtuple
from django.urls import reverse
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User
from urllib.parse import parse_qs
from student.tests.factories import UserFactory
from xmodule.modulestore import ModuleStoreEnum
import re
import json
import urllib.parse
from .views import EdxNewslettersSuscribe, EdxNewslettersUnsuscribe, EdxNewslettersEmails
from .models import EdxNewslettersSuscribed
# Create your tests here.


class TestEdxNewslettersSuscribe(TestCase):

    def setUp(self):
        with patch('student.models.cc.User.save'):
            # staff user
            self.client = Client()
            user = UserFactory(
                username='testuser',
                password='12345',
                email='staff@edx.org',
                is_staff=True)
            self.client.login(username='testuser', password='12345')
            # student user
            self.st_client = Client()
            st_user = UserFactory(
                username='testuser2',
                password='12345',
                email='student@edx.org')
            self.st_client.login(username='testuser2', password='12345')
            self.anm_client = Client()

    def test_get_suscribed(self):
        """
            Test suscribe get normal process
        """
        response = self.client.get(reverse('edxnewsletters-data:suscribe'))
        request = response.request
        self.assertEquals(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/suscribe/')

    def test_get_suscribed_student(self):
        """
            Test suscribe with anonymous user
        """
        response = self.st_client.get(reverse('edxnewsletters-data:suscribe'))
        request = response.request
        self.assertEquals(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/suscribe/')

    def test_get_suscribed_anonymous(self):
        """
            Test suscribe get with anonymous user
        """
        response = self.anm_client.get(reverse('edxnewsletters-data:suscribe'))
        request = response.request
        self.assertEquals(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/suscribe/')

    def test_suscribed_staff_post(self):
        """
            Test suscribed normal process
        """
        post_data = {
            'emails': 'test@test.cl'
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_suscribed\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 1)
        self.assertEqual(emails_scb[0].email, 'test@test.cl')
        self.assertEqual(emails_scb[0].suscribed, True)

    def test_suscribed_staff_post_exists(self):
        """
            Test suscribed with exists email db
        """
        post_data = {
            'emails': 'test3@test.cl'
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        EdxNewslettersSuscribed.objects.create(
            email='test3@test.cl', suscribed=False)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_suscribed\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 1)
        self.assertEqual(emails_scb[0].email, 'test3@test.cl')
        self.assertEqual(emails_scb[0].suscribed, True)

    def test_suscribed_staff_post_multipe_emails(self):
        """
            Test suscribed with multiple email
        """
        post_data = {
            'emails': 'test@test.cl\ntest2@test.cl\ntest3@test.cl\ntest4@test.cl'}
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_suscribed\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 4)
        self.assertEqual(emails_scb[0].email, 'test@test.cl')
        self.assertEqual(emails_scb[0].suscribed, True)
        self.assertEqual(emails_scb[3].email, 'test4@test.cl')
        self.assertEqual(emails_scb[3].suscribed, True)

    def test_suscribed_staff_post_no_email(self):
        """
            Test suscribed with no email
        """
        post_data = {
            'emails': ''
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id=\"no_email\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)

    def test_suscribed_staff_post_wrong_email(self):
        """
            Test suscribed with wrong email
        """
        post_data = {
            'emails': 'adsdsad'
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:suscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_malos\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)


class TestEdxNewslettersUnsuscribe(TestCase):

    def setUp(self):
        with patch('student.models.cc.User.save'):
            # staff user
            self.client = Client()
            user = UserFactory(
                username='testuser',
                password='12345',
                email='staff@edx.org',
                is_staff=True)
            self.client.login(username='testuser', password='12345')
            # student user
            self.st_client = Client()
            st_user = UserFactory(
                username='testuser2',
                password='12345',
                email='student@edx.org')
            self.st_client.login(username='testuser2', password='12345')
            self.anm_client = Client()

    def test_get_unsuscribed(self):
        """
            Test unsuscribe get normal process
        """
        response = self.client.get(reverse('edxnewsletters-data:unsuscribe'))
        request = response.request
        self.assertEquals(response.status_code, 200)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/unsuscribe/')

    def test_get_unsuscribed_student(self):
        """
            Test unsuscribe with student user
        """
        response = self.st_client.get(
            reverse('edxnewsletters-data:unsuscribe'))
        request = response.request
        self.assertEquals(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/unsuscribe/')

    def test_get_unsuscribed_anonymous(self):
        """
            Test unsuscribe with anonymous user
        """
        response = self.anm_client.get(
            reverse('edxnewsletters-data:unsuscribe'))
        request = response.request
        self.assertEquals(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/unsuscribe/')

    def test_unsuscribed_staff_post(self):
        """
            Test unsuscribed normal process
        """
        post_data = {
            'emails': 'test@test.cl'
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_suscribed\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 1)
        self.assertEqual(emails_scb[0].email, 'test@test.cl')
        self.assertEqual(emails_scb[0].suscribed, False)

    def test_unsuscribed_staff_post_exists(self):
        """
            Test unsuscribed with exists email db
        """
        post_data = {
            'emails': 'test@test.cl'
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        EdxNewslettersSuscribed.objects.create(
            email='test@test.cl', suscribed=True)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_suscribed\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 1)
        self.assertEqual(emails_scb[0].email, 'test@test.cl')
        self.assertEqual(emails_scb[0].suscribed, False)

    def test_unsuscribed_staff_post_multipe_emails(self):
        """
            Test unsuscribed with multiple email
        """
        post_data = {
            'emails': 'test@test.cl\ntest2@test.cl\ntest3@test.cl\ntest4@test.cl'}
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_suscribed\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 4)
        self.assertEqual(emails_scb[0].email, 'test@test.cl')
        self.assertEqual(emails_scb[0].suscribed, False)
        self.assertEqual(emails_scb[3].email, 'test4@test.cl')
        self.assertEqual(emails_scb[3].suscribed, False)

    def test_unsuscribed_staff_post_no_email(self):
        """
            Test unsuscribed with no email
        """
        post_data = {
            'emails': ''
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id=\"no_email\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)

    def test_unsuscribed_staff_post_wrong_email(self):
        """
            Test unsuscribed with wrong email
        """
        post_data = {
            'emails': 'adsdsad'
        }
        self.assertEqual(EdxNewslettersSuscribed.objects.all().count(), 0)
        response = self.client.post(
            reverse('edxnewsletters-data:unsuscribe'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "id=\"email_malos\"" in response._container[0].decode())
        emails_scb = EdxNewslettersSuscribed.objects.all()
        self.assertEqual(emails_scb.count(), 0)


class TestEdxNewslettersEmails(TestCase):

    def setUp(self):
        with patch('student.models.cc.User.save'):
            # staff user
            self.client = Client()
            user = UserFactory(
                username='testuser',
                password='12345',
                email='staff@edx.org',
                is_staff=True)
            self.client.login(username='testuser', password='12345')
            # student user
            self.st_client = Client()
            st_user = UserFactory(
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
        self.assertEquals(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/emails/')

    def test_anonymous_export(self):
        """
            Test export with anonymous user
        """
        response = self.anm_client.get(
            reverse('edxnewsletters-data:email'))
        request = response.request
        self.assertEquals(response.status_code, 302)
        self.assertEqual(request['PATH_INFO'], '/edxnewsletters/emails/')

    def test_staff_export_unsuscribed_email(self):
        """
            Test export email without unsuscribed email
        """
        EdxNewslettersSuscribed.objects.create(
            email='student@edx.org', suscribed=False)
        self.assertEquals(EdxNewslettersSuscribed.objects.all().count(), 1)
        response = self.client.get(
            reverse('edxnewsletters-data:email'))
        data = response.content.decode().split("\r\n")
        self.assertEqual(data[0], "Email")
        self.assertEqual(data[1], "staff@edx.org")
        self.assertEqual(data[2], "")
