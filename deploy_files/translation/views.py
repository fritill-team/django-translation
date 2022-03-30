from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from translation.forms import TranslationForm
from translation.serializers import TranslatableModelSerializer


class AdminTranslateView(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get('next') is None:
            raise KeyError(str(_("key next must be included in request")))

        locale = kwargs.get('locale', next(x for x in settings.LANGUAGES_KEYS if x != settings.MAIN_LANGUAGE))
        model = apps.get_model(kwargs['app_label'], kwargs['model'])
        instance = get_object_or_404(model, pk=kwargs['pk'])

        languages = dict(settings.LANGUAGES)
        languages.pop(settings.LANGUAGE_CODE)

        return render(request, "translation/translate.html", context={
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
            if "save" in request.POST:  # save and go to the next language
                return redirect(reverse('translation:translate_form', kwargs={**kwargs}) + "?next={}".format(next_link))
            else:
                return redirect(to=next_link)

        languages = dict(settings.LANGUAGES)
        languages.pop(settings.LANGUAGE_CODE)

        for field, __ in instance.translatable.items():
            if isinstance(getattr(form.instance, field), str):
                instance.set_translation(field, locale, getattr(form.instance, field), soft=True)

        return render(request, "translation/translate.html", context={
            "languages": languages,
            "next": request.GET.get('next'),
            "locale": kwargs.get("locale"),
            "app_label": kwargs.get("app_label"),
            "model": kwargs.get("model"),
            "object": instance,
            "form": form
        }, content_type=None, status=422)


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
