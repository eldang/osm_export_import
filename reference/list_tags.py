#! /usr/bin/env python

# Bootstrap to run export.py as a batch job 
# iterating over all available geographies
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, April 2015"
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config

# load shared helper functions
import helpers

# Python includes
import argparse
import os
import psycopg2                 # PostgreSQL interface: 
#                                 http://initd.org/psycopg/docs/
import sys
import time
import unicodecsv as csv  # unicode-aware replacement for the standard Python 
#                           csv module. 
#                           pip install unicodecsv. 
#                           https://github.com/jdunck/python-unicodecsv


def main():
  # Log starting time of run
  helpers.print_with_timestamp("Starting run.")
  starttime = time.time()

# Parse arguments and get started
  args = get_CLI_arguments()
  
  with psycopg2.connect(
      host=args.host, 
      port=args.port, 
      database=args.database, 
      user=args.user
  ) as conn:
    with conn.cursor() as cur:
      for datatype in ["line", "point", "polygon"]:
        helpers.print_with_timestamp("All tag values for " + datatype + "s:")
        seen_tags = []
        for prefix in args.prefix:
          colsquery = "SELECT column_name FROM information_schema.columns"
          colsquery += " WHERE table_schema = 'public'"
          colsquery += " AND table_name = '" + prefix + datatype + "'"
          colsquery += " AND column_name NOT IN ( \
              'osm_id', \
              'addr:housename', 'addr:housenumber', 'addr:interpolation', \
              'z_order', 'way_area', 'way' \
          );"
          # we may also want to exclude:
          # 'layer', 'name', 'population', 'ref', 'width', \
          cur.execute(colsquery)
          for col in cur.fetchall():
            if col[0] is not None:
              tagsquery = 'SELECT DISTINCT "' + col[0]
              tagsquery += '" FROM ' + prefix + datatype + ';'
              cur.execute(tagsquery)
              for val in cur.fetchall():
                if val[0] is not None:
                  tag = col[0] + "=" + val[0]
                  if tag not in seen_tags:
                    countquery = 'SELECT COUNT(osm_id)'
                    countquery += ' FROM ' + prefix + datatype
                    countquery += ' WHERE "' + col[0] + '"'
                    countquery += "='" + val[0].replace("'", "''") + "';"
                    cur.execute(countquery)
                    if int(cur.fetchone()[0]) >= args.threshold:
                      print tag
                      seen_tags += tag
        helpers.print_with_timestamp(
            "Found " 
            + str(len(seen_tags)) 
            + " unique tag-value combinations for "
            + datatype
            + "s."
        )
  
  helpers.print_with_timestamp(
      "Run complete in " + helpers.elapsed_time(starttime) + "."
  )

  

  
def get_CLI_arguments():
  parser = argparse.ArgumentParser(description="Export OSM data.")

# positional arguments
  parser.add_argument(
      "prefix", 
      help="required argument: the region we are exporting subsets from \
      (e.g. 'africa' or 'south-america')",
      metavar="region-name"
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
      "-t", "--threshold", 
      help="return only tag-value combinations that show up this many times", 
      nargs='?', default=1
  )



  args = parser.parse_args()
  args.prefix = [
      x.replace('/', '_').replace('-', '_') + "_" 
      for x in args.prefix.split(',')
  ]
  args.port = str(args.port)
  args.threshold = int(args.threshold)
  return args








if __name__ == "__main__":
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  main()
