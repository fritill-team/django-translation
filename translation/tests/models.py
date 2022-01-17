from core.helper.base_manger import GetOrNoneManger
from django import forms
from django.db import models
from django.forms.widgets import Textarea
from django.utils.timezone import now
from translation.translation import TranslatableModel


# TranslatableModel
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


class TestManager(GetOrNoneManger):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class MyTest(models.Model):
    objects = TestManager()
    title = models.CharField(max_length=20, blank=True, null=True)
    new_test = models.ForeignKey("MyNewTest", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title


class TestManagerTwo(GetOrNoneManger):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class MyNewTest(models.Model):
    objects = TestManagerTwo()

    description = models.CharField(max_length=20, blank=True, null=True)
