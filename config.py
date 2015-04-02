# Default values for server config and script behaviour.
# Most can be overriden with command line arguments
# Where this is true, the name of the argument is provided as a comment at the end of the line

__name__ = "config"


### server config
host				= "localhost"			# -H or --host
port				= 5433 # 5432 is the postgresql default
database		= "osm_africa"		# -d or --database
user				= "postgres"			# -u or --user
# password has to either be entered manually or stored in .pgpass
# unfortunately, osm2pgsql doesn't seem to have a way to specify schemas, so we'll always be creating tables in the public scheme



# Should we give verbose output and wait for acknowledgement from the user before quitting?
verbose			=	False						# -v or --verbose



# After how many changesets should we do the database cleanup?
clean_interval	= 5						# -c or --clean_interval
