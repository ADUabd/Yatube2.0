from django.shortcuts import render


def page_not_found(request, exception):
    """Страница 404."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    """Страница 500."""
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    """Страница 403."""
    return render(request, 'core/403.html', status=403)
