import click
import logging
import sys
import os

from warehouse_postalcode_generator import __version__
from .core import get_postal_codes

logger = logging.getLogger('warehouse_postalcode_generator')

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.command(
    name="warehouse_postalcode_generator", context_settings=CONTEXT_SETTINGS
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "-b",
    "--branches",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    help="""CSV file with branches list""",
)
@click.option(
    "-d",
    "--destinies",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    help="""csv file with destinies list""",
)
@click.option(
    "-a",
    "--aereal-distance",
    type=click.INT,
    required=True,
    help="""Aereal distance in meters""",
)
@click.option(
    "-D",
    "--driving-distance",
    type=click.INT,
    required=True,
    help="""Driving distance in meters""",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="output.csv",
    show_default=True,
    help="""CSV Output list""",
)
def cli(branches, destinies, aereal_distance, driving_distance, output):
    try:
        gmaps_key = os.environ["GMAPS_API_KEY"]
    except KeyError:
        logger.error("GMAPS_API_KEY is not defined in your environment")
        sys.exit(1)

    if driving_distance < aereal_distance:
        logger.error(
            "Invalid value for driving distance, "
            "must be greater than aereal distace."
        )
        sys.exit(1)

    get_postal_codes(
        branches=branches,
        destinies=destinies,
        aereal_distance=aereal_distance,
        driving_distance=driving_distance,
        output=output,
        api_key=gmaps_key,
    )
