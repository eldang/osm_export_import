# Automating OpenStreetMap imports

## Overview

This is a project to find or build a toolchain for automatically getting OpenStreetMap extracts at specified geographical granularities (usually country level) into PostGIS databases.  There may be a second part for easy exporting in a choice of formats and at the sub-country level.

This is for a specific project, which requires rural data and biases my interest towards three regions of sub-Saharan Africa and one in South America.  I am trying to keep it general enough to be more broadly useful, though.

I tried to find out about as many existing tools and data sources as I could in March 2015: the outcome of that is in [background.md](background.md)

Based on this, I've settled on a simple script to use osm2pgsql and do the following management:

1) Read in a config file with the database parameters and list of region names to fetch from Geofabrik
2) Check if we already have that region in our database, and if not then fetch the full dataset
3) If we do have it, check what the most recently applied changeset was
4) Go through every changeset since that one, downloading, unzipping and applying it
5) Store a reference to the most recently applied changeset, either in a text file in the working directory or a metadata table in the database.
