"""
Requirements:
    1. The parking lot should have multiple levels, each level with certain number of parking spots.
    2. The parking lot should support different types of vehicles, such as cars, motorcycles, trucks
    3. Each parking spot should be able to accommodate a specific type of vehicle.
    4. The system should assign a vehicle a parking spot upon entry and release it upon exit.
    5.The system should track the availability of spots and provide real time information to the users.
    6. The system should handle multiple entry and exit points and support concurrent access.

Entities:
    1. Parking Lot
    2. Parking Spot
    3. Ticket.
    4. Parking Floor
    5. Vehicle

Class Diagrams
    Parking Lot
        - parking_floors : list[ParkingFloor]
        - tickets : List[Ticket]
        - parking_strategy : ParkingStrategy

        + ParkingLot()
        + get_parking_spot(vehicle_id : str, vehicle : Vehicle) -> ParkingSpot
        + free_parking_spot(ticket)

    ParkingFloor
        - number : int
        - parking_spots : list[ParkingSpot]
        - parking_spots : list[ParkingSpot]

        + ParkingFloor()
        + free_parking_spot(parking_spot)
        + occupy_parking_sport(parking_spot)

    Size(Enum)
        - Small
        - Medium
        - Large

    Status(Enum):
        - Free
        - Occupied

    ParkingSpot
        - id : int
        - size : Size
        - status : Status

        + ParkingSpot()
        + free_parking_spot()
        + occupy_parking_spot(Vehicle)

    Vehicle
    - id : int
    - size : Size

"""
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from os import name
from typing import Optional, override


class Size(Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


class Status(Enum):
    FREE = "FREE"
    OCCUPIED = "OCCUPIED"


class Vehicle:
    def __init__(self, id : int, size : Size):
        self.id = id
        self.size = size

    def get_size(self) -> Size:
        return self.size

    def get_id(self) -> int:
        return self.id


class ParkingSpot:
    def __init__(self, id : int, size : Size):
        self.id = id
        self.size = size
        self.Status = Status.FREE
        self.parked_vehicle : Optional[Vehicle | None] = None

    def free_parking_spot(self):
        self.set_parked_vehicle(None)

    def occupy_parking_spot(self, vehicle : Vehicle):
        self.set_parked_vehicle(vehicle)

    def get_parked_vehicle(self):
        return self.parked_vehicle

    def set_parked_vehicle(self, parked_vehicle : Vehicle | None):
        self.parked_vehicle = parked_vehicle

    def get_size(self) -> Size:
        return self.size

    def get_status(self) -> Status:
        return self.Status


class ParkingFloor:
    def __init__(self, number : int):
        self.number = number
        self.parking_spots : dict[int, ParkingSpot]= defaultdict(None)

    def free_parking_spot(self, spot_id : int ):
        self.parking_spots[spot_id].free_parking_spot()

    def occupy_parking_spot(self, spot_id : int, vehicle : Vehicle):
        self.parking_spots[spot_id].occupy_parking_spot(vehicle)

    def get_parking_spots(self) -> list[ParkingSpot]:
        return list(self.parking_spots.values())

    def add_parking_spot(self, parking_spot : ParkingSpot):
        self.parking_spots[parking_spot.id] = parking_spot


class Ticket:
    def __init__(self, id : int, vehicle : Vehicle):
        self.id = id
        self.vehicle = vehicle


class ParkingStrategy(ABC):
    @abstractmethod
    def find_parking_spot(self, vehicle : Vehicle, parking_floors : list[ParkingFloor]) -> ParkingSpot | None:
        pass


class FirstFoundOut(ParkingStrategy):
    @override
    def find_parking_spot(self, vehicle : Vehicle, parking_floors : list[ParkingFloor]) -> ParkingSpot | None:
        for parking_floor in parking_floors:
            for parking_spot in parking_floor.get_parking_spots():
                if parking_spot.get_size() == vehicle.get_size() and parking_spot.get_status()==Status.FREE:
                    return parking_spot

        return None


class ParkingLot:
    def __init__(self, parking_floors : list[ParkingFloor], parking_strategy : ParkingStrategy):
        self.parking_floors : list[ParkingFloor] = parking_floors
        self.parking_strategy : ParkingStrategy = parking_strategy
        self.tickets : dict[Ticket, ParkingSpot] = defaultdict(None)

    def find_parking_spot(self, vehicle : Vehicle) -> ParkingSpot | None:
        spot = self.parking_strategy.find_parking_spot(vehicle, self.get_parking_floors())
        return spot

    def park_vehicle(self, vehicle : Vehicle):
        spot = self.find_parking_spot(vehicle)
        if spot is not None:
            spot.occupy_parking_spot(vehicle)

    def unpark_vehicle(self, ticket : Ticket):
        parking_spot = self.tickets[ticket]

        if parking_spot is not None:
            parking_spot.free_parking_spot()
            del self.tickets[ticket]


    def get_parking_floors(self) -> list[ParkingFloor]:
        return self.parking_floors


if __name__=="__main__":
    pf1 = ParkingFloor(0)
    pf2 = ParkingFloor(1)
    pf3 = ParkingFloor(2)

    for i in range(0,5):
        parking_spot = ParkingSpot(i, Size.SMALL)
        pf1.add_parking_spot(parking_spot)

    for i in range(0,5):
        parking_spot = ParkingSpot(i, Size.MEDIUM)
        pf2.add_parking_spot(parking_spot)

    for i in range(0,5):
        parking_spot = ParkingSpot(i, Size.LARGE)
        pf3.add_parking_spot(parking_spot)

    parking_strategy = FirstFoundOut()

    parking_lot = ParkingLot([pf1, pf2, pf3], parking_strategy)

    v1 = Vehicle(1, Size.SMALL)
    v2 = Vehicle(2, Size.MEDIUM)
    v3 = Vehicle(3, Size.LARGE)

    parking_lot.park_vehicle(v1)
    parking_lot.park_vehicle(v2)
    parking_lot.park_vehicle(v3)








