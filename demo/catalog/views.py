from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST

from .decorators import admin_panel_required, catalog_login_required
from .models import BookingStatus, PaymentMethod, Room
from .services import AdminBookingService, AuthService, BookingService, ReviewService


class HomeView(View):
    def get(self, request):
        return render(request, "catalog/home.html")


class RegisterView(View):
    def get(self, request):
        if request.session.get(settings.SESSION_USER_KEY):
            return redirect(reverse("catalog:cabinet"))
        return render(request, "catalog/register.html", {"errors": {}, "form_data": {}})

    def post(self, request):
        data = {
            "login": request.POST.get("login", ""),
            "password": request.POST.get("password", ""),
            "full_name": request.POST.get("full_name", ""),
            "phone": request.POST.get("phone", ""),
            "email": request.POST.get("email", ""),
        }
        user, errors = AuthService().register(data)
        if user:
            request.session[settings.SESSION_USER_KEY] = user.pk
            messages.success(request, "Регистрация прошла успешно.")
            return redirect(reverse("catalog:cabinet"))
        return render(
            request,
            "catalog/register.html",
            {"errors": errors, "form_data": data},
        )


class LoginView(View):
    def get(self, request):
        if request.session.get(settings.SESSION_USER_KEY):
            return redirect(reverse("catalog:cabinet"))
        return render(request, "catalog/login.html")

    def post(self, request):
        login = request.POST.get("login", "")
        password = request.POST.get("password", "")
        user = AuthService().authenticate(login, password)
        if user:
            request.session[settings.SESSION_USER_KEY] = user.pk
            messages.success(request, "Вы вошли в систему.")
            return redirect(reverse("catalog:cabinet"))
        messages.error(
            request,
            "Неверный логин или пароль. Проверьте данные или пройдите регистрацию.",
        )
        return render(request, "catalog/login.html", {"login_value": login})


class LogoutView(View):
    def get(self, request):
        request.session.pop(settings.SESSION_USER_KEY, None)
        return redirect(reverse("catalog:home"))


@catalog_login_required
def cabinet_view(request):
    bookings = BookingService().user_bookings(request.catalog_user)
    return render(
        request,
        "catalog/cabinet.html",
        {"bookings": bookings, "user": request.catalog_user},
    )


@catalog_login_required
def booking_create_view(request):
    rooms = Room.objects.filter(is_active=True)
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        try:
            room_id = int(room_id)
        except (TypeError, ValueError):
            room_id = None
        booking, error = BookingService().create_booking(
            request.catalog_user,
            room_id,
            request.POST.get("event_date", ""),
            request.POST.get("event_time", "10:00"),
            request.POST.get("payment_method", PaymentMethod.CASH),
        )
        if booking:
            messages.success(
                request,
                f"Заявка №{booking.pk} создана. Статус: «Новое».",
            )
            return redirect(reverse("catalog:cabinet"))
        messages.error(request, error or "Ошибка при создании заявки.")
    return render(
        request,
        "catalog/booking.html",
        {"rooms": rooms, "payment_choices": PaymentMethod.choices},
    )


@catalog_login_required
@require_POST
def review_create_view(request, booking_id):
    review, error = ReviewService().add_review(
        request.catalog_user,
        booking_id,
        request.POST.get("text", ""),
        int(request.POST.get("rating", 5)),
    )
    if review:
        messages.success(request, "Отзыв добавлен.")
    else:
        messages.error(request, error)
    return redirect(reverse("catalog:cabinet"))


class AdminLoginView(View):
    def get(self, request):
        if request.session.get(settings.SESSION_ADMIN_KEY):
            return redirect(reverse("catalog:admin_panel"))
        return render(request, "catalog/admin_login.html")

    def post(self, request):
        login = request.POST.get("login", "")
        password = request.POST.get("password", "")
        if (
            login == settings.ADMIN_PANEL_LOGIN
            and password == settings.ADMIN_PANEL_PASSWORD
        ):
            request.session[settings.SESSION_ADMIN_KEY] = True
            return redirect(reverse("catalog:admin_panel"))
        messages.error(request, "Неверный логин или пароль админа.")
        return render(request, "catalog/admin_login.html")


class AdminLogoutView(View):
    def get(self, request):
        request.session.pop(settings.SESSION_ADMIN_KEY, None)
        return redirect(reverse("catalog:admin_login"))


@admin_panel_required
def admin_panel_view(request):
    service = AdminBookingService()
    status = request.GET.get("status", "")
    room_id = request.GET.get("room", "")
    search = request.GET.get("q", "")
    sort = request.GET.get("sort", "-created")
    page = request.GET.get("page", "1")

    qs = service.get_queryset(
        status=status or None,
        room_id=room_id or None,
        search=search or None,
        sort=sort,
    )
    page_obj = service.paginate(qs, int(page) if str(page).isdigit() else 1)

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        new_status = request.POST.get("status")
        ok, msg = service.update_status(int(booking_id), new_status)
        if ok:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        return redirect(request.get_full_path())

    return render(
        request,
        "catalog/admin_panel.html",
        {
            "page_obj": page_obj,
            "rooms": Room.objects.all(),
            "status_choices": BookingStatus.choices,
            "filters": {"status": status, "room": room_id, "q": search, "sort": sort},
        },
    )

