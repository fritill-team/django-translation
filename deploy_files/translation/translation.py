from django import forms
from django.apps import apps
from django.conf import settings
from django.db import models
from django.forms.widgets import TextInput
from django.utils.translation import gettext as _, get_language
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView


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


class TranslationForm(forms.ModelForm):
    fields = {}

    class Meta:
        model = None
        instance = None

    def __init__(self, *args, **kwargs):
        if "locale" not in kwargs:
            raise KeyError(_("Form missing 1 required key word argument: 'locale'"))

        if kwargs.get('locale') not in dict(settings.LANGUAGES).keys():
            raise ValueError(_("input locale must be included in application languages"))

        if "model_class" not in kwargs:
            raise KeyError(_("Form missing 1 required key word argument: 'model_class'"))

        if "instance" not in kwargs:
            raise KeyError(_("Form missing 1 required key word argument: 'instance'"))

        self._meta.instance = kwargs.get('instance')
        self._meta.model = kwargs.pop('model_class')
        self.locale = kwargs.pop('locale')

        initial = {}
        for field_name, __ in self._meta.model.translatable.items():
            field_value = self._meta.instance.get_field_translation(field_name, self.locale)
            initial.update({field_name: field_value})

        kwargs.update(initial=initial)

        super(TranslationForm, self).__init__(*args, **kwargs)

        for name, field in self._meta.model.translatable.items():
            widget = field['widget'] if 'widget' in field else TextInput
            self.fields.update({name: field['field'](widget=widget, required=True, label=_(name))})

    def save(self, commit=True):
        instance = super(TranslationForm, self).save(commit=False)
        instance.refresh_from_db()
        for field in self.cleaned_data:
            instance.set_translation(field, self.locale, self.cleaned_data[field], soft=True)
        if commit:
            instance.save()
        return instance


class TranslatableModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.original_translatable_values = {}

        if kwargs.get('instance', None):
            instance = kwargs.pop('instance')

            for name, field in instance.translatable.items():
                self.original_translatable_values.update({name: getattr(instance, name)})
                field_value = getattr(instance, name)
                field_initial_value = field_value[
                    settings.MAIN_LANGUAGE] if settings.MAIN_LANGUAGE in field_value else ''
                setattr(instance, name, field_initial_value)
            kwargs.update(instance=instance)

        super(TranslatableModelForm, self).__init__(*args, **kwargs)

        for name, field in self._meta.model.translatable.items():
            widget = field['widget'] if 'widget' in field else forms.TextInput
            self.fields.update({name: field['field'](widget=widget, required=True, label=_(name))})

    def save(self, commit=True):
        instance = super(TranslatableModelForm, self).save(commit=False)

        for field, __ in self._meta.model.translatable.items():
            if field in self.original_translatable_values:
                setattr(instance, field, self.original_translatable_values[field])
            else:
                setattr(instance, field, {})

            if field in self.cleaned_data:
                instance.set_translation(field, settings.LANGUAGE_CODE, self.cleaned_data[field], soft=True)

        if commit:
            instance.save()
        return instance


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


class TranslationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        model = apps.get_model(kwargs['app_label'], kwargs['model'])
        instance = get_object_or_404(model, pk=kwargs['pk'])
        locale = kwargs.get("locale", request.POST.get('locale'))

        TranslatableModelSerializer.Meta.model = model
        serializer = TranslatableModelSerializer(data=request.data, instance=instance, context={'locale': locale})

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
