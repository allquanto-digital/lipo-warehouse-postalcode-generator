import csv
import googlemaps
import logging
import os
import contextlib
import sys


ORIGIN_FILE = "filialen.csv"
DESTINY_FILE = "CH_PLZ_reduced_plus.csv"
OUTPUT_FILE = 'nearest_addresses.csv'
LOG_FILE = 'distance_gmap.log'
MIN_DISTANCE = 11000

# logger = logging.getLogger()
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

streamHandler = logging.StreamHandler(stream=sys.stdout)
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)

fileHandler = logging.FileHandler(filename=LOG_FILE, mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)


@contextlib.contextmanager
def csv_reader_without_header(filename: str):
    logger.debug(f"Opening CSV {filename}")
    with open(filename, "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        next(reader)
        yield reader


def main(gmaps_key: str):
    gmaps = googlemaps.Client(key=gmaps_key)

    logger.info("Starting...")
    with csv_reader_without_header(ORIGIN_FILE) as filialen:
        with csv_reader_without_header(DESTINY_FILE) as zip_code_file:
            with open(OUTPUT_FILE, "w") as near_addresses_file:
                csv_writer = csv.DictWriter(
                    near_addresses_file,
                    fieldnames=[
                        "origin",
                        "destination",
                        "country",
                        "distance",
                    ],
                )
                csv_writer.writeheader()
                for address in filialen:
                    for zip_code in zip_code_file:
                        try:
                            address_str=" ".join(address)
                            destiny_str=" ".join(zip_code)
                            response = gmaps.directions(
                                origin=address_str,
                                destination=destiny_str,
                                mode="driving",
                                alternatives=True,
                                units="meters",
                            )
                            # print(json.dumps(response, indent=4, sort_keys=True))

                            distances = [
                                dist["legs"][0]["distance"]["value"]
                                for dist in response
                            ]
                            logger.debug(f'Distances to {destiny_str} are: {distances}')

                            try:
                                nearest = min(distances)
                            except ValueError:
                                logger.error(
                                    f'Address {address_str} returned 0 '
                                    f'routes, Skipping...'
                                )
                                continue
                            
                            logger.debug(f'Minimal distance is {nearest}')

                            if nearest <= MIN_DISTANCE:
                                logger.info(
                                    f"Destination: {destiny_str} is inside the "
                                    f"minimal distance ({MIN_DISTANCE}), adding "
                                    "in the file."
                                )
                                nearest_index = distances.index(nearest)
                                nearest_leg = response[nearest_index]["legs"][0]
                                # print({
                                #         "distance": nearest_leg["distance"],
                                #         "start_address": nearest_leg[
                                #             "start_address"
                                #         ],
                                #         "end_addresss": nearest_leg["end_address"],
                                # })
                                csv_writer.writerow(
                                    {
                                        "origin": nearest_leg["start_address"],
                                        "destination": nearest_leg[
                                            "end_address"
                                        ].rpartition(",")[0],
                                        "country": nearest_leg[
                                            "end_address"
                                        ].rpartition(",")[-1],
                                        "distance": nearest_leg["distance"][
                                            "value"
                                        ],
                                    }
                                )
                                continue
                            logger.warning(
                                f"Destination: {destiny_str} is too far away, "
                                f"minimum distance is {nearest}"
                            )
                        except Exception as e:
                            logger.error(f"Error: [{type(e)}] {str(e)}")
                            raise


if __name__ == "__main__":
    main(gmaps_key=os.environ["GMAPS_API_KEY"])
