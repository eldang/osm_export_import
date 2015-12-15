#! /usr/bin/env python

# Script to import OpenStreetMap data and apply changelists to keep it updated
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, March 2015"
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config

# load shared helper functions
import helpers


# Python includes
import argparse
from bs4 import BeautifulSoup  # HTML parser: pip install beautifulsoup4
import os
import psycopg2                # PostgreSQL interface:
#                                 http://initd.org/psycopg/docs/
import requests                # HTTP interface: pip install requests
import subprocess
import sys
import time



def main():
  # Log starting time of run
  starttime = time.time()

# Parse arguments and get started
  args = get_CLI_arguments()
  print " "  # just to get a newline
  helpers.print_with_timestamp("Starting run.")
  os.chdir(args.working_directory)

# Step through requested regions,
# either kicking off fresh imports or looking for changesets
  for region in args.regions:
    if os.path.isdir(region):
      # TODO: check for actual files before proceeding
      helpers.print_with_timestamp(
          "Found previous data for " + region
          + ". Checking for updates to apply."
      )
      args = update_import(region, args)
    else:
      helpers.print_with_timestamp(
          "No previous data found for " + region + ". Starting a fresh import."
      )
      args = fresh_import(region, args)

  if args.vacuum:
    if args.verbose:
      helpers.print_with_timestamp(
          "Calling VACUUM FULL for final database housekeeping."
      )
    with psycopg2.connect(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user
    ) as conn:
      conn.set_session(autocommit=True)  # needed for VACUUM call
      with conn.cursor() as cur:
        cur.execute("VACUUM FULL;")

  helpers.print_with_timestamp(
      "Run complete in " + helpers.elapsed_time(starttime) + "."
  )




def fresh_import(region, args):
  # Make the directory we'll use to store data for this region
  os.makedirs(region)
  os.chdir(region)
# Find the latest changelist number and store that
  changeset_dir = (
      "http://download.geofabrik.de/" + region + "-updates/000/000/"
  )
  r = requests.get(changeset_dir)
  latest = BeautifulSoup(r.text, "lxml").find_all('a')[-1].get('href').split('.')[0]
  with open('latest_changeset.txt', 'w') as outfile:
    outfile.write(latest)
# Download the .pbf file
  pbf_url = "http://download.geofabrik.de/" + region + "-latest.osm.pbf"
  r = requests.get(pbf_url)
  with open('mapdata.osm.pbf', 'wb') as outfile:
    for chunk in r.iter_content(100):
      outfile.write(chunk)
# Import the file we've just downloaded
  import_cmd = [
      args.osm2pgsql_path, "-c", "-H", args.host, "-P", str(args.port),
      "-d", args.database, "-U", args.user,
      "-p", region.replace('/', '_').replace('-', '_'),
      "-K", "-s", "-x", "-G", "-r", "pbf"
  ]
  if args.verbose:
    import_cmd += ["-v"]
  import_cmd += ["mapdata.osm.pbf"]
  if args.verbose:
    subprocess.call(import_cmd)
  else:  # suppress osm2pgsql's output
    with open(os.devnull, 'w') as FNULL:
      subprocess.call(import_cmd, stdout=FNULL, stderr=subprocess.STDOUT)
# Clean up
  os.remove('mapdata.osm.pbf')
  os.chdir(args.working_directory)
  helpers.print_with_timestamp("Initial import of " + region + " complete.")
# Immediately call update_import() in case another changelist dropped while
# we were downloading
  args = update_import(region, args)
  return args




def update_import(region, args):
  applied_changelists = 0
  prefix = region.replace('/', '_').replace('-', '_')
# Find the ID of the most recently applied changelist
  os.chdir(region)
  with open('latest_changeset.txt', 'r') as infile:
    latest = infile.read()

# Go through every changeset since that one:
  changeset_dir = (
      "http://download.geofabrik.de/" + region.rstrip("/") + "-updates/000/000/"
  )
  r = requests.get(changeset_dir)
  urls = BeautifulSoup(r.text, "lxml").find_all('a')
  for url in urls:
    urlparts = url.get('href').split('.')
    if urlparts[-1] == 'gz' and urlparts[0] > latest:
      changeset_url = changeset_dir + url.get('href')
# Download the next changeset
      if args.verbose:
        helpers.print_with_timestamp("Downloading changeset " + changeset_url)
      r = requests.get(changeset_url)
      with open('changeset.osc.gz', 'wb') as outfile:
        for chunk in r.iter_content(10):
          outfile.write(chunk)
