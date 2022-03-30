from django.conf import settings
from django.test import TestCase
from django.utils.translation import activate, get_language
from translation.serializers import TranslatableModelSerializer
from translation.tests.models import TranslatableTestModel


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
