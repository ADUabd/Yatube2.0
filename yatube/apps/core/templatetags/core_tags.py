from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляет CSS класс к полю формы."""
    return field.as_widget(attrs={'class': css})


@register.simple_tag
def url_replace(request, field, value):
    """Заменяет параметр в URL."""
    params = request.GET.copy()
    params[field] = value
    return params.urlencode()


@register.filter
def pluralize_ru(value, args):
    """
    Русская плюрализация.
    Использование: {{ count|pluralize_ru:"пост,поста,постов" }}
    """
    try:
        args = args.split(',')
        if len(args) != 3:
            return ''
        
        value = abs(int(value))
        
        if value % 100 in (11, 12, 13, 14):
            return args[2]
        elif value % 10 == 1:
            return args[0]
        elif value % 10 in (2, 3, 4):
            return args[1]
        else:
            return args[2]
    except (ValueError, TypeError):
        return ''
