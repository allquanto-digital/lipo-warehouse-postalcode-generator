# Warehouse PostalCode Generator

- Requires python 3.9.10 or newer.

## Usage

Requires:

- CSV with branches
- CSV with destinations
- aereal minimal distance (integer)
- driving minimal distance (integer)

```
warehouse_postalcode_generator \
    -b branches.csv \
    -d destinations.csv \
    -a 10000 \
    -D 15000
```

Will search for driving distances not greater than 15Km, and aereal distances not greater than 10Km.
The default output file is `output.csv`, but you can specify another name with option `-o`.

```
warehouse_postalcode_generator \
    -b branches.csv \
    -d destinations.csv \
    -a 10000 \
    -D 15000 \
    -o 15kdriving_10kaereal_list.csv
```

## Install

- Requires git

### Using pip

```
pip install git+https://github.com/allquanto-digital/lipo-warehouse-postalcode-generator.git
```

### Using Make:

```
make install
hash -r
```
