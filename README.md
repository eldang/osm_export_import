# Automating OpenStreetMap imports

## Overview

This is a pair of scripts to simplify and automate two Open Street Map related process:

**import.py** is for making a local mirror of one or more geographical areas, and keeping that up to date.

**export.py** is for exporting subsets of that local mirror, for smaller geographic areas.

These were made for a specific project, and design choices will probably reflect that. I have tried to write them in as generally reusable a form as possible. I think **import.py** should be very easy to apply to other cases; **export.py** will need more setup and possibly tinkering. There's more information about the choices made in [background.md](background.md)

## Requirements

A PostGIS database already set up, with [hstore](https://wiki.openstreetmap.org/wiki/Osm2pgsql#hstore) enabled.

The [osm2pgsql](https://wiki.openstreetmap.org/wiki/Osm2pgsql) and [ogr2ogr](http://www.gdal.org/ogr2ogr.html) tools (the latter is easiest to install as part of the [GDAL](https://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries) package). These scripts are really just a wrapper around those utilities.

The following Python modules:

```python
argparse
bs4    # HTML parser: pip install beautifulsoup4
os
psycopg2    # PostgreSQL interface: http://initd.org/psycopg/docs/
requests    # HTTP interface: pip install requests
subprocess
sys
time
zipfile
```

All the ones without a comment about installation or documentation are normally part of a default Python install.

You will also need to set up a [.pgpass file](http://www.postgresql.org/docs/9.1/static/libpq-pgpass.html) as the scripts themselves neither store nor prompt for passwords.

## Usage

### import.py

#### Setup

1. Copy both `import.py` and `config.py` to your working directory
2. Edit the `### shared server config` block to reflect your PostgreSQL setup
3. Give yourself execute permission on the script, with `chmod u+x import.py`. This step is optional, but without it you'll always have to explicitly call python to run the script.

#### Basic syntax

```shell
./import.py regions
```

Where regions is a comma-separated list of geographical area names, in the format that Geofabrik uses for directory names at [http://download.geofabrik.de/](http://download.geofabrik.de/). Each region will be given its own set of tables in the `public` schema of your database, prefixed by the region name with all punctuation normalised to underscores. Some examples:

* To import the entire continent of Antarctica: `./import.py antarctica` which produces a set of `antarctica_...` tables.
* To import the entire continents of Africa and South America: `./import.py africa,south-america` which produces a set of `africa_...` tables and a set of `south-america_...`.
* To import the province of Ontario: `./import.py north-america/canada/ontario` which produces a set of `north_america_canada_ontario_...` tables.

When making a fresh import, the script also creates a local directory with the same name/structure as Geofabrik's, in which it stores some tiny text files to track progress. As long as you leave this directory in place, the next time you call it for the same region it will be detect that a fresh import is not needed, and apply all the new changelists created since it was last run.

#### Advanced options

* If calling this from a cron job, you may need to specify the working directory, which you can do with the `-w` option, and/or the path to the osm2pgsql command, which you can do with the `-o` option.
* There is some [routine database cleanup](http://wiki.openstreetmap.org/wiki/User:Stephankn/knowledgebase#Cleanup_of_ways_outside_the_bounding_box) that should be done from time to time, but is also very time consuming.  The `-c` option specifies how many changelists to apply between doing that cleanup.  Larger values save time, but potentially at the cost of storage space.
* `-v` gives you verbose output. I recommend using this when running the command interactively, and not when scheduling it.

### export.py

#### Setup

1. Copy both `export.py` and `config.py` to your working directory.
2. Give yourself execute permission on the script, with `chmod u+x export.py`. This step is optional, but without it you'll always have to explicitly call python to run the script.
3. Edit the `### shared server config` block of `config.py` to reflect your PostgreSQL setup (if you're also using `import.py` the same settings should work).
4. If you don't already have them, create at least one table on your database that contains geometries by which you want to filter output, in a column named `the_geom`, and some kind of unique identifier (name, number, ISO code - it doesn't matter as long as it's unique) for each of those geometries.  *NB: the structure this script was written for has three such tables: one for supra-national regions, one for countries, and one for sub-national provinces. You don't have to copy this, but the wording of the options will make more sense if you have it in mind.*
5. Edit the `## Export-only:` block of `config.py` to reflect the table structure you've just created. `regions_table` is where the script will look for geometries at the `region` administrative level, and `region_field` is the field it will search by. The equivalent goes for countries and provinces, and provinces have an additional field, to specify country names in case of province names that exist in more than one country.

#### Basic syntax

```shell
./export.py database-prefix adminlevel 'subregion name' filename_with_no_extension
```

Where:

* `database-prefix` is the prefix created by `import.py`, e.g. `africa` or `south-america`
* `adminlevel` is one of `region`, `country` or `province`
* `'subregion name'` is the name or ID of the region, country or province we are filtering by. It is case insensitive and only needs to be in quotes if it contains a space.
* `filename_with_no_extension` is the filename you want output stored in.

Without additional arguments, the script will export three Spatialite files for the area specified—one containing all lines, one containing all points, and one containing all polygons—and then package them as a single zip archive.

#### Advanced options

* `-v` gives you verbose output. I recommend using this when running the command interactively, and not when scheduling it.
* `-f shp` will produce shapefiles instead of Spatialite.
* If exporting a province with a non-unique name, add `-pcfn countryname` to specify which country you want.


