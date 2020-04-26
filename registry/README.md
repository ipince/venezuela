# Registro Electoral (RE) data

I have data dumps of the Registro Electoral, taken at different points in time. Most of the dumps were provided directly by the CNE (Consejo Nacional Electoral). One of them was scraped from their website and is complete and richer in the data that it contains.

Here are the datasets and descriptions:

### 2006 Snapshot
This data set is hosted on Google Drive (~150MB). Ask me for access. The dataset was provided by the CNE ([here](http://www.cne.gov.ve/int_generacion_re/html/index.html)), and represents a snapshot of the registry as of 2006. It was downloaded in February 2013. It contains 1 voting center file and 23 per-state zip files:
* `centros.csv` (9,399 records): voting centers, including center code, state, county, parish, name, address.
* `RE-CSV-<num>.csv`: each of these files contains the registered voters for one state. It includes ID number, nationality, full name, date of birth, and voting center. There are few missing states, including Monagas, Nva Esparta, Portuguesa, Sucre, Tachira, Trujillo, Vargas, Yaracuy, and Zulia.

### 2008 Snapshot
This data set is hosted on Google Drive (~150MB). Ask me for access. The dataset was provided by the CNE ([here](http://www.cne.gov.ve/int_generacion_re/agosto2008/)), and represents a snapshot of the registry as of 2008. It was downloaded in February 2013. It contains 24 per-state zip files:
* `RE-CSV-<num>.csv`: each of these files contains the registered voters for one state. It includes ID number, nationality, full name, date of birth, and voting center.

### April 2012 Snapshot
This data set is hosted on Google Drive (~250MB). Ask me for access. The dataset was provided by the CNE ([here](http://www.cne.gov.ve/web/registro_electoral_descarga/abril2012/nacional.php)), and represents a snapshot of the registry as of April 2012. It was downloaded in February 2013. It contains two zip files: `centros.csv` and `nacional.csv`.
* `centros.csv` (15,298 records): voting centers, including center code, "new" center code, type, state, county, parish, name, address.
* `nacional.csv` (18,903,143 records): registered voters, including ID number, nationality, name (split into first name, middle name, first surname, second surname), voting center.

### Dec 2012 Snapshot
This data set is not currently easily accessible. It includes all 27 million Venezuelans that had ID cards at the time it was taken, in December 2012. It includes more data than the previous ones as well, sometimes including address and/or date of death.

---

* According to [this](http://venezuela.politicaenelmundo.com/averiguar-registro-electoral-para-elecciones-en-venezuela/),
the CNE put out a RE dump corresponding to May 2010
[here](http://www.cne.gov.ve/web/registro_electoral/mayo_2010/index.html), but I wasn't able to download it (as of Feb 2013).

---

Developer Notes:

lxml's etree parsing was not able to extract the data appropriately, which is why we're using an HTMLParser instead.
