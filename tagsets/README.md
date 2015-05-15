# Tag sets

This directory is for sample lists of tags to filter exports by.

## Notes

[I'll make this more readable in due course]

JSON contains the following variables:
* comment (string): human-readable note
* includeByPresence (array): include objects with any non-null instance of these tags
* includeByValue (array): include particular values of these tags; see below
* excludeByPresence (array): exclude objects with any non-null instance of these tags
* excludeByValue (array): exclude particular values of these tags; see below

...ByValue: each is an array of objects. The objects in turn consist of: `tagName` and an array of `values` to filter by.

Completions:
* By default, filter tag names by exact matches, but values by LIKE '%value%' to get substrings.
