"""
Create a base class Flight with basic flight information. Create a derived class ScheduledFlight that adds scheduling information.
 
Requirements:
-Flight should have attributes: flight number, airline.
-ScheduledFlight should add departure time and arrival time.
-Include methods to display complete flight information.
 
 
Create a base class Person, derived class CrewMember, and a further derived class Pilot.
-Person contains name and ID.
-CrewMember adds role (e.g., "Cabin Crew", "Pilot").
-Pilot adds license number and rank (e.g., "Captain").
 
 
Create a base class Service, and derive two classes: SecurityService and BaggageService.
Requirements:
-Service class has a method service_info().
-Derived classes override or extend this to describe their own service.
 
 
Create one class PassengerDetails and another class TicketDetails. Create a new class Booking that inherits from both.
Requirements:
- PassengerDetails has name, age.
- TicketDetails has ticket number, seat number.
- Booking shows all information.
"""
class Flight:
    def __init__(self, flight_number, airline):
        self.flight_number = flight_number
        self.airline = airline

    def display_info(self):
        print(f"Flight Number: {self.flight_number}")
        print(f"Airline: {self.airline}")


class ScheduledFlight(Flight):
    def __init__(self, flight_number, airline, departure_time, arrival_time):
        super().__init__(flight_number, airline)
        self.departure_time = departure_time
        self.arrival_time = arrival_time

    def display_info(self):
        super().display_info()
        print(f"Departure Time: {self.departure_time}")
        print(f"Arrival Time: {self.arrival_time}")

class Person:
    def __init__(self, name, person_id):
        self.name = name
        self.person_id = person_id

    def display_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.person_id}")


class CrewMember(Person):
    def __init__(self, name, person_id, role):
        super().__init__(name, person_id)
        self.role = role

    def display_info(self):
        super().display_info()
        print(f"Role: {self.role}")


class Pilot(CrewMember):
    def __init__(self, name, person_id, license_number, rank):
        super().__init__(name, person_id, role="Pilot")
        self.license_number = license_number
        self.rank = rank

    def display_info(self):
        super().display_info()
        print(f"License Number: {self.license_number}")
        print(f"Rank: {self.rank}")

class Service:
    def service_info(self):
        print("This is a general airport service.")


class SecurityService(Service):
    def service_info(self):
        print("Security Service")


class BaggageService(Service):
    def service_info(self):
        print("Baggage Service")

class PassengerDetails:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display_info(self):
        print(f"Passenger Name: {self.name}")
        print(f"Age: {self.age}")


class TicketDetails:
    def __init__(self, ticket_number, seat_number):
        self.ticket_number = ticket_number
        self.seat_number = seat_number

    def display_info(self):
        print(f"Ticket Number: {self.ticket_number}")
        print(f"Seat Number: {self.seat_number}")


class Booking(PassengerDetails, TicketDetails):
    def __init__(self, name, age, ticket_number, seat_number):
        PassengerDetails.__init__(self, name, age)
        TicketDetails.__init__(self, ticket_number, seat_number)

    def display_info(self):
        PassengerDetails.display_info(self)
        TicketDetails.display_info(self)

if __name__ == "__main__":
    print("Scheduled Flight")
    flight = ScheduledFlight("AI202", "Air India", "10:00 AM", "12:30 PM")
    flight.display_info()
    print("\nPilot Info")
    pilot = Pilot("Mike Brown", "P123", "LIC89063", "Captain")
    pilot.display_info()
    print("\nServices")
    security = SecurityService()
    security.service_info()
    baggage = BaggageService()
    baggage.service_info()
    print("\nBooking")
    booking = Booking("D.Smith", 28, "TCK16745", "17")
    booking.display_info()
