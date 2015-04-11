# Default values for server config and script behaviour.
# Most can be overriden with command line arguments
# Where this is true, the name of the argument is provided as a comment at the end of the line

__name__ = "config"


### shared server config
host				= "localhost"			# -H or --host
port				= 5433 # 5432 is the postgresql default
database		= "osm_africa"		# -d or --database
user				= "postgres"			# -u or --user
# password has to either be entered manually or stored in .pgpass
# unfortunately, osm2pgsql doesn't seem to have a way to specify schemas, so we'll always be creating tables in the public scheme



# Should we give verbose output and wait for acknowledgement from the user before quitting?
verbose			=	False						# -v or --verbose



## Import-only:
# After how many changesets should we do the database cleanup?
clean_interval	= 5						# -c or --clean_interval




## Export-only:
# schema in which the geographies by which to subset are stored
# NB: this does NOT control where map data is imported to. See above for why.
schema			= 'ccrp'					# -s or --schema

# how far beyond the specified boundaries to go (in metres)
buffer_radius	=	0							# -b or --buffer_radius

# tables and fields in which geographies are stored
regions_table	=	'ccrp_regions'							# -rt or --regions_table
region_field	= 'name'											# -rf or --region_field

countries_table	= 'ccrp_countries'					# -ct or --countries_table
country_field		= 'name'										# -cf or --country_field

provinces_table					=	'ccrp_provinces'	# -pt or --provinces_table
province_field					=	'name_1'					# -pf pr --province_field
province_country_field	= 'name_0'					# -pcf or --province_country_field

# default output format
# currently implemented options: 'shp' and 'sqlite'
output_format	= 'sqlite'				# -f or --output_format