# Unzip it (-f to force overwriting of any previous changeset.osc left around)
      if args.verbose:
        helpers.print_with_timestamp("Changeset downloaded. Unpacking.")
      subprocess.call(['gunzip', '-f', 'changeset.osc.gz'])
# Call osm2pgsql to apply it
      if args.verbose:
        helpers.print_with_timestamp("Unpacked. Now calling osm2pgsql")
      update_cmd = [
          args.osm2pgsql_path, "-a", "-H", args.host, "-P", str(args.port),
          "-d", args.database, "-U", args.user,
          "-p", prefix,
          "-K", "-s", "-x", "-G"
      ]
      if args.verbose:
        update_cmd += ["-v"]
      update_cmd += ["changeset.osc"]
      if args.verbose:
        subprocess.call(update_cmd)
      else:  # suppress osm2pgsql's output
        with open(os.devnull, 'w') as FNULL:
          subprocess.call(update_cmd, stdout=FNULL, stderr=subprocess.STDOUT)
# Clean up and report
      os.remove('changeset.osc')
      helpers.print_with_timestamp("Applied changelist #" + urlparts[0])
      applied_changelists += 1
      with open('latest_changeset.txt', 'w') as outfile:
        outfile.write(urlparts[0])
# Check if it's time to clean up the database
  if os.path.isfile('changesets_applied_since_cleanup.txt'):
    with open('changesets_applied_since_cleanup.txt', 'r') as infile:
      cumulative_changelists = applied_changelists + int(infile.read())
  else:
    cumulative_changelists = applied_changelists
  if cumulative_changelists >= int(args.clean_interval):
    dbcleanup(args, prefix)
    args.vacuum = True
    with open('changesets_applied_since_cleanup.txt', 'w') as outfile:
      outfile.write('0')
  else:
    with open('changesets_applied_since_cleanup.txt', 'w') as outfile:
      outfile.write(str(cumulative_changelists))

  os.chdir(args.working_directory)
  helpers.print_with_timestamp(
      "Applied " +
      str(applied_changelists) + " change lists to " +
      region + " data."
  )
  return args




# Clean up db as suggested at
# http://wiki.openstreetmap.org/wiki/User:Stephankn/knowledgebase#Cleanup_of_ways_outside_the_bounding_box
def dbcleanup(args, prefix):
  if args.verbose:
    helpers.print_with_timestamp(
        "Pruning database nodes orphaned by recent updates."
    )
  with psycopg2.connect(
      host=args.host,
      port=args.port,
      database=args.database,
      user=args.user
  ) as conn:
    with conn.cursor() as cur:
      prefix += '_'
      cur.execute(
          "DELETE FROM " + prefix + "ways AS w \
          WHERE 0 = (SELECT COUNT(1) FROM " + prefix + "nodes AS n \
          WHERE n.id = ANY(w.nodes));"
      )
      cur.execute(
          "DELETE FROM " + prefix + "rels AS r \
          WHERE 0 = (SELECT COUNT(1) FROM " + prefix + "nodes AS n \
          WHERE n.id = ANY(r.parts)) \
          AND 0 = (SELECT COUNT(1) FROM " + prefix + "ways AS w \
          WHERE w.id = ANY(r.parts));"
      )
      cur.execute("REINDEX TABLE " + prefix + "ways;")
      cur.execute("REINDEX TABLE " + prefix + "rels;")
      cur.execute("REINDEX TABLE " + prefix + "nodes;")





def get_CLI_arguments():
  parser = argparse.ArgumentParser(
      description="Import and/or update OSM data."
  )

# positional arguments
  parser.add_argument(
      "regions",
      help="required argument: a list of regions to import, \
          e.g. antarctica,australia-oceania/fiji",
      metavar="region1,region2/subregion2"
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
      "-w", "--working_directory",
      help="working directory, which defaults to \
          the directory the program is called from \
          (you'll probably need to set this explicitly in a cron job)",
      nargs='?', default=os.getcwd()
  )
  parser.add_argument(
      "-c", "--clean_interval",
      help="after applying this many changesets, \
          do the periodic database cleaning",
      nargs='?', default=config.clean_interval
  )
  parser.add_argument(
      "-o", "--osm2pgsql_path",
      help="full path to the osm2pgsql command as installed on your system \
          (you may need to specify this for cron jobs)",
      nargs='?', default="osm2pgsql"
  )

  args = parser.parse_args()
  args.regions = args.regions.split(',')  # turns regions string into a list
  args.vacuum = False  # will programmatically set True as appropriate
  return args




if __name__ == "__main__":
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  main()
