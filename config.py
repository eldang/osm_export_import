# Default values for server config and script behaviour.
# Most can be overriden with command line arguments
# Where this is true, the name of the argument is provided as a comment at the 
# end of the line

__name__ = "config"


# ### shared server config
host        = "localhost"      # -H or --host
port        = 5432             # -p or --port ; 5432 is the postgresql default
database    = "osmextracts"    # -d or --database
user        = "eldan"          # -u or --user
# password has to either be entered manually or stored in .pgpass
# unfortunately, osm2pgsql doesn't seem to have a way to specify schemas, so 
# we'll always be creating tables in the public scheme



# Should we give verbose output and wait for acknowledgement from the user 
# before quitting?
verbose       = False          # -v or --verbose



# ## Import-only:
# After how many changesets should we do the database cleanup?
clean_interval = 5            # -c or --clean_interval




# ## Export-only:
# schema in which the geographies by which to subset are stored
# NB: this does NOT control where map data is imported to. See above for why.
schema      = 'public'         # -s or --schema

# how far beyond the specified boundaries to go (in metres)
buffer_radius  = 0             # -b or --buffer_radius

# tables and fields in which geographies are stored
regions_table           = 'ccrp_regions'    # -rt or --regions_table
region_field            = 'name'            # -rf or --region_field

countries_table         = 'ccrp_countries'  # -ct or --countries_table
country_field           = 'name'            # -cf or --country_field

provinces_table         = 'ccrp_provinces'  # -pt or --provinces_table
province_field          = 'name_1'          # -pf pr --province_field
province_country_field  = 'name_0'          # -pcf or --province_country_field

# default output format
# currently implemented options: 'shp' and 'sqlite'
output_format  = 'sqlite'     # -f or --output_format

# tags available in the different osm2pgsql-generated tables:
available_tags = {
    "lines": [
        "admin_level", "aerialway", "aeroway", "amenity", "area", "barrier", 
        "bicycle", "bridge", "boundary", "building", "construction", "covered", 
        "culvert", "cutting", "denomination", "disused", "embankment", "foot", 
        "generator:source", "harbour", "highway", "historic", "horse", 
        "intermittent", "junction", "landuse", "leisure", "lock", "man_made", 
        "military", "motorcar", "natural", "office", "oneway", "place", 
        "power", "power_source", "public_transport", "railway", "ref", 
        "religion", "route", "service", "shop", "sport", "surface", "toll", 
        "tourism", "tower:type", "tracktype", "tunnel", "water", "waterway", 
        "wetland", "wood"
    ],
    "points": [
        "admin_level", "aerialway", "aeroway", "amenity", "area", "barrier", 
        "bicycle", "bridge", "boundary", "building", "capital", "construction", 
        "covered", "culvert", "cutting", "denomination", "disused", 
        "embankment", "foot", "generator:source", "harbour", "highway", 
        "historic", "horse", "intermittent", "junction", "landuse", "leisure", 
        "lock", "man_made", "military", "motorcar", "natural", "office", 
        "oneway", "place", "poi", "power", "power_source", "public_transport", 
        "railway", "religion", "route", "service", "shop", "sport", "surface", 
        "toll", "tourism", "tower:type", "tunnel", "water", "waterway", 
        "wetland", "wood"
    ]
}

available_tags["polygons"] = available_tags["lines"]
