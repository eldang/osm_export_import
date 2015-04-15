#! /usr/bin/env python

# Bootstrap to run export.py as a batch job 
# iterating over all available geographies
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, April 2015"
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config

# load shared helper functions
import helpers

# load the export script to which this is a bootstrap
import export

# Python includes
import argparse
import os
import psycopg2                # PostgreSQL interface: 
#                                 http://initd.org/psycopg/docs/
import string
import sys
import time



def main():
  # Log starting time of run
  helpers.print_with_timestamp("Starting run.")
  starttime = time.time()

# Parse arguments and get started
  args = get_CLI_arguments()
  
  for geography in get_all_geographies(args):
    key = geography[0].replace("&", "and")
    key = key.translate(string.maketrans("", ""), string.punctuation)
    key = key.replace(" ", "-")
    args.subset = key
    if len(geography) == 1:
      args.outfile = key.lower()
      print key
      helpers.print_with_timestamp("Exporting " + key + ".")
    else:
      country = geography[1].replace("&", "and")
      country = country.translate(string.maketrans("", ""), string.punctuation)
      country = country.replace(" ", "-")
      args.subset = key
      args.outfile = country.lower() + "_" + key.lower()
      args.province_country_name = country
      helpers.print_with_timestamp("Exporting " + key + ", " + country + ".")

    export.export(args)

  helpers.print_with_timestamp(
      "Run complete in " + helpers.elapsed_time(starttime) + "."
  )

  
  
def get_all_geographies(args):
  if args.category == "region":
    sqlcmd = (
        "SELECT DISTINCT " + args.region_field +
        " FROM " + args.schema + "." + args.regions_table + ";"
    )
  elif args.category == "country":
    sqlcmd = (
        "SELECT DISTINCT " + args.country_field +
        " FROM " + args.schema + "." + args.countries_table + ";"
    )
  elif args.category == "province":
    if args.province_country_field is not None:
      sqlcmd = (
          "SELECT DISTINCT " + args.province_field + 
          ", " + args.province_country_field + 
          " FROM " + args.schema + "." + args.provinces_table + ";"
      )
    else:
      sqlcmd = (
          "SELECT DISTINCT " + args.province_field +
          " FROM " + args.schema + "." + args.provinces_table + ";"
      )
  
  with psycopg2.connect(
      host=args.host, 
      port=args.port, 
      database=args.database, 
      user=args.user
  ) as conn:
    with conn.cursor() as cur:
      cur.execute(sqlcmd)
      return cur.fetchall()
  

  
def get_CLI_arguments():
  parser = argparse.ArgumentParser(description="Export OSM data.")

# positional arguments
  parser.add_argument(
      "prefix", 
      help="required argument: the region we are exporting subsets from \
      (e.g. 'africa' or 'south-america')",
      metavar="region-name"
  )
  parser.add_argument(
      "category", 
      help="required argument: the geographic level we're subsetting by. \
      Either 'region', 'country' or 'province'.", 
      metavar="region|country|province"
  )

# optional arguments
  parser.add_argument(
      "-v", "--verbose", 
      help="output progress reports while working \
          (default is " + str(config.verbose) + ")", 
      action="store_true"
  )

  parser.add_argument(
      "-H", "--host", 
      help="override the default database host, which is currently: \
          %(default)s", 
      nargs='?', default=config.host, metavar="localhost|URL"
  )
  parser.add_argument(
      "-p", "--port", 
      help="override the default database port, which is currently: \
          %(default)s", 
      nargs='?', default=config.port
  )
  parser.add_argument(
      "-u", "--user", 
      help="override the default database username", 
      nargs='?', default=config.user
  )
  parser.add_argument(
      "-d", "--database", 
      help="override the default database name, which is currently: \
          %(default)s", 
      nargs='?', default=config.database
  )

  parser.add_argument(
      "-f", "--output_format", 
      help="format for output, which is $(default)s by default", 
      nargs='?', default=config.output_format
  )

  parser.add_argument(
      "-b", "--buffer_radius", 
      help="add a buffer of this many metres beyond the specified subset boundary.\
      WARNING: SQL queries using this are extremely slow.", 
      nargs='?', default=config.buffer_radius
  )

  parser.add_argument(
      "-s", "--schema", 
      help="database schema where the geographies to subset by are stored", 
      nargs='?', default=config.schema
  )

  parser.add_argument(
      "-rt", "--regions_table", 
      help="database table containing supranational region-level geometries to \
          subset by", 
      nargs='?', default=config.regions_table
  )
  parser.add_argument(
      "-rf", "--region_field", 
      help="region name field in that table", 
      nargs='?', default=config.region_field
  )

  parser.add_argument(
      "-ct", "--countries_table", 
      help="database table containing country outline geometries to subset by", 
      nargs='?', default=config.countries_table
  )
  parser.add_argument(
      "-cf", "--country_field", 
      help="country name field in that table", 
      nargs='?', default=config.country_field
  )

  parser.add_argument(
      "-pt", "--provinces_table", 
      help="database table containing subnational state- or province-level \
          geometries to subset by", 
      nargs='?', default=config.provinces_table
  )
  parser.add_argument(
      "-pf", "--province_field", 
      help="state/province name field in that table", 
      nargs='?', default=config.province_field
  )
  parser.add_argument(
      "-pcf", "--province_country_field", 
      help="country name field in that table - \
          this only matters if the province name exists in >1 country \
          (though this is not an unusual occurence)", 
      nargs='?', default=config.province_country_field
  )
  parser.add_argument(
      "-pcfn", "--province_country_name", 
      help="name of the country that the province we're subsetting by is in. \
          Required if setting --province_country_field; ignored otherwise.", 
      nargs='?', default=None
  )

  args = parser.parse_args()
  args.prefix = [
      x.replace('/', '_').replace('-', '_') + "_" 
      for x in args.prefix.split(',')
  ]
  args.port = str(args.port)
  args.buffer_radius = str(args.buffer_radius)
  return args








if __name__ == "__main__":
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  main()
