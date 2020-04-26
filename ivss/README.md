# IVSS

This is a set of scripts to scrape data from the Venezuelan social security administration
(IVSS, Instituto Venezolano de los Seguro Sociales).

The IVSS has a [website](http://www.ivss.gob.ve:28088/ConstanciaCotizacion/) where people can request a proof
of registration (or "constancia") by entering their national id number (or "cedula"). The constancia includes data
about their work history, including whether they have registered with the IVSS, who their current
employer is, how many work weeks they have accrued, etc. See `example_input.html`
to see what the service returns, and `example_output.csv` to see what these scripts will output.

## Requirements
The scripts run on Python 2.7 and use the `requests` and `lxml` libraries.

## Usage

To process a large batch of ids, first put the input ids in a file were each line contains the nationality
(either 'V' or 'E') and the cedula, separated by whitespace. Example:
```
V 15000000
E 81000000
```

Assuming the input file is large, I recommend splitting the file into smaller files of, say, 5000 records each.
```
$ split -l 5000 -a 1 <filename> <filename>-
```

Scrape each file separately (ideally using different machines). The service takes quite long to respond. If the person
is registered, the request takes 3-4 seconds; if the person is not registered, it takes ~0.5 seconds. In my experience,
when using about 1 second of wait time in between requests (in order to not overload the system), processing 5k records
takes about 6 hours.
```
$ time python ivss_scrape.py -i <batch>
```

The scraper will save the retrieved html in a folder named `<batch>-cache`. Then, you can run the parser to extract
the structured information from the html:
```
$ python ivss_parse.py -b <batch> -d <directory>
```

The parser requires both the input file and the cache directory because the html does not contain the nationality of
the person in question. I wanted to preserve that information in the output file, so that's why the input file is needed.

You should end up with a file like `example_output.csv`!

Please contact me (file an issue) if you have any questions.
