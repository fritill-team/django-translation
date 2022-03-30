from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from translation.tests.models import TranslatableTestModel as TestModel


class TranslationAPIViewTestCase(TestCase):
    def setUp(self):
        self.test_model = TestModel.objects.create(title={settings.LANGUAGE_CODE: "title"},
                                                   description={"en": "description"})
        self.client = APIClient()
        self.url = reverse('translation:translate', kwargs={"app_label": 'tests',
                                                             'model': 'TranslatableTestModel',
                                                             'pk': '1'})

    def test_it_translate_current_locale_value_when_locale_is_none(self):
        data = {"title": {settings.LANGUAGE_CODE: "other title"}}
        self.client.post(self.url, data=data, format='json')
        self.test_model.refresh_from_db()
        self.assertEquals(self.test_model.title, data['title'])

    def test_it_returns_422_status_code_when_add_invalid_data(self):
        data = {"title": {'sd': "other title"}}
        response = self.client.post(self.url, data=data, format='json')
        self.assertEquals(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_it_translate_chosen_locale(self):
        locale = next(locale for locale in settings.LANGUAGES_KEYS if settings.LANGUAGE_CODE != locale)
        data = {"title": {locale: "{} title".format(locale)}, 'locale': locale}
        response = self.client.post(self.url, data=data, format='json')
        self.test_model.refresh_from_db()
        self.assertEquals(self.test_model.title[locale], data["title"][locale])

    def test_it_updates_existed_locales_values(self):
        data = {"title": {"en": "en title", "ar": "ar title"}}
        response = self.client.post(self.url, data=data, format='json')
        self.test_model.refresh_from_db()
        self.assertEquals(self.test_model.title, data['title'])
