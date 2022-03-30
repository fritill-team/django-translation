from django.test import TestCase
from django.urls import reverse, resolve
from translation.views import TranslationAPIView, AdminTranslateView


class TranslationAdminUrlsTestCase(TestCase):
    def test_admin_translate_view_resolve(self):
        url = reverse('translation:translate_form', args=['app_label', 'model', 'pk'])
        self.assertEquals(resolve(url).func.view_class, AdminTranslateView)

    def test_admin_translate_view_resolve_with_local(self):
        url = reverse('translation:translate_form_locale', args=['app_label', 'model', 'pk', 'ar'])
        self.assertEquals(resolve(url).func.view_class, AdminTranslateView)


class TranslationAPIUrlsTestCase(TestCase):
    def test_admin_translate_view_with_locale_resolve(self):
        url = reverse('translation:translate_locale', args=['app_label', 'model', 'pk', 'ar'])
        self.assertEquals(resolve(url).func.view_class, TranslationAPIView)

    def test_admin_translate_view_resolve(self):
        url = reverse('translation:translate', args=['app_label', 'model', 'pk'])
        self.assertEquals(resolve(url).func.view_class, TranslationAPIView)
