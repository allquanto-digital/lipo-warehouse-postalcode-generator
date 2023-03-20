import csv
import contextlib
import logging

logger = logging.getLogger("warehouse_postalcode_generator")


@contextlib.contextmanager
def csv_reader_without_header(filename: str):
    logger.debug(f"Opening CSV {filename}")
    with open(filename, "r") as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        next(reader)
        yield reader


@contextlib.contextmanager
def csv_output_file(filename: str):
    logger.debug(f"Opening CSV {filename} for writing")
    with open(filename, "w") as output_file:
        csv_writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "origin",
                "destination",
                "kanton",
                "country",
                "driving_distance",
                "aereal_distance",
            ],
        )
        csv_writer.writeheader()
        yield csv_writer
