# Custom Exception Classes
class FlightNotFoundError(Exception):
    """Raised when the flight number does not exist in records."""
    pass

class SeatsUnavailableError(Exception):
    """Raised when requested seats are more than available seats."""
    pass

# Flight Management System
def flight_management():
    try:
        # Open file safely
        f = open("flights.txt", "r")

        # Load flights into dictionary
        flights = {}
        for line in f:
            flight_number, seats, price = line.strip().split()
            flights[flight_number] = {"seats": int(seats), "price": float(price)}

        try:
            # ---- Booking operations ----
            flight_no = input("Enter flight number: ").strip()
            if flight_no not in flights:
                raise FlightNotFoundError("Flight not found!")

            # Get user tickets
            tickets = int(input("Enter number of tickets: "))

            if tickets > flights[flight_no]["seats"]:
                raise SeatsUnavailableError("Not enough seats available!")

            # Calculate total cost
            total_cost = flights[flight_no]["price"] * tickets

            # Discount per ticket = total / tickets
            discount_per_ticket = total_cost / tickets   # May raise ZeroDivisionError
            # discount_total_tickets = discount_per_ticket * tickets

            payable_amount = total_cost - discount_per_ticket

            # Print booking details
            print("\nBooking Successful ✅")
            print(f"Flight Number : {flight_no}")
            print(f"Available Seats: {flights[flight_no]['seats']}")
            print(f"Price per Ticket: {flights[flight_no]['price']}")
            print(f"Tickets Booked : {tickets}")
            print(f"Total Cost     : {total_cost}")
            print(f"Discount/Ticket: {discount_per_ticket:.2f}")
            # print(f"Total Discount : {discount_total_tickets:.2f}")
            print(f"Amount Payable : {payable_amount:.2f}")

        except FlightNotFoundError as e:
            print("Error:", e)
        except SeatsUnavailableError as e:
            print("Error:", e)
        except ValueError:
            print("Error: Invalid input! Please enter numbers only.")
        except ZeroDivisionError:
            print("Error: Number of tickets cannot be zero.")

    except FileNotFoundError:
        print("Error: flights.txt file not found!")
    finally:
        # Ensure file is closed
        try:
            f.close()
        except:
            pass

if __name__ == "__main__":
    flight_management()