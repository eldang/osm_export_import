-- Filter a continent by geography (mix & match)

-- lines by country

SELECT lines.* 
	FROM 
		public.africa_line as lines
		INNER JOIN 
			ccrp.ccrp_countries as g 
			ON 
				st_intersects(st_transform(lines.way,4326), g.the_geom)
				AND g.name ilike 'Kenya';

-- points by province
-- need to filter on country and province name in case of province names that exist in more than one country
-- may want to add a buffer to get n km around the province

SELECT points.* 
	FROM 
		public.africa_point as points
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(points.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley';

-- polygons by region
-- the st_buffer(the_geom,0) hack was suggested by http://postgis.17.x6.nabble.com/How-to-trim-a-GeometryCollection-to-get-a-MultiPolygon-td3556351.html
-- it shouldn't break points or lines, but it may be rather slow
-- of course, we can also use it to make sure our selections go a little beyond the boundaries. In that use, the number is a radius in metres (given SRID 4326).

SELECT polygons.* 
	FROM 
		public.africa_polygon as polygons
		INNER JOIN 
			ccrp.ccrp_regions as g 
			ON 
				st_intersects(st_transform(polygons.way,4326), st_buffer(g.the_geom,0))
				AND g.name ilike 'East & Horn of Africa';




-- combining the data types
-- 3 different geometry types, combined into one GEOMETRYCOLLECTION
-- note that we have to add "NULL AS x" to each table's select query, where x is each field that exists in one of the other tables but not this one

SELECT 
	osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", 
 admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
 brand, bridge, boundary, building, capital, construction, covered, 
 culvert, cutting, denomination, disused, ele, embankment, foot, 
 "generator:source", harbour, highway, historic, horse, intermittent, 
 junction, landuse, layer, leisure, lock, man_made, military, 
 motorcar, name, "natural", office, oneway, operator, place, poi, 
 population, power, power_source, public_transport, railway, ref, 
 religion, route, service, shop, sport, surface, toll, tourism, 
 "tower:type",
 NULL AS tracktype,
 tunnel, water, waterway, wetland, width, wood, 
 z_order, 
 NULL AS way_area,
 ST_ForceCollection(way) AS geom
	FROM 
		public.africa_point as points
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(points.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley'
UNION
SELECT 
	osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", 
	admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
	brand, bridge, boundary, building, 
	NULL AS capital,
	construction, covered, culvert, 
	cutting, denomination, disused, 
	NULL AS ele,
	embankment, foot, "generator:source", 
	harbour, highway, historic, horse, intermittent, junction, landuse, 
	layer, leisure, lock, man_made, military, motorcar, name, "natural", 
	office, oneway, operator, place, 
	NULL AS poi, population, power, power_source, 
	public_transport, railway, ref, religion, route, service, shop, 
	sport, surface, toll, tourism, "tower:type", tracktype, tunnel, 
	water, waterway, wetland, width, wood, z_order, way_area,
	ST_ForceCollection(way) AS geom
	FROM 
		public.africa_line as lines
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(lines.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley'
UNION
SELECT 
	osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", 
	admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
	brand, bridge, boundary, building, 
	NULL AS capital,
	construction, covered, culvert, 
	cutting, denomination, disused, 
	NULL AS ele,
	embankment, foot, "generator:source", 
	harbour, highway, historic, horse, intermittent, junction, landuse, 
	layer, leisure, lock, man_made, military, motorcar, name, "natural", 
	office, oneway, operator, place, 
	NULL AS poi, population, power, power_source, 
	public_transport, railway, ref, religion, route, service, shop, 
	sport, surface, toll, tourism, "tower:type", tracktype, tunnel, 
	water, waterway, wetland, width, wood, z_order, way_area,
	ST_ForceCollection(way) AS geom
	FROM 
		public.africa_polygon as polygons
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(polygons.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley';



-- thinning the data

-- remove poi field because it's always blank
-- reduce the following fields to boolean because they only have one value:
	-- TRUE or NULL:
		-- culvert=yes
	-- TRUE, FALSE or NULL		
		-- intermittent= actually a range of values, but they reduce to boolean
		-- lock=yes or lock=no
		-- toll=no or toll= anything else is a yes

SELECT 
	osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", 
	admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
	brand, bridge, boundary, building, capital, construction, covered, 
	CASE WHEN culvert='yes' THEN TRUE ELSE NULL::boolean END AS culvert, 
	cutting, denomination, disused, ele, embankment, foot, 
	"generator:source", harbour, highway, historic, horse, 
	CASE WHEN intermittent='no' THEN FALSE WHEN intermittent=NULL THEN NULL::boolean ELSE TRUE END as intermittent,
	junction, landuse, layer, leisure, 
	CASE WHEN lock='yes' THEN TRUE WHEN lock='no' THEN FALSE ELSE NULL::boolean END AS lock, 
	man_made, military, 
	motorcar, name, "natural", office, oneway, operator, place, 
	population, power, power_source, public_transport, railway, ref, 
	religion, route, service, shop, sport, surface, 
	CASE WHEN toll='no' THEN FALSE WHEN toll=NULL THEN NULL::boolean ELSE TRUE END as toll,
	tourism, 
	"tower:type",
	NULL AS tracktype,
	tunnel, water, waterway, wetland, width, wood, 
	z_order, 
	NULL AS way_area,
	ST_ForceCollection(way) AS geom
	FROM 
		public.africa_point as points
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(points.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley'
UNION
SELECT 
	osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", 
	admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
	brand, bridge, boundary, building, 
	NULL AS capital,
	construction, covered,
	CASE WHEN culvert='yes' THEN TRUE ELSE NULL::boolean END AS culvert, 
	cutting, denomination, disused, 
	NULL AS ele,
	embankment, foot, "generator:source", 
	harbour, highway, historic, horse, 
	CASE WHEN intermittent='no' THEN FALSE WHEN intermittent=NULL THEN NULL::boolean ELSE TRUE END as intermittent,
	junction, landuse, 
	layer, leisure,
	CASE WHEN lock='yes' THEN TRUE WHEN lock='no' THEN FALSE ELSE NULL::boolean END AS lock, 
	man_made, military, motorcar, name, "natural", 
	office, oneway, operator, place, 
	population, power, power_source, 
	public_transport, railway, ref, religion, route, service, shop, 
	sport, surface,
	CASE WHEN toll='no' THEN FALSE WHEN toll=NULL THEN NULL::boolean ELSE TRUE END as toll,
	tourism, "tower:type", tracktype, tunnel, 
	water, waterway, wetland, width, wood, z_order, way_area,
	ST_ForceCollection(way) AS geom
	FROM 
		public.africa_line as lines
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(lines.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley'
UNION
SELECT 
	osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", 
	admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, 
	brand, bridge, boundary, building, 
	NULL AS capital,
	construction, covered,
	CASE WHEN culvert='yes' THEN TRUE ELSE NULL::boolean END AS culvert, 
	cutting, denomination, disused, 
	NULL AS ele,
	embankment, foot, "generator:source", 
	harbour, highway, historic, horse, 
	CASE WHEN intermittent='no' THEN FALSE WHEN intermittent=NULL THEN NULL::boolean ELSE TRUE END as intermittent,
	junction, landuse, 
	layer, leisure,
	CASE WHEN lock='yes' THEN TRUE WHEN lock='no' THEN FALSE ELSE NULL::boolean END AS lock, 
	man_made, military, motorcar, name, "natural", 
	office, oneway, operator, place, 
	population, power, power_source, 
	public_transport, railway, ref, religion, route, service, shop, 
	sport, surface,
	CASE WHEN toll='no' THEN FALSE WHEN toll=NULL THEN NULL::boolean ELSE TRUE END as toll,
	tourism, "tower:type", tracktype, tunnel, 
	water, waterway, wetland, width, wood, z_order, way_area,
	ST_ForceCollection(way) AS geom
	FROM 
		public.africa_polygon as polygons
		INNER JOIN 
			ccrp.ccrp_provinces as g 
			ON 
				st_intersects(st_transform(polygons.way,4326), g.the_geom)
				AND g.name_0 ilike 'Kenya'
				AND g.name_1 ilike 'Rift Valley';