from django.db import transaction

from airport.models import Ticket, Order

def create_order(user, flight, seats: list[tuple[int, int]]):
    with transaction.atomic():
        order = Order.objects.create(user=user)
        tickets = []
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
