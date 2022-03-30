from django import forms
from django.db import models
from django.forms.widgets import Textarea
from django.utils.timezone import now
from translation.models import TranslatableModel


# Translatable Model
class TranslatableTestModel(TranslatableModel):
    translatable = {
        "title": {"field": forms.CharField},
        "description": {"field": forms.CharField, "widget": Textarea},
    }

    id = models.BigAutoField(primary_key=True)
    title = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_created=True, default=now, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
