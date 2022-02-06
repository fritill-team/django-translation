# Model Translation

## Installation
```python
pip install django-translation
```


## Configuration

### in settings.py file
```python
INSTALLED_APPS = [
  ....
'rest_framework',
'translation'
]

MAIN_LANGUAGE = 'ar' #you could add any language could you want
```

### in urls
```python
urlpatterns = [
    ....
    path('', include('translation.urls', namespace='translation'))
]
```


## usage

### In model:

* Use ```from translation.translation import TranslatableModel```  instead of ``` django.db.models.Model ```
* Use ``` django.db.models.JSONField ``` for every translatable field
* define "translatable" property which defines the translatable fields in the model
* translatable is a dictionary that references the translatable fields in any table
    * translatable key is field name
    * translatable value is a dictionary that can take two items **form field** and **form field widget**
    * the default widget is ```forms.TextInput```
* you can access the current locale of certain field by using ``` model.translated_field```
  for example if ```model``` has field ```name``` to get translated value to current locale
  use ``` model.translated_name ```

**Example**

```python
from django import forms
from django.db import models
from translation.models import  TranslatableModel


class Foo(TranslatableModel):
    ...
    # define translatable 
    translatable = {
        'name': {"field": forms.CharField},
        'bio': {"field": forms.CharField, "widget": forms.Textarea},
    }

    ...
    # define your fields here
    name = models.JSONField(blank=True, null=True)
    bio = models.JSONField(blank=True, null=True)

    ...

```

### In Forms:

Use ```from translation.translation import TranslatableModelForm```  instead of ``` django.forms.ModelForm ```

### TranslationURl

To use translation form for any model just redirect to this url

**please note** "next" query parameter is mandatory parameter

```python
from django.urls import reverse

next_url = '/any/url/you/want/to/redirect/to/after/translation'

reverse("{yourpath}:translate", kwargs={
    "app_label": "app_label",
    "model": "model",
    "pk": "pk"
}) + '?next={}'.format(next_url)
```

### In Serializer

Use ```utils.serializers.TranslatableModelSerializer``` instead of ``` rest_framework.serializers.ModelSerializer ```

```python
from translation.serializers import  TranslatableModelSerializer


class FooSerializer(TranslatableModelSerializer):
    class Meta:
        fields = '__all__'
        model = TranslatableTestModel


...

data = {
    "title": {
        "en": "en_title",
        "ar": "ar_title"
    },
    "description": {
        "en": "en_title",
        "ar": "ar_title"
    }
}

serializer = FooSerializer(data=data)
serializer.is_valid()
serializer.save()
```

<ins>```.to_representation(self, instance)```</ins>

* it returns value by current locale ``` serializer.data["title"] ```
  => ```"en_title"``` if current locale is ```en```

* when current does not exist it returns value by fallback locale

<ins>```.to_internal_value(self, data)```</ins>

* it accepts single value and set it by current locale
    * ``` data = {"title": "foo title"} ``` => ``` {"title": {"en": "foo title"}} ``` if ``` en ``` is current locale
* it accepts json value and set it as it is
    * ``` data = {"title": {"en": "en foo title", "ar": "ar foo title"}} ```
      => ``` {"title": {"en": "en foo title", "ar": "ar foo title"}} ```
    * it raises validation error when add language code that doe not exists in supported languages

### In templates

<ins>```get_field_original_translation```</ins>

to get original field translation "main language" use filter for example

EX:

   ```  name|get_field_original_translation ```
