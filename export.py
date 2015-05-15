#! /usr/bin/env python

#  Script to export OpenStreetMap data subsetted by geography and tag set
__author__ = "Eldan Goldenberg for TerraGIS & CoreGIS, April 2015"
#    http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com



# load local config
import config

# load shared helper functions
import helpers


# Python includes
import argparse
import json
import os
import subprocess
import sys
import time
import zipfile



def main():
  # Log starting time of run
  helpers.print_with_timestamp("Starting run.")
  starttime = time.time()

# Parse arguments and get started
  args = get_CLI_arguments()
  export(args)

# And we're done, so report the time
  helpers.print_with_timestamp(
      "Run complete in " + helpers.elapsed_time(starttime) + "."
  )




def export(args):
  os.chdir(args.working_directory)
  if args.category == "province" and args.province_country_name is not None:
    if not os.path.isdir(args.province_country_name):
      os.mkdir(args.province_country_name)
    os.chdir(args.province_country_name)
# Call ogr2ogr to produce the output files
  ogrcmds = assemble_ogr_cmds(args)
  for key, cmd in ogrcmds.items():
    if args.verbose:
      helpers.print_with_timestamp("Exporting " + key + ".")
      subprocess.call(cmd)
    else:  # suppress ogr2ogr's output
      with open(os.devnull, 'w') as FNULL:
        subprocess.call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)
  compress(args)




# Package the output up as a ZIP file, and delete the uncompressed files
def compress(args):
  if args.verbose:
    helpers.print_with_timestamp("Exports complete. Compressing files.")
  zname = args.outfile + "." + args.output_format + ".zip"
  with zipfile.ZipFile(zname, 'w') as zip:
    for fname in os.listdir(os.getcwd()):
      if fname.startswith(args.outfile + "_"):
        if args.verbose:
          helpers.print_with_timestamp(
              "Adding " + fname + " to archive " + zname
          )
        zip.write(fname)
        os.remove(fname)





def assemble_sql(args):
  geomref = assemble_geom_ref(args)

  joincmd, joinfilters = make_join_cmds(args, geomref)

  if args.taglist is not None:
    tagfilters = make_tag_filters(args)
  else:
    tagfilters = {"lines": "", "points": "", "polygons": ""}

  sqlcmds = {"lines": "", "points": "", "polygons": ""}
  first = False
  for prefix in args.prefix:
    # If this is not the first prefix, use UNION to combine:
    if first:
      for key in sqlcmds.keys():
        sqlcmds[key] += " UNION "
    else:
      first = True

    sqlcmds['lines'] += (
        "SELECT d.* FROM public." + prefix + "line AS d" +
        joincmd + joinfilters + tagfilters["lines"]
    )
    sqlcmds['points'] += (
        "SELECT d.* FROM public." + prefix + "point AS d" +
        joincmd + joinfilters + tagfilters["points"]
    )
    sqlcmds['polygons'] += (
        "SELECT d.* FROM public." + prefix + "polygon AS d" + joincmd
    )

# Extra processing to exclude polygons that border the selection area
    sqlcmds['polygons'] += (
        " AND NOT st_touches(st_transform(d.way,4326), " + geomref + ")"
    )
    sqlcmds['polygons'] += joinfilters + tagfilters["polygons"]

  return sqlcmds




# only add a buffer if necessary, because it slows execution down massively
# for some reason region exports need an st_buffer call even if the buffer
# size is 0
def assemble_geom_ref(args):
  if args.buffer_radius in ['0', '0.0'] and args.category != 'region':
    return "g.the_geom"
  else:
    return "st_buffer(g.the_geom," + args.buffer_radius + ")"




def make_join_cmds(args, geomref):
  joincmd = " INNER JOIN " + args.schema + "."

  if args.category == 'region':
    joincmd += args.regions_table
    joinfilters = (
        " AND g." + args.region_field + " ilike '" + args.subset + "'"
    )
  elif args.category == 'country':
    joincmd += args.countries_table
    joinfilters = (
        " AND g." + args.country_field + " ilike '" + args.subset + "'"
    )
  elif args.category == 'province':
    joincmd += args.provinces_table
    joinfilters = (
        " AND g." + args.province_field + " ilike '" + args.subset + "'"
    )
    if args.province_country_name is not None:
      joinfilters = (
          " AND g." + args.province_country_field +
          " ilike '" + args.province_country_name + "'" +
          joinfilters
      )
  else:
    helpers.print_with_timestamp(
        "Category not recognised. Must be one of region, country or province."
    )
    exit(1)

  joincmd += (
      " as g ON st_intersects(st_transform(d.way,4326), " + geomref + ")"
  )
  return joincmd, joinfilters



