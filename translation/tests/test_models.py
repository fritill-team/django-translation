from django.conf import settings
from django.test import TestCase
from django.utils.translation import activate, get_language
from django.utils.translation import gettext as _
from translation.tests.models import TranslatableTestModel as TestModel


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
