# Seed Data

`first_names.txt` and `last_names.txt` are derived from the
[U.S. Census Bureau 1990 census name files](https://www.census.gov/topics/population/genealogy/data/1990_census/1990_census_namefiles.html):

- `first_names.txt` — union of `dist.male.first` and `dist.female.first`,
  capitalised, deduplicated, sorted (5,163 names).
- `last_names.txt` — top 5,000 entries of `dist.all.last` by frequency,
  capitalised, deduplicated, sorted.

**License**: U.S. Federal Government works are in the public domain, no
attribution required.

The seed script combines these to produce realistic-looking full names
without shipping any individual's personally identifiable information —
the source files contain only frequency tabulations of first and last
names, never combinations.
