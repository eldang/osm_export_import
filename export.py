#! /usr/bin/env python

#	Script to export OpenStreetMap data subsetted by geography and tag set
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, April 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config


# Python includes
import argparse
import os
import psycopg2 								# PostgreSQL interface: http://initd.org/psycopg/docs/
import subprocess
import sys
import time



def main():
#	Log starting time of run
	starttime = time.time()

# Parse arguments and get stated
	args = get_CLI_arguments()
	print_with_timestamp("Starting run.")


	print_with_timestamp("Run complete in " + elapsed_time(starttime) + ".")






def get_CLI_arguments():
	parser = argparse.ArgumentParser(description="Export OSM data.")

# positional arguments
	parser.add_argument("prefix", help="required argument: the region we are exporting from (e.g. 'africa' or 'south-america')", metavar="region-name")
	parser.add_argument("subset", help="required argument: the region we are subsetting to (e.g. 'kenya' or 'rift valley')", metavar="'subregion name'")
	parser.add_argument("outfile", help="required argument: file to save output to", metavar="filename.ext")

# optional arguments
	parser.add_argument("-v", "--verbose", help="output progress reports while working (default is "+str(config.verbose)+")", action="store_true")

	parser.add_argument("-H", "--host", help="override the default database host, which is currently: %(default)s", nargs='?', default=config.host, metavar="localhost|URL")
	parser.add_argument("-p", "--port", help="override the default database port, which is currently: %(default)s", nargs='?', default=config.port)
	parser.add_argument("-u", "--user", help="override the default database username", nargs='?', default=config.user)
	parser.add_argument("-d", "--database", help="override the default database name, which is currently: %(default)s", nargs='?', default=config.database)

	parser.add_argument("-f", "--output_format", help="format for output", nargs='?', default=config.output_format)

	parser.add_argument("-s", "--schema", help="database schema where the geographies to subset by are stored", nargs='?', default=config.schema)

	parser.add_argument("-rt", "--regions_table", help="database table containing supranational region-level geometries to subset by", nargs='?', default=config.regions_table)
	parser.add_argument("-rf", "--region_field", help="region name field in that table", nargs='?', default=config.region_field)

	parser.add_argument("-ct", "--countries_table", help="database table containing country outline geometries to subset by", nargs='?', default=config.countries_table)
	parser.add_argument("-cf", "--country_field", help="country name field in that table", nargs='?', default=config.country_field)

	parser.add_argument("-pt", "--provinces_table", help="database table containing subnatinoal state- or province-level geometries to subset by", nargs='?', default=config.provinces_table)
	parser.add_argument("-pf", "--province_field", help="state/province name field in that table", nargs='?', default=config.province_field)
	parser.add_argument("-pcf", "--province_country_field", help="country name field in that table - this only matters if the province name exists in more than one country (though this is not an unusual occurence)", nargs='?', default=config.province_country_field)
	parser.add_argument("-pcfn", "--province_country_name", help="name of the country that the province we're subsetting by is in. Required if setting --province_country_field; ignored otherwise/", nargs='?', default=config.province_country_field)


	args = parser.parse_args()
	args.prefix = args.prefix.replace('/', '_').replace('-', '_') + "_"
	return args





def print_with_timestamp(msg):
	print time.ctime() + ": " + str(msg)
	sys.stdout.flush() # explicitly flushing stdout makes sure that a .out file stays up to date - otherwise it can be hard to keep track of whether a background job is hanging




def elapsed_time(starttime):
	seconds = time.time() - starttime
	if seconds < 1: seconds = 1
	hours = int(seconds / 60 / 60)
	minutes = int(seconds / 60 - hours * 60)
	seconds = int(seconds - minutes * 60 - hours * 60 * 60)
	return str(hours) + " hours, " + str(minutes) + " minutes and " + str(seconds) + " seconds"



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
