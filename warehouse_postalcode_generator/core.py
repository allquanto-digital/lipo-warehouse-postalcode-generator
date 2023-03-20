from .fileop import csv_reader_without_header, csv_output_file
import googlemaps
import logging
from .coordinates import Address, Destiny, Coordinate

logger = logging.getLogger("warehouse_postalcode_generator")


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
                            coord = Coordinate(
                                address=Address(*address),
                                destiny=Destiny(*destiny),
                                gmap=gmaps_api,
                            )

                            if coord.aereal_distance > aereal_distance:
                                logger.warning(
                                    f"Destination {coord.destiny.to_str} "
                                    f"aereal distance ({coord.aereal_distance})"
                                    " is outside the mininal distance "
                                    f"({aereal_distance}), Skipping"
                                )
                                continue
                            if (
                                coord.shorter_driving_distance
                                > driving_distance
                            ):
                                logger.info(
                                    f"Destiny {coord.destiny.to_str} "
                                    f"driving distance ("
                                    f"{coord.shorter_driving_distance}) is "
                                    "outside the minimal distance ("
                                    f"{driving_distance}), but still will"
                                    "be added"
                                )
                                outputfile.writerow(coord.record)
                                continue
                            logger.info(
                                f"Destiny {coord.destiny.to_str} matches "
                                f"all criteria driving distance: "
                                f"{coord.shorter_driving_distance}, aereal: "
                                f"{coord.aereal_distance}, expected: "
                                f"{driving_distance} and {aereal_distance}"
                            )
                            outputfile.writerow(coord.record)
                        except Exception as e:
                            logger.error(f"{e}", exc_info=True)
                            raise
