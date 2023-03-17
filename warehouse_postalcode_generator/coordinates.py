from dataclasses import dataclass
from googlemaps.client import Client as GMapsClient
import logging
from geopy.distance import great_circle
import math

logger = logging.getLogger("warehouse_postalcode_generator")


@dataclass(frozen=True)
class Address:
    address: str
    zip_code: str
    location: str
    city: str

    @property
    def to_str(self):
        return f"{self.address} {self.zip_code} {self.location} {self.city}"


@dataclass(frozen=True)
class Destiny:
    zip_code: str
    location: str
    city: str

    @property
    def to_str(self):
        return f"{self.zip_code} {self.location} {self.city}"


class Coordinate:
    def __init__(
        self, address: Address, destiny: Destiny, gmap: GMapsClient
    ) -> None:
        self.__address = address
        self.__destiny = destiny
        self.__gmapscli = gmap
        self.get_driving_routes()
        self.get_aereal_distance()

    @property
    def address(self):
        return self.__address

    @property
    def destiny(self):
        return self.__destiny

    def get_driving_routes(self):
        self.__drivingroutes = self.__gmapscli.directions(
            origin=self.__address.to_str,
            destination=self.__destiny.to_str,
            mode="driving",
            alternatives=True,
            units="meters",
        )
        self.__driving_distances = [
            distance["legs"][0]["distance"]["value"]
            for distance in self.__drivingroutes
        ]

        try:
            nearest = min(self.__driving_distances)
        except ValueError:
            ...
            # NO routes found

        route_index = self.__driving_distances.index(nearest)
        self.__shorter_driving_route = self.__drivingroutes[route_index][
            "legs"
        ][0]

    @property
    def shorter_driving_route(self):
        return self.__shorter_driving_route

    @property
    def shorter_driving_distance(self):
        return self.__shorter_driving_route["distance"]["value"]

    def get_aereal_distance(self):
        origin_coordinates = (
            self.shorter_driving_route["start_location"]["lat"],
            self.shorter_driving_route["start_location"]["lng"],
        )
        destiny_coordinates = (
            self.shorter_driving_route["end_location"]["lat"],
            self.shorter_driving_route["end_location"]["lng"],
        )
        self.__aereal_distance = great_circle(
            origin_coordinates, destiny_coordinates
        )

    @property
    def aereal_distance(self):
        return int(math.floor(self.__aereal_distance.m))

    @property
    def record(self):
        return {
            "origin": self.shorter_driving_route["start_address"],
            "destination": self.shorter_driving_route["end_address"],
            "kanton": self.__destiny.city,
            "country": self.shorter_driving_route["end_address"].rpartition(
                ","
            )[-1],
            "driving_distance": self.shorter_driving_distance,
            "aereal_distance": self.aereal_distance,
        }
