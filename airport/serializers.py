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


# Airplane Type
class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


# Airplane
class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "rows", "seats_in_row", "airplane_type", "capacity"
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "capacity")


class AirplaneRetrieveSerializer(AirplaneListSerializer):
    class Meta(AirplaneListSerializer.Meta):
        model = Airplane
        fields = (
            "id", "name", "rows", "seats_in_row", "airplane_type", "capacity"
        )


# Airport
class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name")


# Route
class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


# Crew
class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = Crew
        fields = ("id", "full_name")


# Flight
class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "crew",
            "route",
            "airplane",
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteListSerializer()
    seats_left = serializers.IntegerField()

    class Meta:
        model = Flight
        fields = ("id", "route", "seats_left")


class FlightRetrieveSerializer(FlightListSerializer):
    crew = serializers.StringRelatedField(many=True)
    airplane = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta(FlightListSerializer.Meta):
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "crew",
            "route",
            "airplane",
            "seats_left"
        )


# Ticket
class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketListSerializer(serializers.ModelSerializer):
    route = serializers.CharField(source="flight.route", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "route")


class TicketRetrieveSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(read_only=True)

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


# Order
class OrderCreateSerializer(serializers.Serializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    tickets = TicketCreateSerializer(many=True)

    def create(self, validated_data):
        tickets_data = validated_data["tickets"]
        flight = validated_data["flight"]
        user = self.context["request"].user

        return Order.create_order(
            user=user,
            flight=flight,
            seats=[(t["row"], t["seat"]) for t in tickets_data]
        )
