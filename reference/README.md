# Reference info

Contents:

1. [A .sql file](./command_reference.sql) that I'm just using as a scratchpad, to store SQL commands as I figure out how to accomplish various tasks.
2. [A python script](list_tags.py) to query the database and get all unique tag values out, with certain exceptions: there's a settable threshold for how often the value must occur, and the following tags are ignored because their values are not categories: `'osm_id', 'layer', 'name', 'population', 'ref', 'width'`.  Note that it's not particularly good quality code - this is something I just made quickly to figure some things out.
3. The output from `list_tags.py` as a series of CSV files. The number in each filename is the threshold, so line_tags_100.csv contains all line tag values that occurred at least 100 times in our database (Africa + South America), point_tags_1.csv contains all point tag values that occurred at all (threshold 1), and so on.