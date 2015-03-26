#! /usr/bin/env python

#	Script to import OpenStreetMap data and apply changelists to keep it updated
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, March 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config


# Python includes
import argparse
from bs4 import BeautifulSoup		# HTML parser: pip install beautifulsoup4
import os
import requests 								# HTTP interface: pip install requests
import subprocess
import sys
import time



def main():
#	Log starting time of run
	starttime = time.time()

# Parse arguments
	args = get_CLI_arguments()

	print time.ctime() + ": Starting run"
	sys.stdout.flush()

# Step through requested regions, either kicking off fresh imports or looking for changesets
	for region in args.regions:
		if os.path.isdir(region):
# TODO: check for actual files before proceeding
			print time.ctime() + ": Found previous data for " + region + ". Checking for updates to apply."
		else:
			print time.ctime() + ": No previous data found for " + region + ". Starting a fresh import."
			fresh_import(region, args)




def fresh_import(region, args):
# Make the directory we'll use to store data for this region
	os.makedirs(region)
	os.chdir(region)
# Find the latest changelist number and store that
	changeset_dir = "http://download.geofabrik.de/" + region + "-updates/000/000/"
	r = requests.get(changeset_dir)
	latest = BeautifulSoup(r.text).find_all('a')[-1].get('href').split('.')[0]
	with open('latest_changeset.txt', 'w') as outfile:
		outfile.write(changeset_dir+latest)
# Download the .pbf file
	pbf_url = "http://download.geofabrik.de/" + region + "-latest.osm.pbf"
	r = requests.get(pbf_url)
	with open('mapdata.osm.pbf', 'wb') as outfile:
		for chunk in r.iter_content(100):
			outfile.write(chunk)
# Import the file we've just downloaded
	import_cmd = ["osm2pgsql", "-H", args.host, "-P", str(args.port)]
	import_cmd += ["-d", args.database, "-U", args.user]
	import_cmd += ["-p", region.replace('/', '_').replace('-', '_')]
	import_cmd += ["-K", "-s", "-x", "-G", "-r", "pbf"]
	if args.verbose: import_cmd += ["-v"]
	import_cmd += ["mapdata.osm.pbf"]
	if args.verbose:
		subprocess.call(import_cmd)
	else: # suppress osm2pgsql's output
		with open(os.devnull, 'w') as FNULL:
			subprocess.call(import_cmd, stdout=FNULL, stderr=subprocess.STDOUT)
# Clean up
	os.remove('mapdata.osm.pbf')
	for i in region.split('/'):
		os.chdir('..')
	print time.ctime() + ": Initial import of " + region + " complete."
# Immediately call update() in case another changelist dropped while we were downloading



# Apply changelist:
# 3) If we do have it, check what the most recently applied changeset was
# 4) Go through every changeset since that one, downloading, unzipping and applying it
# wget the changelist
# gunzip it, then:
# osm2pgsql -a -d osm_africa -K -s -x -v -H localhost -U postgres -k -P 5433 --flat-nodes africa_flat-nodes -p africa -G -W 738.osc
# clean up with http://wiki.openstreetmap.org/wiki/User:Stephankn/knowledgebase#Cleanup_of_ways_outside_the_bounding_box




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
