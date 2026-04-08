import datetime


def year(request):
    """Добавляет текущий год в контекст шаблонов."""
    return {'year': datetime.datetime.now().year}
