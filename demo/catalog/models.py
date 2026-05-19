from django.db import models
from django.utils import timezone


class RoomType(models.TextChoices):
    AUDITORIUM = "auditorium", "Аудитория"
    COWORKING = "coworking", "Коворкинг"
    CINEMA = "cinema", "Кинозал"


class BookingStatus(models.TextChoices):
    NEW = "new", "Новое"
    ASSIGNED = "assigned", "Мероприятие назначено"
    COMPLETED = "completed", "Мероприятие завершено"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Наличные"
    TRANSFER = "transfer", "Перевод"


# свой пользователь, не стандартный User django
class CatalogUser(models.Model):
    login = models.CharField(max_length=64, unique=True, verbose_name="Логин")
    password_hash = models.CharField(max_length=128, verbose_name="Хэш пароля")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(max_length=254, verbose_name="Email")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.login


class Room(models.Model):
    name = models.CharField(max_length=120, verbose_name="Название")
    room_type = models.CharField(
        max_length=20, choices=RoomType.choices, verbose_name="Тип помещения"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    capacity = models.PositiveIntegerField(default=50, verbose_name="Вместимость")
    image = models.ImageField(upload_to="rooms/", blank=True, null=True, verbose_name="Фото")
    is_active = models.BooleanField(default=True, verbose_name="Доступно")

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ["room_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"


class BookingRequest(models.Model):
    user = models.ForeignKey(
        CatalogUser, on_delete=models.CASCADE, related_name="bookings", verbose_name="Пользователь"
    )
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name="bookings", verbose_name="Помещение"
    )
    event_start = models.DateTimeField(verbose_name="Начало конференции")
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, verbose_name="Способ оплаты"
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.NEW,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Создана")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка #{self.pk} — {self.user.login}"

    @property
    def can_leave_review(self):
        # отзыв только если админ уже менял статус
        return self.status != BookingStatus.NEW


class Review(models.Model):
    booking = models.OneToOneField(
        BookingRequest, on_delete=models.CASCADE, related_name="review", verbose_name="Заявка"
    )
    user = models.ForeignKey(
        CatalogUser, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автор"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="Оценка")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв к заявке #{self.booking_id}"
