from django import template
import builtins

register = template.Library()

@register.filter(name='abs')
def absolute_value(value):
    try:
        return builtins.abs(int(value))
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value
