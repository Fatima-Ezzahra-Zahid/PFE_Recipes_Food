from django import template

register = template.Library()


@register.filter(name='get')
def get(dictionary, key):
    """
    Get the value of a dictionary for the given key in Django templates.
    """
    return dictionary.get(key)
