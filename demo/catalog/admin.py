from django.contrib import admin

from .models import BookingRequest, CatalogUser, Review, Room


@admin.register(CatalogUser)
class CatalogUserAdmin(admin.ModelAdmin):
    list_display = ("login", "full_name", "email", "phone", "created_at")
    search_fields = ("login", "full_name", "email")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_type", "capacity", "is_active")
    list_filter = ("room_type", "is_active")


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "event_start", "status", "payment_method")
    list_filter = ("status", "payment_method")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "user", "rating", "created_at")
