from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate
from translation.forms import TranslationForm
from translation.tests.models import TranslatableTestModel as TestModel


class AdminTranslationViewTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

        self.client = Client()
        self.model = TestModel.objects.create(
            title={"en": "Welcome :)", "ar": "اهلا"},
            description={"en": "Welcome :)", "ar": "اهلا"},
        )
        self.url = reverse("translation:translate_form",
                           args=["tests", "TranslatableTestModel", self.model.pk]) + "?next=/test/"

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_uses_translate_template_in_GET_request(self):
        """
        method: GET
        template: translate.html
        """
        self.response = self.client.get(self.url)
        self.assertTemplateUsed(self.response, "translation/translate.html")

    def test_context_has_list_of_languages_in_GET_request(self):
        """
        method: GET
        context must have list of languages
        """
        self.response = self.client.get(self.url)
        self.assertIn("languages", self.response.context)

    def test_languages_is_all_locales_except_the_app_locale_in_GET_request(self):
        """
        method: GET
        it returns the languages key with the value of all locales except the locale stored in
        settings.LANGUAGE_CODE
        """
        self.response = self.client.get(self.url)
        languages = dict(settings.LANGUAGES)
        languages.pop(settings.LANGUAGE_CODE)
        self.assertEquals(languages, self.response.context['languages'])

    def test_context_has_next_in_GET_request(self):
        """
          method: GET
          context must have next link
        """
        self.response = self.client.get(self.url)
        self.assertIn("next", self.response.context)

    def test_it_throws_exception_if_next_is_not_in_url_in_GET_request(self):
        """
        method: GET
        context must have next link
        """
        with self.assertRaises(KeyError) as context:
            self.response = self.client.get(
                reverse("translation:translate_form_locale", args=["admin", "testmodel", 1, 'ar']))
            self.assertTrue("key next must be included in request" in str(context.exception))

    def test_it_uses_the_next_locale_if_locale_is_not_provided_in_url(self):
        url = reverse("translation:translate_form",
                      args=["tests", "TranslatableTestModel", self.model.pk]) + "?next=/test/"
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_context_has_target_locale_in_GET_request(self):
        """
        method: GET
        context must have list of languages
        """
        self.response = self.client.get(self.url)
        self.assertIn("locale", self.response.context)

    def test_context_has_app_label_in_GET_request(self):
        """
        method: GET
        context must have app_label
        """
        self.response = self.client.get(self.url)
        self.assertIn("app_label", self.response.context)

    def test_context_has_model_in_GET_request(self):
        """
        method: GET
        context must have model
        """
        self.response = self.client.get(self.url)
        self.assertIn("model", self.response.context)

    def test_context_has_object_in_GET_request(self):
        """
        method: GET
        context must have object
        """
        self.response = self.client.get(self.url)
        self.assertIn("object", self.response.context)

    def test_object_must_be_an_instance_of_model_in_GET_request(self):
        """
        method: GET
        context must have object
        """
        self.response = self.client.get(self.url)
        self.assertEquals(self.response.context['object'], self.model)

    def test_context_has_form_in_GET_request(self):
        """
        method: GET
        context must have form
        """
        self.response = self.client.get(self.url)
        self.assertIn("form", self.response.context)

    def test_form_is_an_instance_of_AdminTranslationForm_in_GET_request(self):
        """
        method: GET
        context must have form
        """
        self.response = self.client.get(self.url)
        self.assertIsInstance(self.response.context["form"], TranslationForm)

    def test_it_throws_exception_if_locale_is_not_in_request_in_POST_request(self):
        """
        method: GET
        context must have next link
        """
        with self.assertRaises(KeyError) as context:
            self.client.post(self.url, {"title": "اهلا وسهلا", "description": "اهلا وسهلا", "save": ""})

    def test_it_throws_exception_if_next_is_not_in_url_in_POST_request(self):
        """
        method: POST
        context must have next link
        """
        with self.assertRaises(KeyError) as context:
            self.client.post(self.url, {
                "title": "اهلا وسهلا",
                "description": "اهلا وسهلا",
                "save": ""})
            self.assertTrue("key next must be included in request" in str(context.exception))

    def test_it_updates_model_value_on_submit_in_POST_request(self):
        self.client.post(self.url, {
            "title": "اهلا وسهلا",
            "description": "اهلا وسهلا",
            "locale": settings.LANGUAGE_ARABIC,
            "next": "/test/",
            "save": ""
        })
        self.model.refresh_from_db()
        self.assertEquals("اهلا وسهلا", self.model.title['ar'])

    def test_it_redirects_to_next_url_if_save_is_not_in_request_in_POST_request(self):
        self.response = self.client.post(self.url, {
            "title": "اهلا وسهلا",
            "description": "اهلا وسهلا",
            "locale": settings.LANGUAGE_ARABIC,
            "next": "/",
        })
        self.assertRedirects(self.response, '/', fetch_redirect_response=False)
        self.assertEquals(self.response.status_code, 302)

    def test_it_redirects_to_same_url_if_save_in_POST_request(self):
        self.response = self.client.post(self.url, {
            "title": "اهلا وسهلا",
            "description": "اهلا وسهلا",
            "next": "/test/",
            "locale": settings.LANGUAGE_ARABIC,
            "save": ""})
        self.assertRedirects(self.response, self.url, fetch_redirect_response=False)
        self.assertEquals(self.response.status_code, 302)

    def test_it_renders_the_same_requests_with_errors_if_data_is_invalid_in_POST_request(self):
        self.response = self.client.post(self.url, {
            "title": "اهلا وسهلا",
            "next": "/test/",
            "locale": settings.LANGUAGE_ARABIC,
            "save": ""})
        self.assertTemplateUsed(self.response, "translation/translate.html")
        self.assertEquals(self.response.status_code, 422)
