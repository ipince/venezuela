# Registro Electoral (RE) data

RE data is taken directly from the CNE, either from dumps provided by the CNE itself, or through a scraper.
The extracted data is too large to host on GitHub, so it is hosted on Google Drive. Ask me for access.

The availalable data is the following:

* RE, as of January 2006, by state, including voting centers. Provided by the CNE
[here](http://www.cne.gov.ve/int_generacion_re/html/index.html). Some states are missing though (404'd when trying
to download). These are Monagas, Nva Esparta, Portuguesa, Sucre, Tachira, Trujillo, Vargas, Yaracuy, and Zulia.
Data was downloaded on February 2013.

* RE, as of August 2008, by state, including voting centers. Provided by the CNE
[here](http://www.cne.gov.ve/int_generacion_re/agosto2008/). All states and centers were downloaded on February 2013.

* According to [this](http://venezuela.politicaenelmundo.com/averiguar-registro-electoral-para-elecciones-en-venezuela/),
the CNE put out a RE dump corresponding to May 2010
[here](http://www.cne.gov.ve/web/registro_electoral/mayo_2010/index.html), but I wasn't able to download it (as of Feb 2013).

* RE, as of April 2012, on national level, and including voting centers. Provided by the CNE
[here](http://www.cne.gov.ve/web/registro_electoral_descarga/abril2012/nacional.php). Downloaded on February 2013.

* Full *cedulado* registy, including people are are not registered to vote. Scraped from November to December 2012.
Includes all 27 million Venezuelans with ID cards. Ask me for details.


Developer Notes:

lxml's etree parsing was not able to extract the data appropriately, which is why we're using an HTMLParser instead.
