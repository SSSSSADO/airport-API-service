from django.db import transaction

from rest_framework import serializers

from airport.models import (
    AirplaneType,
    Airport,
    Route,
    Crew,
    Airplane,
    Flight,
    Ticket,
    Order
)


class AirPlainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")

class AirPlainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class FlightSerializer(serializers.ModelSerializer):
    seats_left = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "crew",
            "route",
            "airplane",
            "seats_left"
        )

    def get_seats_left(self, obj):
        return obj.seats_left


class OrderSerializer(serializers.ModelSerializer):
    tickets = serializers.SerializerMethodField(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")

    def create(self, validated_data):
        user = self.context["request"].user
        tickets_data = validated_data.pop("tickets")

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            tickets = []
            for ticket_data in tickets_data:
                ticket = Ticket(
                    order=order,
                    **ticket_data
                )
                ticket.full_clean()
                tickets.append(ticket)
            Ticket.objects.bulk_create(tickets)

        return order
