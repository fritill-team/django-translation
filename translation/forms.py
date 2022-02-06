from django import forms
from django.conf import settings
from django.forms.widgets import TextInput
from django.utils.translation import gettext as _





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

