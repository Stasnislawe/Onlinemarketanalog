from django import template


register = template.Library()

@register.filter()
def currency(value):
    curr_value = format(value, ',').replace(',', '.')
    return f'{curr_value} ₽'