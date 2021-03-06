# Automating OpenStreetMap imports

## Overview

This is for a specific project, which requires rural data and biases my interest towards three regions of sub-Saharan Africa and one in South America.  I am trying to keep it general enough to be more broadly useful, though.

I tried to find out about as many existing tools and data sources as I could in March 2015: the outcome of that is below.

Based on this, I've settled on a simple script to use osm2pgsql for importing and do the following management:

1. Read in a config file with the database parameters and list of region names to fetch from Geofabrik
2. Check if we already have that region in our database, and if not then fetch the full dataset
3. If we do have it, check what the most recently applied changeset was
4. Go through every changeset since that one, downloading, unzipping and applying it
5. Store a reference to the most recently applied changeset, either in a text file in the working directory or a metadata table in the database.





## Background

This was a snapshot of the OSM export/import tools I could find in March 2015. See [README.md](README.md) for the background and what this was used for.



## Exporting from OSM

### Recommendations

* Whenever Geofabrik’s extracts match areas we want, we should ingest those.  They’re updated every 24 hours, save a lot of work, and they publish changelists so we can probably avoid reimporting whole countries every time.  I think this covers at least half of the countries we’re interested in.

* For countries they don’t cover (or if we want smaller geographies than whole countries), we have a few options.  None is perfect, but it’s a question of different trade-offs.  I think these three are the best:

1) We ingest whole continents from Geofabrik, and then use the daily changelists to avoid having to repeat all that work after setup.
Pro: should be relatively straightforward; isn’t huge amounts of data after initial setup.
Con: Africa and South America are about ¾ GB each, so it’s a lot of storage.  Setup may also be a monster of a job.

2) We use WeoGeo Market to ingest custom areas.
Pro: relatively easy to work with; no rate or size limits.
Con: updates are relatively infrequent.  Although it says “monthly”, their OSM data was last updated in late January, and their job scheduler seems slow enough that getting all the areas we need may take a few days after each update.

3) We use the Overpass API to ingest custom areas.
Pro: data is either live or updated frequently.
Con: looks less easy to work with than WeoGeo, and has a daily quota - I think if we don’t need each country updated more than weekly we can stay within that quota easily, though.

**I am implementing option 1 above, because in our system storage space is not a major concern.**  On the server we're using for testing, initial import of Africa or South America takes 3-4 hours, and incorporating one daily changelist 15-20 minutes.

### Existing data repositories

#### Geofabrik

