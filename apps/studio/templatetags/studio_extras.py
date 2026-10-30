from django import template

register = template.Library()


@register.filter
def field_value(obj, name):
    """Display value of a model field, using get_FOO_display for choices."""
    display = getattr(obj, f"get_{name}_display", None)
    value = display() if callable(display) else getattr(obj, name, "")
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return value if value not in (None, "") else "—"
