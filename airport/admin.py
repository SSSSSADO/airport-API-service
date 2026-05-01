from django.contrib import admin

from airport.models import (
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Order,
    Ticket
)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "airplane_type",
        "rows",
        "seats_in_row",
        "capacity"
    )
    list_filter = ("airplane_type",)
    search_fields = ("name",)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "airplane",
        "departure_time",
        "arrival_time",
        "get_crew"
    )
    list_filter = ("airplane",)
    search_fields = ("route__source__name", "route__destination__name")

    def get_crew(self, obj):
        return ", ".join([str(c) for c in obj.crew.all()])


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("flight", "row", "seat", "order")
    list_filter = ("flight",)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    inlines = [TicketInline]
