from .fileop import csv_reader_without_header, csv_output_file
import googlemaps
import logging
from geopy.distance import great_circle
import math

logger = logging.getLogger('warehouse_postalcode_generator')


def list_to_str(l: list) -> str:
    return " ".join(l)


def get_distances(d: dict) -> list:
    return [dist["legs"][0]["distance"]["value"] for dist in d]


def locate_leg_by_index(distances: list, nearest: int, response: dict) -> dict:
    index = distances.index(nearest)
    return response[index]["legs"][0]

def get_greatcircle_distance(data: dict):
    origin_location = data["start_location"]
    destiny_location = data["end_location"]
    origin = (origin_location["lat"], origin_location["lng"])
    destiny = (destiny_location["lat"], destiny_location["lng"])
    return great_circle(origin, destiny)

def get_postal_codes(
    branches: str,
    destinies: str,
    aereal_distance: int,
    driving_distance: int,
    output: str,
    api_key: str,
):
    gmaps_api = googlemaps.Client(api_key)

    with csv_reader_without_header(branches) as branchfile:
        with csv_reader_without_header(destinies) as destinyfile:
            with csv_output_file(output) as outputfile:
                for address in branchfile:
                    for destiny in destinyfile:
                        try:
                            address_str = list_to_str(address)
                            destiny_str = list_to_str(destiny)
                            response = gmaps_api.directions(
                                origin=address_str,
                                destination=destiny_str,
                                mode="driving",
                                alternatives=True,
                                units="meters",
                            )

                            distances = get_distances(response)

                            try:
                                nearest = min(distances)
                            except ValueError:
                                logger.error(
                                    f"Address {address_str} returned 0 "
                                    f"routes, Skipping..."
                                )
                                continue

                            logger.debug(f"Minimal distance is {nearest}")

                            if nearest <= driving_distance:
                                logger.info(
                                    f"Destination: {destiny_str} is inside the "
                                    f"minimal distance ({driving_distance})"
                                )
                                leg = locate_leg_by_index(
                                    distances=distances,
                                    nearest=nearest,
                                    response=response,
                                )

                                aereal = get_greatcircle_distance(leg)

                                if aereal.m > aereal_distance:
                                    logger.warning(
                                        f"Destination: {destiny_str} aereal "
                                        "distance is greater than expected."
                                    )
                                    continue

                                logger.info(
                                    f"Destination: {destiny_str} aereal "
                                    "distance are inside the range "
                                    f"({aereal_distance})"
                                )
                                outputfile.writerow(
                                    {
                                        "origin": leg["start_address"],
                                        "destination": leg["end_address"],
                                        "kanton": destiny[2],
                                        "country": leg[
                                            "end_address"
                                        ].rpartition(",")[-1],
                                        "driving_distance": leg["distance"][
                                            "value"
                                        ],
                                        "aereal_distance": int(
                                            math.floor(aereal.m)
                                        ),
                                    }
                                )

                                continue
                            logger.warning(
                                f"Destination: {destiny_str} is too far away, "
                                f"minimum distance is {nearest}"
                            )
                        except Exception as e:
                            logger.error(f"{e}", exc_info=True)
                            raise
