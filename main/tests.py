from django.test import TestCase
from django.core.urlresolvers import reverse
import datetime

from main.models import Car, EngineType, CarType


class ClockTestCase(TestCase):
    fixtures = ['test']


    def get_page(self, url):
        """ Ensures given url returns HTTP 200. """
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response

    def page_redirect(self, url):
        """ Ensure given url returns HTTP 302 """
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        return response

    def page_404(self, url):
        """ Ensure given url returns HTTP 404 """
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        return response

    def login(self):
        login = self.client.login(username='admin', password='admin')
        self.assertEqual(login, True)

    def logout(self):
        self.client.logout()

    def test_homepage(self):
        self.get_page(reverse('main:index'))

    def test_car_list_good(self):
        self.get_page(reverse('main:car_list_default'))
        self.get_page(reverse('main:car_list', kwargs={'page': 1}))

    def test_car_list_bad(self):
        self.page_404(reverse('main:car_list', kwargs={'page': 99999}))

    def test_car_list_paginate(self):
        response = self.get_page(reverse('main:car_list', kwargs={'page': 1}))
        self.assertEqual(len(response.context['car_list']), 10)
        response = self.get_page(reverse('main:car_list', kwargs={'page': 2}))
        self.assertEqual(len(response.context['car_list']), 3)

    def test_car_detail_good(self):
        self.get_page(reverse('main:car_detail', kwargs={'car_id': 1}))

    def test_car_detail_bad(self):
        self.page_404(reverse('main:car_detail', kwargs={'car_id': 99999}))

    def test_rent_car_loggedin_good(self):
        self.login()
        self.get_page(reverse('main:rent_create', kwargs={'car_id': 1}))

    def test_rent_car_loggedin_bad(self):
        self.login()
        self.page_404(reverse('main:rent_create', kwargs={'car_id': 99999}))

    def test_rent_car_loggedout(self):
        self.logout()
        self.page_redirect(reverse('main:rent_create', kwargs={'car_id': 1}))
        self.page_redirect(reverse('main:rent_create', kwargs={'car_id': 99999}))

    def test_my_history_list_good(self):
        self.get_page(reverse('main:my_history_list_default'))
        self.get_page(reverse('main:my_history_list', kwargs={'page': 1}))

    def test_my_history_list_bad(self):
        self.page_404(reverse('main:my_history_list', kwargs={'page': 99999}))

    def test_filter_car_name(self):
        url = "%s?car_name=Audi" % reverse('main:index')
        self.get_page(url)

    def test_filter_car_type_good(self):
        url = "%s?car_type=2" % reverse('main:index')
        self.get_page(url)

    def test_filter_engine_type(self):
        url = "%s?engine_type=3" % reverse('main:index')
        self.get_page(url)

    def test_filter_price_from(self):
        url = "%s?price_from=80" % reverse('main:index')
        self.get_page(url)

    def test_filter_price_to(self):
        url = "%s?price_to=220" % reverse('main:index')
        self.get_page(url)

    def test_filter_start_date(self):
        i = datetime.datetime.now()
        url = "%s?start_date=%s-%s-%s" % (reverse('main:index'), i.year, i.month, i.day)
        self.get_page(url)

    def test_filter_end_date(self):
        i = datetime.datetime.now()
        url = "%s?end_date=%s-%s-%s" % (reverse('main:index'), i.year, i.month, i.day+7)
        self.get_page(url)

