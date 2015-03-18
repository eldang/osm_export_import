# Automating OpenStreetMap imports

## Overview

This is a project to find or build a toolchain for automatically getting OpenStreetMap extracts at specified geographical granularities (usually country level) into PostGIS databases.  There may be a second part for easy exporting in a choice of formats and at the sub-country level.

I hope to find existing tools for this, but am prepared to write whatever parts of the chain I can't find existing work for.



## Exporting from OSM

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
* Not instant - puts jobs in a queue.  Jamaica took about 1 minute; a combined area covering Kenya, Tanzania, Uganda, Rwanda and a little overlap into neighbouring countries is taking longer (20 mins so far, and not finished).
* Can specify polygons by drawing on a map, uploading a KML file (via the UI), or supplying GeoJSON via the API
* Claims to update monthly, but at the time of writing the latest update date is ~7 weeks ago
* UI allows downloading as Shapefiles, GeoJSON, CSV, GBD or FFFS
* API allows downloading as JSON, XML, WEO (proprietary format?), KML, PDF or CSV
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




## Links that I haven't looked at yet

http://wiki.openstreetmap.org/wiki/XAPI
