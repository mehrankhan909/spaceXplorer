from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, 'N/A')
    return 'N/A'


@register.filter
def default_if_none(value, default=''):
    if value is None:
        return default
    return value
