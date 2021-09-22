# pa-api-pulldata-v2.py
Python script using the PurpleAir API to download sensor PM2.5 data. This version pulls PA API ID and read key values from an input CSV file (use the PA_IDs.csv file as a template).

<b>How to find PA API information for data downloader:</b>

<img width="292" src="https://user-images.githubusercontent.com/81830321/113453656-eaf02300-93b2-11eb-8fe8-e9d638801bb1.png">

<b>1.</b> Hover over “Get this widget” after clicking on a PurpleAir sensor on the map. Copy the HTML that pops up to find the sensor ID and API read key in the script tag. Here is an example with a random sensor in Bel Air, CA:

<script src=‘https://www.purpleair.com/pa.widget.js?key=<b>YLV2RFZLX93DRHY3</b>&module=AQI&conversion=C0&average=10&layer=standard&container=PurpleAirWidget_<b>78091</b>_module_AQI_conversion_C0_average_10_layer_standard'></script> <br></br>
- “key=<b>YLV2RFZLX93DRHY3</b>” - PA API read key for the A sensor
- “PurpleAirWidget_<b>78091</b>” - PA ID (this 5 digit ID is not the same as the API IDs for A and B sensors) <br></br>


<b>2.</b> Use this URL format to find the Thingspeak API IDs and read keys needed for PA_IDS.csv file:

https://www.purpleair.com/json?key=<b>YLV2RFZLX93DRHY3</b>&show=<b>78091</b>

You should see a page that looks like this (note a different sensor ID shown here): <br></br>
<img width="292" src="https://user-images.githubusercontent.com/81830321/113453921-81bcdf80-93b3-11eb-9fbe-d74141a24818.png"> <br></br>


<b>3.</b> Make a CSV file with the following columns names, fill in information for PAs:

<b>PA_API_ID_A</b> = First instance of "THINGSPEAK_PRIMARY_ID” on page from step 2.

<b>PA_API_key_A</b>  = First instance of "THINGSPEAK_PRIMARY_ID_READ_KEY" on page from step 2

<b>PA_API_ID_B</b> = First instance of "THINGSPEAK_PRIMARY_ID” on page from step 2. 

<b>PA_API_key_B</b>  = First instance of "THINGSPEAK_PRIMARY_ID_READ_KEY" on page from step 2

<b>PA_column_name</b> = desired column name for output file, leave off units, they will be added along with the a and b designations (ie. _a_ugm3 added)<br></br>


<b>4.</b> Run python script:

./pa-api-pulldata.py startdate enddate input.csv 

Where start date and enddate are in YYYY-MM-DD HH:MM:SS format. For example:

./pa-api-pulldata.py 2021-09-09 00:00:00 2021-09-10 00:00:00 PA_IDs.csv 

Note that the amount of data that can be download at once from this script is limited. If you are not getting the full date range of data needed, try downloading in smaller increments. Weekly increments seem to work well.



