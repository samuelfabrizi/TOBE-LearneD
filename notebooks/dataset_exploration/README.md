# DEDDIAG, a domestic electricity demand dataset of individual appliances in Germany
The dataset contains recordings of 15 homes over a period of up to 3.5 years, wherein total 50 appliances have been recorded at a frequency of 1 Hz. Recorded appliances are of significance for load-shifting purposes such as dishwashers, washing machines and refrigerators. One home also includes three-phase mains readings that can be used for disaggregation tasks. Additionally, DEDDIAG contains manual ground truth event annotations for 14 appliances, that provide precise start and stop timestamp.

The system used to collect the dataset can be found on [deddiag.github.io](https://deddiag.github.io/)

## Dataset Structure
```
/
|- house_00/
   |- house.tsv.................................HOUSE DESCRIPTION
   |- items.tsv.................................APPLIANCE DESCRIPTIONS
   |- item_0001_data.tsv.gz.....................POWER MEASUREMENTS
   |- item_0001_annotations.tsv.................ANNOTATIONS
   |- item_0001_annotation_labels.tsv...........ANNOTATION LABELS
   |- item_XXXX_data.tsv.gz
   |- item_XXXX_annotations.tsv
   |- item_XXXX_annotation_labels.tsv
|- house_XX/
   |- ...
|- import.sh....................................IMPORT SCRIPT
|- create_tables_0.sql..........................DATABASE TABLES
|- create_tables_1.sql..........................DATABASE INDICES AND FUNCTIONS
|- README.md....................................DATASET DESCRIPTION
```


## Create database
Data can be imported to a postgres database. 
The provided import script assumes importing the data into a docker container.
Help on how to use docker can be found [here](https://docs.docker.com/get-started/overview/).

Create PostgreSQL container: 
```
docker run -d --name deddiagdb -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=password postgres
```

Additionally the postgres instance may be optimized by increasing buffer sizes.
The following values are only suggestions and need to be adjusted depending on available system memory. 
Be aware that `work_mem` is the maximum amount of memory to be used by a query operation which can very quickly add up.
If your system has a large amount of memory, e.g. `>256GB`, you may use a higher limit such as `10GB`.
please consult the [postgres manual](https://www.postgresql.org/docs/current/runtime-config-resource.html) for more information.
 
```
echo "alter system set shared_buffers='256MB';" | docker exec deddiagdb psql -U postgres
echo  "alter system set work_mem='1GB';" | docker exec deddiagdb psql -U postgres
```

## Import data to docker instance
Each house is packaged into a separate ZIP-Archive, the import script will import all unzipped archives:  ```house_00/, house_01/, ...```.

Run the `import.sh` script

**Important:** The uncompressed measurements are very large and require > 139GB of disc space. The import will take several hours.   

```
./import.sh
```

## Data description
The data set contains power measurements from homes in Germany.
Measurements are recorded in a 'lazy' manor, meaning only value changes are stored.

| House | Item id | Name | Category | First Measurement | Last Measurement | Duration | 
| --- | --- | --- | --- | --- | --- | --- |
| 0 |  10 | Refrigerator | Refrigerator | 2016-11-30 | 2019-06-02 | 913 days |
| --- | | | | | | |
| 1 |  1 | Refrigerator | Refrigerator | 2016-10-06 | 2017-04-11 | 186 days |
| 1 |  2 | Washing Machine | Washing Machine | 2017-02-18 | 2017-04-11 | 51 days |
| 1 |  4 | Bosch | Dish Washer | 2016-10-06 | 2017-04-11 | 186 days |
| --- | | | | | | |
| 2 |  11 | Freezer | Freezer | 2016-12-08 | 2020-08-21 | 1351 days |
| 2 |  12 | Washing Machine | Washing Machine | 2016-12-08 | 2018-12-14 | 735 days |
| --- | | | | | | |
| 3 |  13 | Miele F 12020 S-3 | Freezer | 2017-01-07 | 2018-05-27 | 504 days |
| 3 |  14 | Bosch Maxx 6 ecoSpar | Washing Machine | 2016-12-20 | 2019-07-13 | 935 days |
| 3 |  16 | Miele K14827 SD ED/CS | Refrigerator | 2017-01-07 | 2019-07-13 | 917 days |
| --- | | | | | | |
| 4 |  17 | Liebherr KTS14* | Refrigerator | 2017-04-17 | 2020-11-16 | 1308 days |
| 4 |  18 | AEG arctis | Freezer | 2017-04-17 | 2020-12-09 | 1331 days |
| 4 |  19 | Bosch | Dish Washer | 2017-04-17 | 2020-12-09 | 1331 days |
| 4 |  20 | AEG Lavamat Exclusive 54569 Electronic | Washing Machine | 2017-04-17 | 2020-12-09 | 1331 days |
| --- | | | | | | |
| 5 |  5 | Bosch SMS69N48EU | Dish Washer | 2016-08-10 | 2019-01-18 | 890 days |
| 5 |  6 | Miele SOFTTRONIC W2241 | Washing Machine | 2016-08-16 | 2019-01-17 | 884 days |
| 5 |  8 | Office Desk | Office Desk | 2016-12-06 | 2019-01-18 | 772 days |
| 5 |  9 | Bauknecht | Refrigerator | 2016-08-10 | 2019-01-18 | 890 days |
| 5 |  30 | Bezzera BZ09 | Coffee Machine | 2017-06-28 | 2019-01-18 | 568 days |
| --- | | | | | | |
| 6 |  31 | Dish Washer | Dish Washer | 2017-07-22 | 2018-02-02 | 194 days |
| 6 |  32 | Refrigerator | Refrigerator | 2017-07-22 | 2018-02-02 | 194 days |
| 6 |  33 | Miele Novotronic W1514 | Washing Machine | 2017-07-22 | 2017-08-12 | 21 days |
| 6 |  34 | Miele Novotronic T7644C | Dryer | 2017-07-22 | 2018-02-01 | 194 days |
| 6 |  36 | Siemens Extrakl. Festival Spuler | Dish Washer | 2017-07-26 | 2018-02-02 | 190 days |
| 6 |  37 | Haier HEC MCS662FIX | Refrigerator | 2017-07-26 | 2018-03-05 | 221 days |
| --- | | | | | | |
| 7 |  68 | Miele Hydromatic W701 | Washing Machine | 2017-10-08 | 2020-12-09 | 1157 days |
| 7 |  69 | Whirlpool | Other | 2017-10-08 | 2018-07-20 | 284 days |
| 7 |  70 | Sony KDL-48W605B | TV | 2017-10-08 | 2020-05-04 | 938 days |
| 7 |  71 | Saeco Magic Comfort+ | Coffee Machine | 2017-10-08 | 2020-12-09 | 1157 days |
| --- | | | | | | |
| 8 |  24 | Miele W 5873 WPS Edition 111 | Washing Machine | 2017-06-06 | 2018-07-28 | 416 days |
| 8 |  26 | Dish Washer | Dish Washer | 2017-06-18 | 2018-07-28 | 404 days |
| 8 |  27 | Bezzera Mitica Top MN | Coffee Machine | 2017-06-18 | 2018-07-28 | 404 days |
| 8 |  28 | Office Desk | Office Desk | 2017-06-18 | 2018-07-28 | 404 days |
| 8 |  35 | Refrigerator | Refrigerator | 2017-07-23 | 2018-07-28 | 369 days |
| 8 |  51 | Modbus Smart Meter Phase 1 | Smart Meter Phase | 2017-09-05 | 2018-07-28 | 325 days |
| 8 |  52 | Modbus Smart Meter Phase 2 | Smart Meter Phase | 2017-09-05 | 2018-07-28 | 325 days |
| 8 |  53 | Modbus Smart Meter Phase 3 | Smart Meter Phase | 2017-09-05 | 2018-07-28 | 325 days |
| 8 |  59 | Modbus Smart Meter Total | Smart Meter Total | 2017-09-12 | 2018-07-28 | 318 days |
| --- | | | | | | |
| 9 |  44 | Dish Washer | Dish Washer | 2017-08-05 | 2019-02-03 | 546 days |
| 9 |  45 | Refrigerator | Refrigerator | 2017-08-05 | 2020-03-17 | 954 days |
| 9 |  46 | Washing Machine | Washing Machine | 2017-08-05 | 2020-03-17 | 954 days |
| --- | | | | | | |
| 10 |  65 | Refrigerator | Refrigerator | 2017-09-20 | 2019-11-01 | 771 days |
| 10 |  66 | Dish Washer | Dish Washer | 2017-09-20 | 2019-11-01 | 771 days |
| 10 |  67 | Washing Machine | Washing Machine | 2017-09-20 | 2019-11-01 | 771 days |
| --- | | | | | | |
| 11 |  38 | Dryer | Dryer | 2017-07-27 | 2017-12-15 | 140 days |
| --- | | | | | | |
| 12 |  61 | Washing Machine | Washing Machine | 2017-09-13 | 2018-07-31 | 320 days |
| 12 |  62 | Dish Washer | Dish Washer | 2017-09-13 | 2018-07-31 | 320 days |
| 12 |  63 | Dryer | Dryer | 2017-09-13 | 2018-07-31 | 320 days |
| 12 |  64 | Refrigerator | Refrigerator | 2017-09-13 | 2018-07-31 | 320 days |
| --- | | | | | | |
| 13 |  39 | Washing Machine | Washing Machine | 2017-07-30 | 2018-10-06 | 433 days |
| 13 |  40 | Dish Washer | Dish Washer | 2017-07-30 | 2018-10-06 | 433 days |
| 13 |  41 | Refrigerator | Refrigerator | 2017-07-30 | 2018-10-06 | 433 days |
| --- | | | | | | |
| --- | | | | | | |
| 14 |  81 | Heat Pump | Other | 2017-10-24 | 2019-10-14 | 720 days |
| 14 |  82 | Refrigerator | Refrigerator | 2017-11-10 | 2020-12-09 | 1124 days |
| 14 |  83 | Washing Machine | Washing Machine | 2017-11-12 | 2020-12-09 | 1122 days |
| --- | | | | | | |



## Query Data
Since data is measured in a lazy manor where only changes are recorded, you have to use the get_measurements(item_id, from_time, to_time) function to retrieve gap filled data.
The function returns a value for each second rounded to seconds.

Sample query for item 19
```
SELECT * FROM get_measurements(19,'2017-04-19T06:06:00','2017-04-19T06:07:00');
```

Get houses and demographic data
```
"SELECT id, json_array_elements(persons) FROM houses"
```

## Authors
* [Marc Wenninger](https://orcid.org/0000-0003-2690-9434) - [Rosenheim Technical University of Applied Sciences](https://www.th-rosenheim.de/en/rosenheim-university-of-applied-sciences/faculties-institutes/faculty-of-computer-science/)
* [Andreas Maier](https://orcid.org/0000-0002-9550-5284) - [Friedrich-Alexander-University Erlangen-Nürnberg](https://lme.tf.fau.de/)
* [Jochen Schmidt](https://orcid.org/0000-0001-5645-5520) - [Rosenheim Technical University of Applied Sciences](https://www.th-rosenheim.de/en/rosenheim-university-of-applied-sciences/faculties-institutes/faculty-of-computer-science/)

## Acknowledgments
Major parts of this work were funded by the German Federal Ministry of Education and Research (BMBF), grant [01LY1506](https://foerderportal.bund.de/foekat/jsp/SucheAction.do?actionMode=view&fkz=01LY1506B),and supported by the [Bayerische Wissenschaftsforum](https://energie.baywiss.de/) (BayWISS). 
Furthermore, we thank all participating households for their data donation and all students involved in the system development.


## License
CC BY 4.0 licensed as found in the LICENSE file.
