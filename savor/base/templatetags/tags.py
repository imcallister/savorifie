from django.template import Library
import pytz

EASTERN = pytz.timezone('US/Eastern')
UTC = pytz.timezone('UTC')

register = Library()

@register.filter(name='_getattr')
def _getattr(value, arg):
    return getattr(value, arg)

@register.filter(name='_getdict')
def _getdict(dictionary, arg):
    return dictionary.get(arg, '')

@register.filter(name='as_EST')
def as_EST(value):
    return UTC.localize(value).astimezone(EASTERN)

@register.filter(name='_getitem')
def _getitem(value, arg):
    return value[arg]