def make_tag_filters(args):
  with open(args.taglist, 'r') as infile:
    taglist = json.load(infile)
    if args.verbose and 'comment' in taglist:
      helpers.print_with_timestamp(
          "Loaded tag set with comment '" + taglist['comment'] + "'."
      )

    tagfilters = {"lines": "", "points": "", "polygons": ""}

    if "includeByPresence" in taglist:
      tagfilters = filter_by_presence(
          taglist["includeByPresence"],
          tagfilters,
          exclude=False
      )
    if "includeByValue" in taglist:
      tagfilters = filter_by_value(
          taglist["includeByValue"],
          tagfilters,
          exclude=False
      )
    if "excludeByPresence" in taglist:
      tagfilters = filter_by_presence(
          taglist["excludeByPresence"],
          tagfilters,
          exclude=True
      )
    if "excludeByValue" in taglist:
      tagfilters = filter_by_value(
          taglist["excludeByValue"],
          tagfilters,
          exclude=True
      )

  for datatype in {"points", "lines", "polygons"}:
    if tagfilters[datatype] != "":
      tagfilters[datatype] = "AND (" + tagfilters[datatype] + ") "
  return tagfilters




def filter_by_presence(taglist, tagfilters, exclude):
  for datatype in {"points", "lines", "polygons"}:
    empty = True
    for tag in taglist:
      if tag in config.available_tags[datatype]:
        if empty:
          empty = False
          tagfilters[datatype] = start_block(tagfilters[datatype], exclude)
        else:
          tagfilters[datatype] += "OR "

        tagfilters[datatype] += tag + " IS NOT NULL "

    if not empty:
      tagfilters[datatype] += ") "

  return tagfilters




def filter_by_value(taglist, tagfilters, exclude):
  for datatype in {"points", "lines", "polygons"}:
    empty = True
    for tag in taglist:
      if tag["tagName"] in config.available_tags[datatype]:
        if empty:
          empty = False
          tagfilters[datatype] = start_block(tagfilters[datatype], exclude)
        else:
          tagfilters[datatype] += "OR "

        firstval = True
        for val in tag["values"]:
          if firstval:
            firstval = False
            tagfilters[datatype] += "("
          else:
            tagfilters[datatype] += "OR "

          tagfilters[datatype] += '"' + tag["tagName"] + '"'
          tagfilters[datatype] += " ILIKE '%" + val + "%' "
        tagfilters[datatype] += ") "

    if not empty:
      tagfilters[datatype] += ") "

  return tagfilters




def start_block(filterblock, exclude):
  if filterblock != "":
    if exclude:
      filterblock += "AND "
    else:
      filterblock += "OR "
  if exclude:
    filterblock += "NOT "
  filterblock += "("

  return filterblock




def assemble_ogr_cmds(args):
  sqlcmds = assemble_sql(args)
  ogrcmds = {}

  for key, sqlcmd in sqlcmds.items():
    ogrcmds[key] = ["ogr2ogr", "-f"]

    if args.output_format == 'shp':
      ogrcmds[key] += ['ESRI Shapefile']
    elif args.output_format in ['spatialite', 'sqlite']:
      ogrcmds[key] += ["SQLite", '-dsco', 'SPATIALITE=yes']
    else:
      helpers.print_with_timestamp(
          "Output format not recognised. \
              Must be one of shp, spatialite or sqlite."
      )
      exit(2)

    ogrcmds[key] += [args.outfile + "_" + key + "." + args.output_format]
    ogrcmds[key] += [
        'PG:host=' + args.host +
        ' user=' + args.user +
        ' port=' + args.port +
        ' dbname=' + args.database
    ]
    ogrcmds[key] += ['-sql', sqlcmd]

  return ogrcmds




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
  parser.add_argument(
      "subset",
      help="required argument: the region we are subsetting to \
      (e.g. 'kenya' or 'rift valley')",
      metavar="'subregion name'"
  )
  parser.add_argument(
      "outfile",
      help="required argument: filename stub to save output to \
      (will have data types & extension added)",
      metavar="filename_with_no_ext"
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

  parser.add_argument(
      "-t", "--taglist",
      help="JSON file specifying tags to include and/or exclude.",
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
