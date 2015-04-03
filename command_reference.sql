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
-- the st_buffer() hack was suggested by http://postgis.17.x6.nabble.com/How-to-trim-a-GeometryCollection-to-get-a-MultiPolygon-td3556351.html

SELECT polygons.* 
	FROM 
		public.africa_polygon as polygons
		INNER JOIN 
			ccrp.ccrp_regions as g 
			ON 
				st_intersects(st_transform(polygons.way,4326), st_buffer(g.the_geom,0))
				AND g.name ilike 'East & Horn of Africa';

