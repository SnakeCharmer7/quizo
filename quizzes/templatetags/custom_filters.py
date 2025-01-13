from django import template

register = template.Library()

@register.filter
def css_class_for_percentage(value):
    try:
        percentage = float(value)
        if percentage >= 80:
            return "success"
        elif 50 <= percentage < 80:
            return "warning"
        else:
            return "danger"
    except ValueError:
        return "danger"
