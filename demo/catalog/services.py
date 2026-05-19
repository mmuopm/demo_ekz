from datetime import datetime
from typing import Any

from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.utils import timezone

from .models import BookingRequest, BookingStatus, CatalogUser, Review, Room
from .validators import BookingDateValidator, RegistrationValidator


class AuthService:
    def __init__(self):
        self._validator = RegistrationValidator()

    def validate_registration(self, data: dict[str, str]) -> dict[str, str]:
        errors: dict[str, str] = {}
        checks = [
            ("login", self._validator.validate_login(data.get("login", ""))),
            ("password", self._validator.validate_password(data.get("password", ""))),
            ("full_name", self._validator.validate_full_name(data.get("full_name", ""))),
            ("phone", self._validator.validate_phone(data.get("phone", ""))),
            ("email", self._validator.validate_email(data.get("email", ""))),
        ]
        for field, message in checks:
            if message:
                errors[field] = message
        if not errors.get("login") and CatalogUser.objects.filter(login=data.get("login")).exists():
            errors["login"] = "Такой логин уже есть."
        return errors

    def register(self, data: dict[str, str]) -> tuple[CatalogUser | None, dict[str, str]]:
        errors = self.validate_registration(data)
        if errors:
            return None, errors
        password = data["password"]
        if self._password_exists(password):
            errors["password"] = "Этот пароль уже занят."
            return None, errors
        user = CatalogUser.objects.create(
            login=data["login"].strip(),
            password_hash=make_password(password),
            full_name=data["full_name"].strip(),
            phone=data["phone"].strip(),
            email=data["email"].strip().lower(),
        )
        return user, {}

    def _password_exists(self, raw_password: str) -> bool:
        for user in CatalogUser.objects.only("password_hash"):
            if check_password(raw_password, user.password_hash):
                return True
        return False

    def authenticate(self, login: str, password: str) -> CatalogUser | None:
        try:
            user = CatalogUser.objects.get(login=login.strip())
        except CatalogUser.DoesNotExist:
            return None
        if check_password(password, user.password_hash):
            return user
        return None


class BookingService:
    def create_booking(
        self,
        user: CatalogUser,
        room_id: int | None,
        date_str: str,
        time_str: str,
        payment_method: str,
    ) -> tuple[BookingRequest | None, str | None]:
        if not room_id:
            return None, "Выберите помещение."
        try:
            room = Room.objects.get(pk=room_id, is_active=True)
        except Room.DoesNotExist:
            return None, "Помещение не найдено."

        try:
            base_date = BookingDateValidator.parse(date_str)
        except Exception as exc:
            return None, str(exc)

        try:
            hour, minute = map(int, time_str.split(":"))
        except (ValueError, AttributeError):
            return None, "Время в формате ЧЧ:ММ."

        event_start = timezone.make_aware(
            datetime(base_date.year, base_date.month, base_date.day, hour, minute)
        )
        if event_start < timezone.now():
            return None, "Нельзя выбрать прошедшую дату."

        booking = BookingRequest.objects.create(
            user=user,
            room=room,
            event_start=event_start,
            payment_method=payment_method,
            status=BookingStatus.NEW,
        )
        return booking, None

    def user_bookings(self, user: CatalogUser) -> QuerySet[BookingRequest]:
        return (
            BookingRequest.objects.filter(user=user)
            .select_related("room", "review")
            .order_by("-created_at")
        )


class ReviewService:
    def add_review(
        self, user: CatalogUser, booking_id: int, text: str, rating: int
    ) -> tuple[Review | None, str | None]:
        try:
            booking = BookingRequest.objects.select_related("review").get(pk=booking_id, user=user)
        except BookingRequest.DoesNotExist:
            return None, "Заявка не найдена."
        if not booking.can_leave_review:
            return None, "Сначала админ должен обработать заявку."
        if hasattr(booking, "review"):
            return None, "Отзыв уже есть."
        if not text.strip():
            return None, "Напишите текст отзыва."
        rating = max(1, min(5, rating))
        review = Review.objects.create(
            booking=booking, user=user, text=text.strip(), rating=rating
        )
        return review, None


class AdminBookingService:
    SORT_FIELDS = {
        "date": "event_start",
        "-date": "-event_start",
        "created": "created_at",
        "-created": "-created_at",
        "status": "status",
        "-status": "-status",
    }

    def get_queryset(
        self,
        status: str | None = None,
        room_id: str | None = None,
        search: str | None = None,
        sort: str = "-created",
    ) -> QuerySet[BookingRequest]:
        qs = BookingRequest.objects.select_related("user", "room").all()
        if status:
            qs = qs.filter(status=status)
        if room_id:
            qs = qs.filter(room_id=room_id)
        if search:
            qs = qs.filter(
                Q(user__login__icontains=search)
                | Q(user__full_name__icontains=search)
                | Q(room__name__icontains=search)
            )
        order = self.SORT_FIELDS.get(sort, "-created_at")
        return qs.order_by(order)

    def paginate(self, queryset: QuerySet, page: int, per_page: int = 8) -> Any:
        return Paginator(queryset, per_page).get_page(page)

    def update_status(self, booking_id: int, new_status: str) -> tuple[bool, str]:
        if new_status not in BookingStatus.values:
            return False, "Неверный статус."
        updated = BookingRequest.objects.filter(pk=booking_id).update(status=new_status)
        if not updated:
            return False, "Заявка не найдена."
        return True, "Статус сохранён."
