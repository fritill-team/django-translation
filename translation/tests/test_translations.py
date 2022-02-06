from django import forms
from django.conf import settings

from django.forms.widgets import TextInput, Textarea
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.utils.translation import activate, get_language
from django.utils.translation import gettext as _
from translation.forms import TranslationForm, TranslatableModelForm
from translation.serializers import TranslatableModelSerializer
from translation.tests.models import TranslatableTestModel as TestModel, TranslatableTestModel
from rest_framework.test import APIClient
from rest_framework import status


class TranslatableModelGetFieldTranslationTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_raises_exception_if_field_is_not_in_translatable_property(self):
        with self.assertRaises(KeyError) as context:
            self.model = TestModel.objects.create(title={"en": "Welcome :)", "ar": "اهلا"})
            self.model.get_field_translation('created_at', settings.LANGUAGE_ARABIC)
            self.assertEquals(context.exception, _('"created_at" is not translatable field'))

    def test_it_raises_exception_if_field_value_is_string(self):
        with self.assertRaises(ValueError) as context:
            self.model = TestModel.objects.create(title="Welcome :)")
            self.model.get_field_translation('title', settings.LANGUAGE_ARABIC)
            self.assertEquals(context.exception, _('"title" value is string, expected to be json'))

    def test_it_returns_the_required_locale(self):
        self.model = TestModel.objects.create(title={"en": "Welcome :)", "ar": "اهلا"})
        translated_title = self.model.get_field_translation('title', settings.LANGUAGE_ARABIC)
        self.assertEquals(translated_title, "اهلا")

    def test_it_returns_the_value_of_fallback_locale_if_requested_locale_does_not_exists(self):
        self.model = TestModel.objects.create(title={"en": "Welcome :)"})
        translated_title = self.model.get_field_translation('title', settings.LANGUAGE_ARABIC)
        self.assertEquals(translated_title, "Welcome :)")

    def test_it_returns_the_value_of_any_available_locale_if_requested_locale_and_fallback_locale_does_not_exists(self):
        self.model = TestModel.objects.create(title={"es": "Welcome :)"})
        translated_title = self.model.get_field_translation('title', settings.LANGUAGE_ARABIC)
        self.assertEquals(translated_title, "Welcome :)")

    def test_it_returns_empty_string_if_field_value_has_no_values(self):
        self.model = TestModel.objects.create(title={})
        translated_title = self.model.get_field_translation('title', settings.LANGUAGE_ARABIC)
        self.assertEquals(translated_title, "")

    def test_it_returns_empty_string_if_field_value_has_None_value(self):
        self.model = TestModel.objects.create()
        translated_title = self.model.get_field_translation('title', settings.LANGUAGE_ARABIC)
        self.assertEquals(translated_title, "")


class TranslatableModelGetTranslatedObjectTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_returns_all_translatable_fields_translated_into_required_locale(self):
        model = TestModel.objects.create(
            title={"en": "Welcome :)", "ar": "اهلا"},
            description={"en": "Welcome :)", "ar": "اهلا"},
        )
        model.get_translated_object(settings.LANGUAGE_ARABIC)
        self.assertEquals(model.title, "اهلا")
        self.assertEquals(model.title, "اهلا")

    def test_it_returns_all_translatable_fields_translated_into_current_locale_if_locale_is_not_provided(self):
        model = TestModel.objects.create(
            title={"en": "Welcome :)", "ar": "اهلا"},
            description={"en": "Welcome :)", "ar": "اهلا"},
        )
        model.get_translated_object()
        self.assertEquals(model.title, "Welcome :)")
        self.assertEquals(model.title, "Welcome :)")


class TranslatableModelSetTranslationTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_hard_sets_field_translation_for_target_field(self):
        model = TestModel.objects.create(title={"en": "Welcome :)"})
        model.set_translation('title', settings.LANGUAGE_ARABIC, "اهلا")

        # hard check
        model.refresh_from_db()
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ARABIC), "اهلا")
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ENGLISH), "Welcome :)")

    def test_it_soft_sets_field_translation_for_target_field(self):
        model = TestModel.objects.create(title={"en": "Welcome :)"})
        model.set_translation('title', settings.LANGUAGE_ARABIC, "اهلا", soft=True)

        # soft check
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ARABIC), "اهلا")
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ENGLISH), "Welcome :)")

        # hard check
        model.refresh_from_db()
        self.assertTrue(settings.LANGUAGE_ARABIC not in model.title)
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ENGLISH), "Welcome :)")

    def test_it_sets_the_field_value_to_the_language_code_if_field_value_is_string(self):
        model = TestModel.objects.create(title="Welcome :)")
        model.set_translation('title', settings.LANGUAGE_ARABIC, "اهلا")
        # hard check
        model.refresh_from_db()
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ENGLISH), "Welcome :)")
        self.assertEquals(model.get_field_translation('title', settings.LANGUAGE_ARABIC), "اهلا")

    def test_it_throws_exception_if_field_is_not_translatable(self):
        with self.assertRaises(KeyError) as context:
            model = TestModel.objects.create(title="Welcome :)")
            model.set_translation('created_at', settings.LANGUAGE_ARABIC, "اهلا")
            self.assertEquals(context.exception, _('"created_at" is not translatable field'))

    def test_it_throws_exception_if_locale_is_not_in_settings_LANGUAGES_KEYS(self):
        with self.assertRaises(KeyError) as context:
            model = TestModel.objects.create(title="Welcome :)")
            model.set_translation('title', 'ccc', "اهلا")
            self.assertEquals(context.exception, _('"ccc" is not translatable field'))


class TranslatableModelTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_contains_translated_property_for_each_translatable_field(self):
        model = TestModel.objects.create(title={"en": "Welcome :)"})
        self.assertTrue(
            all([hasattr(model, 'translated_{}'.format(field)) for field, __ in model.translatable.items()]))

    def test_it_passes_the_field_value_as_it_is_if_the_value_is_string(self):
        model = TestModel.objects.create(title="Welcome :)")
        self.assertEquals(model.translated_title, "Welcome :)")

    def test_it_returns_translated_fields_with_current_locale_if_exists_in_field(self):
        activate(settings.LANGUAGE_ARABIC)
        model = TestModel.objects.create(title={"en": "Welcome :)", "ar": "اهلا"},
                                         description={"en": "Welcome :)", "ar": "اهلا"})
        self.assertEquals(model.translated_title, "اهلا")

    def test_it_returns_translated_field_with_the_value_of_fallback_locale_if_requested_locale_does_not_exists(self):
        activate(settings.LANGUAGE_ARABIC)
        model = TestModel.objects.create(title={"en": "Welcome :)"}, description={"en": "Welcome :)"})
        self.assertEquals(model.translated_title, "Welcome :)")

    def test_it_returns_translated_field_with_the_value_of_any_available_locale_if_requested_locale_and_fallback_locale_does_not_exists(
            self):
        model = TestModel.objects.create(title={"es": "Welcome :)"}, description={"es": "Welcome :)"})
        self.assertEquals(model.translated_title, "Welcome :)")

    def test_it_returns_empty_string_if_field_value_has_no_values(self):
        model = TestModel.objects.create()
        self.assertEquals(model.translated_title, "")

    def test_each_translated_field_has_the_correct_value(self):
        model = TestModel.objects.create(
            title={"en": "Welcome :)", "ar": "اهلا"},
            description={"en": "Welcome :)", "ar": "اهلا"},
        )
        self.assertTrue(
            all([model.get_field_translation(field, get_language()) == getattr(model, "translated_{}".format(field))
                 for field, __ in model.translatable.items()]))

    def test_each_translated_field_has_the_correct_value_in_different_language(self):
        activate(settings.LANGUAGE_ARABIC)
        model = TestModel.objects.create(
            title={"en": "Welcome :)", "ar": "اهلا"},
            description={"en": "Welcome :)", "ar": "اهلا"},
        )
        self.assertTrue(
            all([model.get_field_translation(field, get_language()) == getattr(model, "translated_{}".format(field))
                 for field, __ in model.translatable.items()]))


class TranslationFormTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

        self.instance = TestModel.objects.create(
            title={"en": "Welcome :)", "ar": "اهلا"},
            description={"en": "Welcome :)", "ar": "اهلا"},
        )

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_updates_the_same_instance_of_the_model(self):
        """
        the form must update the same instance and must not create any new records
        """
        form = TranslationForm(
            model_class=TestModel,
            instance=self.instance,
            locale="ar",
            data={"title": "اهلا", "description": "اهلا"}
        )
        instance = form.save()
        self.assertEquals(instance.pk, self.instance.pk)

    def test_throws_exception_if_model_class_is_not_provided(self):
        """
        model_class must be provided to form
        """
        with self.assertRaises(KeyError) as context:
            TranslationForm(locale="ar", instance=self.instance)
        self.assertTrue("Form missing 1 required key word argument: 'model_class'" in str(context.exception))

    def test_throws_exception_if_instance_is_not_provided(self):
        """
        instance must be provided to form
        """
        with self.assertRaises(KeyError) as context:
            TranslationForm(locale="ar", model_class=TestModel)
        self.assertTrue("Form missing 1 required key word argument: 'instance'" in str(context.exception))

    def test_throws_exception_if_locale_is_not_provided(self):
        """
        locale must be provided to form
        """
        with self.assertRaises(KeyError) as context:
            TranslationForm(model_class=TestModel, instance=self.instance)
        self.assertTrue("Form missing 1 required key word argument: 'locale'" in str(context.exception))

    def test_it_returns_initial_values_with_available_locale_values(self):
        form = TranslationForm(model_class=TestModel, instance=self.instance, locale="ar")
        self.assertEquals(form.initial['title'], "اهلا")
        self.assertEquals(form.initial['description'], "اهلا")

    def test_it_returns_fields_and_widgets_based_on_model_translatable_attributes(self):
        form = TranslationForm(model_class=TestModel, instance=self.instance, locale="ar")
        self.assertIsInstance(form.fields['title'], forms.CharField)
        self.assertIsInstance(form.fields['title'].widget, TextInput)
        self.assertIsInstance(form.fields['description'], forms.CharField)
        self.assertIsInstance(form.fields['description'].widget, Textarea)

    def test_it_updates_fields_without_overriding_other_locales(self):
        self.instance = TestModel.objects.create(title={"en": "Welcome :)"}, description={"en": "Welcome :)"})
        form = TranslationForm(
            model_class=TestModel,
            instance=self.instance,
            locale="ar",
            data={"title": "اهلا", "description": "اهلا"}
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.instance.refresh_from_db()

        self.assertEquals(self.instance.title['en'], "Welcome :)")
        self.assertEquals(self.instance.title['ar'], "اهلا")
        self.assertEquals(self.instance.description['en'], "Welcome :)")
        self.assertEquals(self.instance.description['ar'], "اهلا")

    def test_it_throws_exception_if_input_is_invalid_locales(self):
        """
        throws exception if the locale is not a valid locale
        """
        with self.assertRaises(ValueError) as context:
            TranslationForm(
                model_class=TestModel,
                instance=self.instance,
                locale="not-a-language",
                data={"title": "اهلا", "description": "اهلا"}
            )
            self.assertTrue("input locale must be included in application languages" in str(context.exception))


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
        self.url = reverse("translate:admin-view",
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
        self.assertTemplateUsed(self.response, "translate.html")

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
            self.response = self.client.get(reverse("translate:admin-view", args=["admin", "testmodel", 1, 'ar']))
            self.assertTrue("key next must be included in request" in str(context.exception))

    def test_it_uses_the_next_locale_if_locale_is_not_provided_in_url(self):
        url = reverse("translate:admin-view",
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
        self.assertRedirects(self.response, '/')
        self.assertEquals(self.response.status_code, 302)

    def test_it_redirects_to_same_url_if_save_in_POST_request(self):
        self.response = self.client.post(self.url, {
            "title": "اهلا وسهلا",
            "description": "اهلا وسهلا",
            "next": "/test/",
            "locale": settings.LANGUAGE_ARABIC,
            "save": ""})
        self.assertRedirects(self.response, self.url)
        self.assertEquals(self.response.status_code, 302)

    def test_it_renders_the_same_requests_with_errors_if_data_is_invalid_in_POST_request(self):
        self.response = self.client.post(self.url, {
            "title": "اهلا وسهلا",
            "next": "/test/",
            "locale": settings.LANGUAGE_ARABIC,
            "save": ""})
        self.assertTemplateUsed(self.response, "translate.html")
        self.assertEquals(self.response.status_code, 422)


class TestModelForm(TranslatableModelForm):
    class Meta:
        model = TestModel
        fields = "__all__"


class TranslatableModelFormTestCase(TestCase):
    def setUp(self):
        self.old_LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.old_FALLBACK_LOCALE = settings.FALLBACK_LOCALE
        self.old_MAIN_LANGUAGE = settings.MAIN_LANGUAGE

        settings.FALLBACK_LOCALE = settings.LANGUAGE_ENGLISH
        settings.LANGUAGE_CODE = settings.LANGUAGE_ENGLISH
        settings.MAIN_LANGUAGE = settings.LANGUAGE_ENGLISH
        activate(settings.LANGUAGE_ENGLISH)

    def tearDown(self):
        settings.FALLBACK_LOCALE = self.old_LANGUAGE_CODE
        settings.LANGUAGE_CODE = self.old_FALLBACK_LOCALE
        settings.MAIN_LANGUAGE = self.old_MAIN_LANGUAGE
        activate(settings.LANGUAGE_CODE)

    def test_it_returns_fields_and_widgets_based_on_model_translatable_attributes(self):
        form = TestModelForm(data={"title": "Welcome :)", "description": "Welcome :)"})
        self.assertIsInstance(form.fields['title'], forms.CharField)
        self.assertIsInstance(form.fields['title'].widget, TextInput)
        self.assertIsInstance(form.fields['description'], forms.CharField)
        self.assertIsInstance(form.fields['description'].widget, Textarea)

    def test_it_returns_field_initial_value_in_original_locale_only(self):
        instance = TestModel.objects.create(
            title={"en": "Welcome from title:)", "ar": "اهلا فى العنوان"},
            description={"en": "Welcome from description:)", "ar": "اهلا فى الوصف"})
        form = TestModelForm(instance=instance)
        self.assertEquals(form.instance.title, "Welcome from title:)")

    def test_it_saves_translatable_value_with_settings_language_code_in_creation_of_new_record(self):
        """
        in creation of new record the original field value is None
        """
        form = TestModelForm(data={"title": "Welcome from title:)", "description": "Welcome from description:)"})
        self.assertTrue(form.is_valid())
        form.save()

        instance = TestModel.objects.get(pk=1)
        self.assertEquals(instance.title['en'], "Welcome from title:)")
        self.assertEquals(instance.description['en'], "Welcome from description:)")

    def test_it_updates_translatable_values_of_settings_default_locale(self):
        """
        in instance update it saves the new values
        """
        TestModel.objects.create(title={"en": "Welcome from title:)"}, description={"en": "Welcome from description:)"})

        form = TestModelForm(data={"title": "Welcome!!", "description": "Welcome Dude!!"},
                             instance=TestModel.objects.get(pk=1))
        self.assertTrue(form.is_valid())
        form.save()
        instance = TestModel.objects.get(pk=1)

        self.assertEquals(instance.title['en'], "Welcome!!")
        self.assertEquals(instance.description['en'], "Welcome Dude!!")

    def test_it_maintains_other_locales_on_instance_update(self):
        """
        in instance update it saves the new values  without changing other locales values
        """
        instance = TestModel.objects.create(
            title={"en": "Welcome from title:)", "ar": "اهلا فى العنوان"},
            description={"en": "Welcome from description:)", "ar": "اهلا فى الوصف"})

        form = TestModelForm(data={"title": "Welcome!!", "description": "Welcome Dude!!"}, instance=instance)

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEquals(instance.title['ar'], "اهلا فى العنوان")
        self.assertEquals(instance.description['ar'], "اهلا فى الوصف")
        self.assertEquals(instance.title['en'], "Welcome!!")
        self.assertEquals(instance.description['en'], "Welcome Dude!!")


class TestSerializer(TranslatableModelSerializer):
    class Meta:
        model = TranslatableTestModel
        fields = '__all__'


class TranslatableModelSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {'title': 'title', 'description': 'description'}
        self.serializer = TestSerializer(data=self.data)
        self.serializer.is_valid()
        self.serializer.save()
        self.test_obj = TranslatableTestModel.objects.get(pk=1)

    def test_it_turns_all_translatable_fields_into_json(self):
        self.assertEquals(self.test_obj.translated_title, 'title')

    def test_it_keeps_un_translatable_fields_as_it_is(self):
        self.assertNotIsInstance(self.test_obj.created_at, dict)

    def test_it_set_field_to_current(self):
        ((locale, value),) = self.test_obj.title.items()
        self.assertEquals(locale, get_language())

    def test_it_set_fields_as_it_is_when_insert_json(self):
        data = {'title': {'en': 'title', 'ar': 'عنوان'}, 'description': 'description'}
        serializer = TestSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        self.assertEquals(serializer.instance.title, data['title'])

    def test_it_return_validation_error_when_insert_unsupported_locale(self):
        data = {'title': {'en': 'title', 'su': 'asdca'}, 'description': 'description'}
        serializer = TestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEquals(set(serializer.errors.keys()), {'title'})

    def test_it_return_field_by_current_locale(self):
        self.assertEquals(self.serializer.data['title'], 'title')

    def test_it_returns_fall_back_locale_when_there_is_no_value_for_current_locale(self):
        activate(next(locale for locale in settings.LANGUAGES_KEYS if locale != settings.LANGUAGE_CODE))
        self.assertEquals(self.serializer.data['title'], 'title')

    def test_it_return_current_locale_when_activate_other_locale(self):
        data = {'title': {'en': 'title', 'ar': 'عنوان'}, 'description': 'description'}
        serializer = TestSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        activate(next(locale for locale in settings.LANGUAGES_KEYS if locale != get_language()))
        self.assertEquals(serializer.data['title'], data['title'][get_language()])
        activate(next(locale for locale in settings.LANGUAGES_KEYS if locale != get_language()))

    def test_it_return_field_by_current_locale_when_insert_json(self):
        data = {'title': {'en': 'title', 'ar': 'عنوان'}, 'description': 'description'}
        serializer = TestSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        self.assertEquals(serializer.data['title'], data['title'][settings.LANGUAGE_CODE])
        self.assertEquals(serializer.data['description'], data['description'][settings.LANGUAGE_CODE])

    def test_it_updates_instance(self):
        data = {'title': {'en': 'title', 'ar': 'عنوان'}, 'description': 'description'}
        serializer = TestSerializer(data=data, instance=self.test_obj)
        serializer.is_valid()
        serializer.save()
        self.test_obj.refresh_from_db()
        self.assertEquals(self.test_obj.title, data['title'])

    def test_it_updates_specified_locale_value(self):
        data = {'title': 'title', 'description': 'description'}
        serializer = TestSerializer(data=data, instance=self.test_obj, context={'locale': 'en'})
        serializer.is_valid()
        serializer.save()
        self.assertEquals(self.test_obj.title['en'], data['title']['en'])

    def test_it_append_supported_locale_value_if_does_not_exist(self):
        other_locale = next(locale for locale in settings.LANGUAGES_KEYS if locale != settings.LANGUAGE_CODE)
        data = {'title': {other_locale: 'other locale title'}, 'description': 'description'}
        serializer = TestSerializer(data=data, instance=self.test_obj)
        serializer.is_valid()
        serializer.save()
        title = {**data['title'], settings.LANGUAGE_CODE: self.data['title'][settings.LANGUAGE_CODE]}
        self.assertEquals(self.test_obj.title, title)

    def test_it_update_locale_values_when_it_exists(self):
        data = {'title': {settings.LANGUAGE_CODE: 'other title'}, 'description': 'description'}
        serializer = TestSerializer(data=data, instance=self.test_obj)
        serializer.is_valid()
        serializer.save()
        self.assertEquals(data['title'][settings.LANGUAGE_CODE], self.test_obj.title[settings.LANGUAGE_CODE])


class TranslationAPIViewTestCase(TestCase):
    def setUp(self):
        self.test_model = TestModel.objects.create(title={settings.LANGUAGE_CODE: "title"},
                                                   description={"en": "description"})
        self.client = APIClient()
        self.url = reverse('translate:api-view', kwargs={"app_label": 'tests',
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
