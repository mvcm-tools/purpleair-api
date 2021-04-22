# purpleair-api-pulldata-v2.py
Python script using the PurpleAir API to download sensor PM2.5 data.

Updated version of "purpleair-api-pulldata.py" with simpler user input. Instead of the user having to look up the API ID's and read keys from the PurpleAir website, this version pulls these values from the "PA_IDs.csv" file. Users can change line X of this script to specify which PAs to pull data from, the default will pull data from all PAs in the CSV.

Usage now uses a "start" and "end" date input rather than a "days from" input:

./purpleair-api-pulldata-v2.py startdate enddate

startdate and enddate should be input in YYYY-MM-DD HH:MM:SS format

-------------------------------------------------------------------------------------------------------------------------------------------------------------------

# purpleair-api-pulldata.py
Python script using the PurpleAir API to download sensor PM2.5 data 

Usage:

./purpleair-api-pulldata.py #ofdays

#ofdays = # of days prior to the current day to pull data for

You can edit the "sensors" list to include PurpleAir sensors you want, currently pulls data from A and B sensors of 10 Fairbanks PurpleAirs (see map for details)

To find PurpleAir API IDs and read keys from map:
- go to the map at https://www.purpleair.com/map
- Hover over "Get this widget" and click on "JSON"
- <img width="292" src="https://user-images.githubusercontent.com/81830321/113453656-eaf02300-93b2-11eb-8fe8-e9d638801bb1.png">
- Thingspeak API IDs and read keys are found here 
- <img width="292" src="https://user-images.githubusercontent.com/81830321/113453921-81bcdf80-93b3-11eb-9fbe-d74141a24818.png">
- The "primary" IDs and read keys are where PM2.5 data in microgram/m3 is found 

