# purpleair-api
python script using the PurpleAir API to download sensor PM2.5 data 

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


