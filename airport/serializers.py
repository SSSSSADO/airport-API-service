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


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")

class AirplaneSerializer(serializers.ModelSerializer):
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


class TicketCreateSerializer(serializers.Serializer):
    row = serializers.IntegerField()
    seat = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderCreateSerializer(serializers.Serializer):
    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all()
    )
    tickets = TicketCreateSerializer(many=True)

    def create(self, validated_data):
        tickets_data = validated_data["tickets"]
        flight = validated_data["flight"]
        user = self.context["request"].user

        return Ticket.create_order(
            user=user,
            flight=flight,
            seats=[(t["row"], t["seat"]) for t in tickets_data]
        )



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
        return obj.seats_left()
