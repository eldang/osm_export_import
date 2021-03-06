# Making sense of OpenStreetMap layers and tags

NB: This is based only on analysis of extracts imported from Geofabrik. As far as I know the tags are identical to planet.osm's, but I haven't checked. I think the layer structure is actually defined by osm2pgsql rather than the data source.

I'm starting out by looking at an area including part of Nairobi and rural territory to the East of it - https://www.openstreetmap.org/#map=12/-1.3126/36.9439 - and comparing that map with the data I've imported from Geofabrik's OSM extracts and other data they had prepackaged as Shapefiles.

## Useful links:

* Geofabrik's relatively sparse [Data Extracts - Technical Details](http://download.geofabrik.de/technical.html)
* [https://wiki.openstreetmap.org/wiki/Map_Features](https://wiki.openstreetmap.org/wiki/Map_Features)
* Mapzen's [So You Want To Use A Metro Extract](https://mapzen.com/blog/metro-extracts-101)
* Michal Migurski's [openstreetmap in postgres](http://mike.teczno.com/notes/osm-and-postgres.html)

### OSM styles

I'm pretty sure that the way to start is by figuring out the tag sets used in existing OSM styles, so to that end here are some resources I'm finding:

* [MapCSS Examples](https://wiki.openstreetmap.org/wiki/MapCSS/Examples)
* [PGMapCSS](https://github.com/plepe/pgmapcss) - adapter to process osm2pgsql generated databases with MapCSS. It's all written in Python, so I may well be able to use their parser.
* [PGMapCSS interactive demo](http://pgmapcss.openstreetbrowser.org/?style=585f5) - lets you try out PGMapCSS selectors and see what they alter.
* [JOSM Map Styles](https://josm.openstreetmap.de/wiki/Styles) - note the many highly specialised styles in this set.
* [osm2pgsql's default.style](https://github.com/openstreetmap/osm2pgsql/blob/master/default.style) - I believe this enumerates all the tags that osm2pgsql doesn't ignore.  Doesn't say much about meanings or tag values, though.


## Data structure

The Geofabrik -> osm2pgsql workflow gives us 4 tables that we care about, and 3 temp tables (nodes, rels & ways) that I will ignore. The interesting tables are divided by data type: polygons, lines, roads and points.

**Very important**: a given *feature* type is not necessarily entirely described by any one of these *data* types.  For example, roads are intuitively lines, but they sometimes show up in the polygons table because they are wide enough to be drawn as an area, and meanwhile the roads table only includes relatively major roads.  Or administrative boundaries are polygons if they're entirely contained within the extract we're using, but lines if the polygon can't be closed.

### Polygons

Polygons, confusingly, encapsulates buildings, businesses, region names, and administrative boundaries.  For instance, a polygon for a building may be contained within a polygon for a housing estate, within a polygon for the region, within a polygon for the country.  I think for any practical use we would want to split these types of polygon up.

### Lines

Lines feels like a somewhat more natural category than polygons, because although they can represent many things they don't contain each other.  The main types that seem relevant are barriers, boundaries, transport links (roads, public transit and railways), and waterways (streams and canals).

### Roads

I think the Roads table is a bit of a distraction. I was hoping it would just be the subset of Lines and Polygons that were tagged with `highway`, but (a) it seems to only include relatively major roads and yet (b) at the same time it includes the occasional non-road line like a light rail route.

Its geometry type is LineString, which is the same as the lines table, so I also don't think it does anything useful like aggregate across the other 3 tables.

### Points

Points encompasses anything that can be stored as a single point - amenities, the centres of cities, towns & villages, roundabouts, etc. It's a wide array of things, but the tagging is easier to follow than for polygons and lines (see below).

## Tags

For the most part I think it makes sense to filter by the presence of a tag, not its contents.  However, even a presence filter has to either filter out or treat differently values of `tag=no`, because `bicycle=no` clearly does not mean the same thing as `bicycle=yes` (for example)! We should also always include the actual tag content in exports, because it will often be useful for map styling or detail popups.

### Polygons and Lines

Here is the full selection of tags available for polygons and lines:

```
admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
bridge, boundary, building, construction, covered, culvert, 
cutting, denomination, disused, embankment, foot, "generator:source", 
harbour, highway, historic, horse, intermittent, junction, landuse, 
leisure, lock, man_made, military, motorcar, "natural", 
office, oneway, place, power, power_source, 
public_transport, railway, ref, religion, route, service, shop, 
sport, surface, toll, tourism, "tower:type", tracktype, tunnel, 
water, waterway, wetland, wood
```

There are also address (3 fields all starting with `addr:`, `operator`, `brand` and `name` fields, which are free text, and `population` and `width` which are sort-of numeric (sort-of because they can still contain text, so they'll need to be cleaned up to use).

Here are the tags which seem worth filtering within, and values that seem relevant to CCRP:

* **access**: describes assorted access restrictions: [list of usual values](https://wiki.openstreetmap.org/wiki/Key:access#Values).
* **boundary**:  `administrative` (filtered by a minimum [admin_level=](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative#admin_level)), `protected_area` and `national_park` (probably combined).
* **landuse**: this one's very messy! But it includes tags for things like farmland, grazing, forestry etc: https://wiki.openstreetmap.org/wiki/Landuse
* **man_made**: includes `water_tower`, `water_well`, `silo`: https://wiki.openstreetmap.org/wiki/Key:man_made
* **natural**: values of interest include `water` (i.e. lakes, ponds etc), `wetland`, `spring`, `wood`, `bare_rock`, `scree` and `sand`: https://wiki.openstreetmap.org/wiki/Places
* **place**: describes various *types* of settlement, and a hierarchy of place subdivisions: https://wiki.openstreetmap.org/wiki/Places
* **route**: see https://wiki.openstreetmap.org/wiki/Relation:route#Route_relations_in_use
* **surface**: describes surface types. It's more relevant to roads, but presence/absence is meaningless for this one without filtering further: https://wiki.openstreetmap.org/wiki/Key:surface
* **water** and **waterway**: we may well want to distinguish between natural waterways and canals, and to separate out those waterways also tagged with `intermittent` from the rest.

Note that several other fields also have a long list of values; they're just not things I think we'll want to filter on.

### Points

The point tags are a similar, but not quite identical list to those for lines and polygons:

```
admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
bridge, boundary, building, capital, construction, covered, 
culvert, cutting, denomination, disused, embankment, foot, 
"generator:source", harbour, highway, historic, horse, intermittent, 
junction, landuse, leisure, lock, man_made, military, 
motorcar, "natural", office, oneway, place, poi, 
power, power_source, public_transport, railway, 
religion, route, service, shop, sport, surface, toll, tourism, 
"tower:type", tunnel, water, waterway, wetland, wood
```

There are also the same free text and sort-of-numeric fields as for polygons and lines, plus `ele` which is numeric and seems to correspond to elevation in metres.

I think the same list of tags to filter by value rather than mere presence applies as for polygons and lines.

### Roads

The tagging of roads is rather complicated, but also logical.  The `highway` tag has a hierarchical set of [normal values](https://wiki.openstreetmap.org/wiki/Highways), and then the lowest level there, `highway=track`, is further broken down by the `tracktype` tag, which has [these values](https://wiki.openstreetmap.org/wiki/Key:tracktype).  I think it will be useful to be able to filter by a few different levels on that hierarchy.

Roads can also be modified by other tags, such as `bicycle=no`, `oneway=yes`, `surface`, `width` or `access`. I don't think we need to filter by these, but we should include them in any export of roads.

## Correspondence to Geofabrik's pre-packaged shapefiles

A shapefile download from Geofabrik is broken down logically rather than by geometry type. Here's what they seem to correspond to in the raw OSM data:

### Buildings

This one corresponds almost exactly to OSM polygons filtered by the presence of the `building` tag. I'm finding a handful of Nairobi buildings in my OSM export that aren't in the prepackaged buildings layer - I suspect this is just because the shapefiles we're using are older.

### Landuse

This is a subset of OSM polygons, but a superset of polygons tagged with `landuse`. The Nairobi National Park boundary, for example, is not tagged with `landuse` but is included in the prepackaged Landuse layer. `landuse=forest` seems to be entirely missing from the prepackaged Landuse layer

### Natural

I'm pretty perplexed by this one!  It seems to include `landuse=forest` (which the OSM Wiki explicitly marks as for managed forests and plantations), and some segments of lines tagged with `waterway`, but nothing like complete waterways.  I would be highly reluctant to rely on this set, because it's unclear why things are left out....

### Places

This one seems to correspond exactly to OSM points tagged with `place`.

### Points

This one seems to be all points that are *not* in the Places set. I can't be 100% sure because I do see other points in the OSM import that aren't in the prepackaged layer, but the proportion of those seems consistent with them simply having been added recently.

### Railways

This corresponds perfectly to all the lines in the raw OSM import tagged as `highway`.

### Roads

This seems to be all the lines tagged as `highway`. As above, there are some in the OSM import that aren't in the prepackaged shapefile, but it's few enough that I think that just reflects the Geofabrik set being more recent.



