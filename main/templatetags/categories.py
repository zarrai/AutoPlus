from django import template

from main.models import CarType

register = template.Library()

@register.simple_tag
def get_categories():
    return CarType.objects.all()
