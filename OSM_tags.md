# Making sense of OpenStreetMap layers and tags

NB: This is based only on analysis of extracts imported from Geofabrik. As far as I know the tags are identical to planet.osm's, but I haven't checked. I think the layer structure is actually defined by osm2pgsql rather than the data source.

I'm starting out by looking at an area including part of Nairobi and rural territory to the East of it - https://www.openstreetmap.org/#map=12/-1.3126/36.9439 - and comparing that map with the data I've imported from Geofabrik and other data imported from WeoGeo.

## Useful links:

* Geofabrik's relatively sparse [Data Extracts - Technical Details](http://download.geofabrik.de/technical.html)
* [https://wiki.openstreetmap.org/wiki/Map_Features](https://wiki.openstreetmap.org/wiki/Map_Features)
* Mapzen's [So You Want To Use A Metro Extract](https://mapzen.com/blog/metro-extracts-101)
* Michal Migurski's [openstreetmap in postgres](http://mike.teczno.com/notes/osm-and-postgres.html)

## Data structure and tags

The Geofabrik -> osm2pgsql workflow gives us 4 tables that we care about, and 3 temp tables (nodes, rels & ways) that I will ignore. The interesting tables are divided by data type: polygons, lines, roads and points.

### Polygons

Polygons, confusingly, encapsulates buildings, businesses, region names, and administrative boundaries.  For instance, a polygon for a building may be contained within a polygon for a housing estate, within a polygon for the region, within a polygon for the country.  I think for any practical use we would want to split these types of polygon up.

Here is the selection of tags available for polygons:

```
admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
brand, bridge, boundary, building, construction, covered, culvert, 
cutting, denomination, disused, embankment, foot, "generator:source", 
harbour, highway, historic, horse, intermittent, junction, landuse, 
leisure, lock, man_made, military, motorcar, "natural", 
office, oneway, operator, place, power, power_source, 
public_transport, railway, ref, religion, route, service, shop, 
sport, surface, toll, tourism, "tower:type", tracktype, tunnel, 
water, waterway, wetland, width, wood
```

There are also address (3 fields all starting with `addr:`, `operator` and `name` fields, which are free text.

For the most part I think it makes sense to filter by the presence of a tag, not its contents.  Here are the few tags which seem worth filtering within, and values that seem relevant to CCRP:

* **access**: describes assorted access restrictions: [list of usual values](https://wiki.openstreetmap.org/wiki/Key:access#Values).
* **boundary**:	`administrative` (filtered by a minimum [admin_level=](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative#admin_level)), `protected_area` and `national_park` (probably combined).
* **place**: describes various *types* of settlement, and a hierarchy of place subdivisions: https://wiki.openstreetmap.org/wiki/Places
* **surface**: describes surface types. It's more relevant to roads, but presence/absence is meaningless for this one without filtering further: https://wiki.openstreetmap.org/wiki/Key:surface

Note that several other fields also have a long list of values; they're just not things I think we'll want to filter on. I do recommend including the tag values in any export, as they often add useful metadata to individual polygons.

### Lines



### Roads




## Unresolved questions:

* What is the `access` field in the polygons table?  I *think* it's about where the data came from in the first place, but I'm very unsure of that.