#! /usr/bin/env python

#	Script to import OpenStreetMap data and apply changelists to keep it updated
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, March 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config


# Python includes
import argparse
import os
import sys
import time
#import urllib



def main():
#	log starting time of run
	starttime = time.time()

# parse arguments
	args = get_CLI_arguments()

# if we're not in verbose mode, log the starting time so it'll be findable in saved output.
	if not args.verbose:
		print time.ctime() + ": Starting run"
		sys.stdout.flush()

# 1) Read in a config file with the database parameters and list of region names to fetch from Geofabrik
# 2) Check if we already have that region in our database, and if not then fetch the full dataset
# 3) If we do have it, check what the most recently applied changeset was
# 4) Go through every changeset since that one, downloading, unzipping and applying it
# 5) Store a reference to the most recently applied changeset, either in a text file in the working directory or a metadata table in the database.


# Import:
# osm2pgsql -c -d osm_africa -p africa -K -r pbf -s -x -v -H localhost -U postgres -k -P 5433 --flat-nodes africa_flat-nodes -G -W africa-latest.osm.pbf

# Apply changelist:
# wget the changelist
# gunzip it, then:
# osm2pgsql -a -d osm_africa -K -s -x -v -H localhost -U postgres -k -P 5433 --flat-nodes africa_flat-nodes -p africa -G -W 738.osc




def get_CLI_arguments():
	parser = argparse.ArgumentParser(description="Import and/or update OSM data.")

# positional arguments
	parser.add_argument("regions", help="required argument: a list of regions to import, e.g. antarctica,australia-oceania/fiji", metavar="region1,region2/subregion2")

# optional arguments
	parser.add_argument("-v", "--verbose", help="output progress reports while working (default is "+str(config.verbose)+")", action="store_true", dest="verbose")

	args = parser.parse_args()

	args.regions = args.regions.split(',') # turn regions string into a list

	return args



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
