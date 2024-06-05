from django import template


register = template.Library()

@register.filter()
def currency(value):
    int_value = int(value)
    curr_value = format(int_value, ',').replace(',', '.')
    return f'{curr_value} ₽'