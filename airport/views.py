from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from airport.models import (
    Airport,
    Route,
    Flight,
    Order,
    Crew,
    Airplane,
    AirplaneType,
    Ticket
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    CrewSerializer,
    CrewListSerializer,
    AirportSerializer,
    AirportListSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    FlightSerializer,
    FlightRetrieveSerializer,
    FlightListSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    TicketSerializer,
    TicketCreateSerializer, TicketListSerializer, TicketRetrieveSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        return AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()

    def get_queryset(self):
        qs = Ticket.objects.all()
        if self.action == "list":
            return qs.select_related(
                "flight__route__source",
                "flight__route__destination",
            )
        if self.action == "retrieve":
            return qs.select_related(
                "flight__route__source",
                "flight__route__destination",
                "flight__airplane",
            ).prefetch_related("flight__crew")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

    def get_queryset(self):
        return (
            Flight.objects
            .select_related(
                "route",
                "route__source",
                "route__destination",
                "airplane",
                "airplane__airplane_type",
            )
            .prefetch_related(
                "crew",
                "tickets",
            )
            .annotate(
                seats_taken=Count("tickets")
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer
