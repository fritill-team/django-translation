from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.apps import apps

from translation.translation import TranslationForm
from django.conf import settings


class AdminTranslateView(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get('next') is None:
            raise KeyError(str(_("key next must be included in request")))

        locale = kwargs.get('locale', next(x for x in settings.LANGUAGES_KEYS if x != settings.MAIN_LANGUAGE))
        model = apps.get_model(kwargs['app_label'], kwargs['model'])
        instance = get_object_or_404(model, pk=kwargs['pk'])

        languages = dict(settings.LANGUAGES)
        languages.pop(settings.LANGUAGE_CODE)

        return render(request, "translate.html", context={
            "languages": languages,
            "next": request.GET.get('next'),
            "locale": locale,
            "app_label": kwargs.get("app_label"),
            "model": kwargs.get("model"),
            "object": instance,
            "form": TranslationForm(model_class=model, instance=instance, locale=locale)
        })

    def post(self, request, *args, **kwargs):
        if request.POST.get('next') is None:
            raise KeyError(str(_("key next must be included in request")))

        model = apps.get_model(kwargs['app_label'], kwargs['model'])
        instance = get_object_or_404(model, pk=kwargs['pk'])
        locale = kwargs.get("locale", request.POST.get('locale'))
        next_link = request.POST.get('next')

        form = TranslationForm(model_class=model, instance=instance, locale=locale, data=request.POST)

        if form.is_valid():
            form.save()
            if "save" in request.POST:
                return redirect(reverse('admin:utils:translate', kwargs={**kwargs}) + "?next={}".format(next_link))
            else:
                return redirect(to=next_link)

        languages = dict(settings.LANGUAGES)
        languages.pop(settings.LANGUAGE_CODE)

        for field, __ in instance.translatable.items():
            if isinstance(getattr(form.instance, field), str):
                instance.set_translation(field, locale, getattr(form.instance, field), soft=True)

        return render(request, "translate.html", context={
            "languages": languages,
            "next": request.GET.get('next'),
            "locale": kwargs.get("locale"),
            "app_label": kwargs.get("app_label"),
            "model": kwargs.get("model"),
            "object": instance,
            "form": form
        }, content_type=None, status=422)
