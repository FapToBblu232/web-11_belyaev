from django import template


register = template.Library()

@register.filter
def truncate_str(string_to_truncate, limit=10):
    if isinstance(string_to_truncate, str) and len(string_to_truncate) > limit + 3:
        return string_to_truncate[:limit] + '...'
    return string_to_truncate