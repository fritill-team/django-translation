from django import forms
from django.conf import settings
from django.forms.widgets import TextInput, Textarea
from django.test import TestCase
from django.utils.translation import activate, get_language
from translation.forms import TranslationForm, TranslatableModelForm
from translation.tests.models import TranslatableTestModel as TestModel


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
