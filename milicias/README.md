# Militia Data


This directory contains a csv file (`milicias-merged-cleaned.csv`) listing members of the [Bolivarian Militias][milicias-home], as of May 2013. The 'Fecha' column contains the date of the source document that the data was obtained from.

The data was obtained through the following steps:

1. Finding documents listing rank promotions ("ascensos") on the Militia's [site][milicias-home], such as [these][promo-example]. These documents (pdfs) are dated and are sometimes region-specific; the dates and region of the data is included in the final csv. All the documents found and processed are listed later on this README.
2. Transcribing the names and cedulas in the promotion documents (either by hand or through Mechanical Turk).
3. Verifying that the transcribed names and cedulas match the CNE registry, and filtering out those names that do not match. The `milicias-merged-raw.csv` file contains the raw transcribed data. The final `milicias-merged-cleaned.csv` file contains the same data with the non-matching rows excluded. The `filter_names.py` script generated the `cleaned` csv from the `raw` one. In order to work, the script requires access to a local MySQL database with name and cedulas. The name matching is fuzzy, using edit distances and trying permutations of the name to determine whether there is a match.


## List of documents found/processed

I have copies of all these documents, in case the government decides to pull them off the Milicia's website. I can make them available upon request. The dates are the dates printed on the documents themselves.

Processed:
* September 7, 2011 (1 doc)
* September 20, 2011 (6 docs, by region)
* September 28, 2011 (1 doc)
* September 29, 2011 (2 docs)
* December 8, 2011 (2 docs)
* December 16, 2011 (1 doc)
* December 27, 2011 (1 doc)
* March 27, 2012 (2 docs)
* June 26, 2012 (3 docs)
* June 28, 2012 (8 docs)
* August 6, 2012 (6 docs, by region)
* August 27, 2012 (3 docs)

Found and copied, but not yet processed:
* April 13, 2013 (1 doc, 630 names)

Last check done on: May 19, 2013. Easiest way to check again is to do a Google search with `site:` and `filetype:` (pdf) restrictions, as well as a date restriction (see "Search Tools").


[milicias-home]: http://www.milicia.mil.ve/sitio/web/
[promo-example]: http://www.milicia.mil.ve/sitio/web/index.php?option=com_content&view=article&id=152&Itemid=199

