#! /usr/bin/env python

#	Script to import OpenStreetMap data and apply changelists to keep it updated
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, March 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config


# Python includes
import argparse
from bs4 import BeautifulSoup		# HTML parser
import os
import requests 								# HTTP interface
import sys
import time



def main():
#	Log starting time of run
	starttime = time.time()

# Parse arguments
	args = get_CLI_arguments()

	print time.ctime() + ": Starting run"
	sys.stdout.flush()

# Load password if previously stored, or ask user for it if not found.
	if os.path.isfile('pw.txt'):
		infile = open('pw.txt', 'r')
		args.password = infile.read()
		infile.close()
		if args.verbose: print "Found previously set password. Delete pw.txt if you need to reset it."
	else:
		args.password = raw_input("Enter the password for user " + args.user + " on database " + args.database + ": ")
		outfile = open('pw.txt', 'w')
		outfile.write(args.password)
		outfile.close()

# Step through requested regions, either kicking off fresh imports or looking for changesets
	for region in args.regions:
		if os.path.isdir(region):
# TODO: check for actual files before proceeding
			if args.verbose: print "Found previous data for " + region + ". Checking for updates to apply."
		else:
			if args.verbose: print "No previous data found for " + region + ". Starting a fresh import."
			fresh_import(region, args)

# 2) Check if we already have that region in our database, and if not then fetch the full dataset
# 3) If we do have it, check what the most recently applied changeset was
# 4) Go through every changeset since that one, downloading, unzipping and applying it
# 5) Store a reference to the most recently applied changeset, either in a text file in the working directory or a metadata table in the database.



def fresh_import(region, args):
# Make the directory we'll use to store data for this region
	os.makedirs(region)
	os.chdir(region)
# Find the latest changelist number and store that
	changeset_dir = "http://download.geofabrik.de/" + region + "-updates/000/000/"
	r = requests.get(changeset_dir)
	latest = BeautifulSoup(r.text).find_all('a')[-1].get('href').split('.')[0]
	outfile = open('latest_changeset.txt', 'w')
	outfile.write(latest)
	outfile.close
# Download the .pbf file
# Import the file we've just downloaded
# osm2pgsql -c -d osm_africa -p africa -K -r pbf -s -x -v -H localhost -U postgres -k -P 5433 --flat-nodes africa_flat-nodes -G -W africa-latest.osm.pbf
# Clean up
	for i in region.split('/'):
		os.chdir('..')
# Immediately call update() in case another changelist dropped while we were downloading

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
	parser.add_argument("-H", "--host", help="override the default database host, which is currently: %(default)s", nargs='?', default=config.host, metavar="localhost|URL")
	parser.add_argument("-p", "--port", help="override the default database port, which is currently: %(default)s", nargs='?', default=config.port)
	parser.add_argument("-u", "--user", help="override the default database username", nargs='?', default=config.user)
	parser.add_argument("-d", "--database", help="override the default database name, which is currently: %(default)s", nargs='?', default=config.database)

	args = parser.parse_args()

	args.regions = args.regions.split(',') # turn regions string into a list

	return args



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
