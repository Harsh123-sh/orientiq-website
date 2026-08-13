from django import template

register = template.Library()


@register.filter
def getattr(obj, attr):
    """Return the attribute value of an object by name."""
    return getattr(obj, attr, "")