from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from .models import CatalogUser


def catalog_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get(settings.SESSION_USER_KEY)
        if not user_id:
            return redirect(reverse("catalog:login"))
        try:
            request.catalog_user = CatalogUser.objects.get(pk=user_id)
        except CatalogUser.DoesNotExist:
            request.session.flush()
            return redirect(reverse("catalog:login"))
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_panel_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get(settings.SESSION_ADMIN_KEY):
            return redirect(reverse("catalog:admin_login"))
        return view_func(request, *args, **kwargs)

    return wrapper
