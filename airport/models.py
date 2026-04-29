from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.auth import get_user_model


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.closest_big_city} - {self.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return (f"{self.airplane_type} - {self.name}: "
                f"{self.rows} {self.seats_in_row}")


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )
    distance = models.PositiveIntegerField()

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination must be different")

    def __str__(self):
        return f"{self.source} -> {self.destination} - {self.distance}"


class Flight(models.Model):
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival must be after departure")

    def get_taken_seats(self):
        return self.tickets.values_list("row", "seat")

    def seats_left(self):
        return self.airplane.capacity - self.tickets.count()

    def get_available_seats(self):
        taken = set(self.get_taken_seats())
        seats = []
        for row in range(1, self.airplane.rows + 1):
            for seat in range(1, self.airplane.seats_in_row + 1):
                if (row, seat) not in taken:
                    seats.append((row, seat))
        return seats

    def __str__(self):
        return (f"{self.route} {self.airplane}\n"
                f"{self.departure_time} - {self.arrival_time}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders"
    )



    def __str__(self):
        return f"{self.user} {self.created_at}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = ("flight", "row", "seat")

    def clean(self):
        airplane = self.flight.airplane
        if self.row > airplane.rows:
            raise ValidationError("Row does not exist")
        if self.seat > airplane.seats_in_row:
            raise ValidationError("Seat does not exist")
        if Ticket.objects.filter(
            row=self.row,
            seat=self.seat,
            flight=self.flight,
        ).exists():
            raise ValidationError("Seat already taken")

    @staticmethod
    def create_order(user, flight, seats):
        with transaction.atomic():
            tickets = []
            order = Order.objects.create(user=user)

            for row, seat in seats:
                ticket = Ticket(
                    flight=flight,
                    order=order,
                    row=row,
                    seat=seat
                )
                ticket.full_clean()
                tickets.append(ticket)

            Ticket.objects.bulk_create(tickets)
            return order

    def __str__(self):
        return (f"{self.flight} {self.order}\n"
                f"row: {self.row} seat: {self.seat}")
