from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name="get_field_original_translation")
def get_field_original_translation(_o, field):
    return _o.get_field_translation(field, settings.MAIN_LANGUAGE)


register.filter('get_field_original_translation', get_field_original_translation)
