import re
from datetime import datetime

from django.core.exceptions import ValidationError

LOGIN_PATTERN = re.compile(r"^[a-zA-Z0-9]{6,}$")
PASSWORD_PATTERN = re.compile(r"^[a-zA-Z0-9]{8,}$")
PHONE_PATTERN = re.compile(r"^\+?[0-9\-\s()]{10,18}$")
DATE_DD_MM_YYYY = re.compile(r"^(\d{2})-(\d{2})-(\d{4})$")


class RegistrationValidator:
    @staticmethod
    def validate_login(login: str) -> str | None:
        if not login or not login.strip():
            return "Логин обязателен."
        if not LOGIN_PATTERN.match(login):
            return "Логин: латиница и цифры, минимум 6 символов."
        return None

    @staticmethod
    def validate_password(password: str) -> str | None:
        if not password:
            return "Пароль обязателен."
        if not PASSWORD_PATTERN.match(password):
            return "Пароль: латиница и цифры, минимум 8 символов."
        return None

    @staticmethod
    def validate_full_name(full_name: str) -> str | None:
        if not full_name or len(full_name.strip()) < 5:
            return "Укажите ФИО."
        return None

    @staticmethod
    def validate_phone(phone: str) -> str | None:
        if not phone:
            return "Укажите телефон."
        if not PHONE_PATTERN.match(phone.strip()):
            return "Неверный формат телефона."
        return None

    @staticmethod
    def validate_email(email: str) -> str | None:
        if not email:
            return "Укажите email."
        if "@" not in email or "." not in email.split("@")[-1]:
            return "Неверный email."
        return None


class BookingDateValidator:
    # дата как в задании: 18-05-2026
    @staticmethod
    def parse(date_str: str) -> datetime:
        match = DATE_DD_MM_YYYY.match(date_str.strip())
        if not match:
            raise ValidationError("Дата в формате ДД-ММ-ГГГГ.")
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError as exc:
            raise ValidationError("Некорректная дата.") from exc
