from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _, get_language


class TranslatableModel(models.Model):
    class Meta:
        abstract = True

    translatable = {}

    def get_field_translation(self, field, locale):
        if field not in self.translatable:
            raise KeyError(_('"{}" is not translatable field'.format(field)))

        field_value = getattr(self, field)

        if isinstance(field_value, str):
            raise ValueError(_('"{}" value is string, expected to be json'.format(field)))

        if not field_value:
            return ''

        if locale in field_value:
            return field_value[locale]
        elif settings.FALLBACK_LOCALE in field_value:
            return field_value[settings.FALLBACK_LOCALE]
        elif bool(field_value):
            available_locale = list(field_value.keys())[0]
            return field_value[available_locale]
        else:
            return ""

    def get_translated_object(self, locale=None):
        if not locale:
            locale = get_language()

        for field in self.translatable:
            field_value = self.get_field_translation(field, locale)
            setattr(self, field, field_value)

    def set_translation(self, field, locale, value, soft=False):
        if field not in self.translatable:
            raise KeyError(_('"{}" is not translatable_field'.format(field)))

        if locale not in settings.LANGUAGES_KEYS:
            raise KeyError(_('"{}" is not translatable_field'.format(locale)))

        field_value = getattr(self, field)
        if isinstance(field_value, str):
            field_value = {settings.LANGUAGE_CODE: field_value}

        field_value.update({locale: value})
        setattr(self, field, field_value)
        if not soft:
            self.save()

    def __init__(self, *args, **kwargs):
        super(TranslatableModel, self).__init__(*args, **kwargs)

        for field, __ in self.translatable.items():
            field_value = getattr(self, field)

            current_locale = get_language()
            if field_value:
                if isinstance(field_value, str):
                    translated_value = field_value
                elif current_locale in field_value:
                    translated_value = field_value[current_locale]
                elif settings.FALLBACK_LOCALE in field_value:
                    translated_value = field_value[settings.FALLBACK_LOCALE]
                elif bool(field_value):
                    available_locale = list(field_value.keys())[0]
                    translated_value = field_value[available_locale]
                else:
                    translated_value = ""
            else:
                translated_value = ""

            setattr(self, 'translated_{}'.format(field), translated_value)
