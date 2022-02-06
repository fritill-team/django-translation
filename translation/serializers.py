from django.conf import settings
from django.utils.translation import gettext as _, get_language
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class TranslatableModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        for field_name in self.Meta.model.translatable:
            if field_name in data:
                if isinstance(data[field_name], dict):
                    for locale, value in data[field_name].items():
                        if locale not in settings.LANGUAGES_KEYS:
                            raise ValidationError({field_name: _("'{}' is not in supported locales".format(locale))})
                else:
                    if 'locale' in self.context and self.context.get('locale', None):
                        data[field_name] = {self.context['locale']: data[field_name]}
                    else:
                        data[field_name] = {get_language(): data[field_name]}
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field, __ in instance.translatable.items():
            if field in representation:
                if isinstance(representation[field], dict):
                    if get_language() in representation[field]:
                        representation[field] = representation[field][get_language()]
                    else:
                        if settings.FALLBACK_LOCALE in representation[field]:
                            representation[field] = representation[field][settings.FALLBACK_LOCALE]
                        else:
                            representation[field] = ''
        return representation

    def update(self, instance, validated_data):
        for field_name, __ in self.Meta.model.translatable.items():
            if field_name in validated_data:
                for locale, value in validated_data[field_name].items():
                    instance.set_translation(field_name, locale, value, soft=True)
                validated_data.pop(field_name)
        return super(TranslatableModelSerializer, self).update(instance, validated_data)

    class Meta:
        model = None
        fields = '__all__'
