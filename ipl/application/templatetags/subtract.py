from django import template

register = template.Library()

@register.filter
def do_subtract(value, arg):
    return value - arg