[Geofabrik hosts extracts](http://download.geofabrik.de/) 

* Updated every 24 hours
* `.osm.pbf` & `.osm.bz2` available for each continent and many countries
* `.shp.zip` available for a smaller subset of countries
* `.poly` files describing the extent of every region for which there are `.osm/*` extracts
* `.osc.gz` files containing daily change lists for every region for which there are `.osm.*` extracts, with which it should be possible to do updates as changes only.
* We may need to download entire continents because not all countries we want have country-level extracts.  Africa is 785MB, South America is 645MB, and I don't yet know if it's practical to download the continent and then import a subset.
* One day's changes for the whole of Africa are typically < 4MB, so having to import entire continents may not be such a problem if we can subsequently consume updates only.

#### Metro Extracts

[Mapzen hosts and maintains Michal Migurski's Metro Extracts](https://mapzen.com/metro-extracts/)

Similar to Geofabrik, but focussed on urban areas, so probably not relevant to CCRP.  One big advantage: it doesn't artificially break at country/region boundaries when metro areas spill over those.



### Existing custom extract sources

#### HOT Exports

[The Humanitarian OpenStreetMap Team's export service](http://export.hotosm.org/en)

* Covers everywhere HOT operates, which includes all of Africa and South America
* Easy to draw custom rectangular bounding boxes for new extracts
* Allows downloading as `.pbf`,  Shapefiles, SQLite or KMZ
* Doesn't have its own job scheduler, but I can probably automate that by faking a click on the "Start new run" button.
* Not instant - creating a job puts it in a queue.  My quick test using Jamaica took about 10 minutes to run
* They ask users to be mindful of shared resources, so wouldn't appreciate frequent re-running of batch jobs
* I think the data is updated live; not certain though

#### BBBike

[Wolfram Schneider's BBBike](http://extract.bbbike.org/)

* Similar to HOT Exports, with a few key differences
* Can draw polygonal bounding boxes
* Has an easily tinkered-with REST API, so automation would be straightforward
* Underlying data updated weekly
* There's a pro version available with nightly data updates, more metadata, and presumably faster responses / no/higher rate limits, but the pricing is not listed
* Doesn't seem to do SQLite or KMZ exports.  Does have the formats we're more likely to use, though.

#### Overpass API

[Overpass API (or OSM3S)](http://wiki.openstreetmap.org/wiki/Overpass_API)

* XML-based API that looks highly customisable
* Accesses a few mirrors, with soft quotas of 5GB/day
* Good idea if we're downloading either small areas or a relatively small subset of tags/fields
* Will hit speed and rate limits if we try to download everything for every country we're interested in
* Might be good for filling in the gaps from Geofabrik's country extracts - I *think* that countries they don't have extracts for are typically the ones for which there's less data in the first place
* Two [Python wrappers](http://wiki.openstreetmap.org/wiki/Overpass_API#Python_API) are available
* Update frequency noted as "Permanent updates" on the OSM wiki.  I *think* this means it's live data.

There's also [XAPI](http://wiki.openstreetmap.org/wiki/XAPI) which looks simpler but less customisable, and has a 10M element (< 1/3 of California) or 100 square degree request size limit.

#### WeoGeo Market

[WeoGeo Market hosts a special OSM Planet mirror](http://market.weogeo.com/datasets/osm-openstreetmap-planet)

* All OSM data is free to download
* Not instant - puts jobs in a queue.  Jamaica took about 1 minute; a combined area covering Kenya, Tanzania, Uganda, Rwanda and a little overlap into neighbouring countries took 50 minutes.
* Can specify polygons by drawing on a map, uploading a KML file (via the UI), or supplying GeoJSON via the API
* Claims to update monthly, but at the time of writing the latest update date is ~7 weeks ago
* UI allows downloading as Shapefiles, GeoJSON, CSV, GBD or FFFS
* API allows downloading as JSON, XML, WEO (looks like an XML schema), KML, PDF or CSV
* There's a [Python wrapper for the API](http://www.weogeo.com/developer_doc/WeoGeo_API_Wrappers_Python.html) which looks well documented and easy to work with






### Existing tools to roll our own extracts

*We probably don't want to go this route, because it's computationally expensive, but I want to keep track of all options for reference.*

#### Planet.osm mirror

In case we do end up rolling our own, it's useful to note that there is [one planet.openstreetmap.org mirror](http://ftp5.gwdg.de/pub/misc/openstreetmap/planet.openstreetmap.org/) which publishes changelists, so we might be able to avoid rebuilding from scratch each time.

#### Extractotron

[Michal Migurski's Extractotron](https://github.com/migurski/Extractotron/)

* Python and shell scripts to generate OSM extracts
* Spins up an AWS instance to do the real work
* Has instructions for customising the list of extracted regions

#### Metroextractor

[Mapzen's Metroextractor Chef Cookbook](https://github.com/mapzen/chef-metroextractor)

* Chef / Vagrant cookbook
* I think it's functionally equivalent to Extractotron





## Parsing OSM files and importing to PostGIS

#### GDAL OSM drivers

[OSM - OpenStreetMap XML and PBF](http://www.gdal.org/drv_osm.html)

* Driver for `ogr2ogr`
* Can parse `.osm` and `.pbf` files
* Can output whatever `ogr2ogr` can output, which includes Shapefiles and PostgreSQL


#### osm2pgsql

[osm2pgsql](https://github.com/openstreetmap/osm2pgsql)

* Command line tool to import OSM data to PostgreSQL databases
* Can parse `.pbf` files and `.osc` changelists
* Looks like this will do everything we need, actually


