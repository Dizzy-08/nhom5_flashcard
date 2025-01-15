from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    return float(value) * float(arg)


@register.filter
def divided_by(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def subtract(value, arg):
    return value - arg
