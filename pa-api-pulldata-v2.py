# python script to pull 10-min data from PurpleAir website using their API
# updated version of "purpleair-api-pulldata.py" with updated user configuration
# based on code from https://blocks.roadtolarissa.com/ekerstein/56757f993a7a8d17eabbca5a8562f5cc
# modified data output for cleaner output file

import requests # for url requests
import json # for json reading/writing
import time # for epoch timestamp
import pandas as pd # for writing csv files
import datetime
import re 
import sys

print('Usage: '+sys.argv[0]+' startdate enddate')
print(' ')
print('startdate and enddate should be in YYYY-MM-DD HH:MM:SS')
print(' ')
print('data reported in 10 minute intervals')

#################################################
#               USER CONFIG START               #
#################################################

# change names in "pas_to_get" 
# use names from the "PA_column_name" column in "PA_IDS.csv"

pas_to_get = ['CTC_pa_roof_pm2_5_atm','CTC_pa_ground_pm2_5_atm','pa_e530_lvl1_pm2_5_atm','pa_7a6c_lvl2_pm2_5_atm','pa_e3a5_lvl3_pm2_5_atm','pa_e4b7_lvl4_pm2_5_atm','NCORE3_pa_pm2_5_atm','NCORE4_pa_pm2_5_atm','NCORE4-2_pa_pm2_5_atm','NCORE-ADEC1_pa_pm2_5_atm','Piper_St_pa_pm2_5_atm','Hurst_Rd_pa_pm2_5_atm','Plack_Nelson_pa_pm2_5_atm','Dakota_St_pa_pm2_5_atm']

#################################################
#               USER CONFIG END                 #
#################################################


# load dataframe of PA IDs and API keys
ids = pd.read_csv('PA_IDs.csv', delimiter = ',')
ids.index = ids['PA_column_name']

# create empty dictionary to hold PA API information
df_a = pd.DataFrame(index=range(0,len(pas_to_get)),columns = ['id','key','name'])
df_b = pd.DataFrame(index=range(0,len(pas_to_get)),columns = ['id','key','name'])

# grab data for list of PA sensors in "pas_to_get"
for xi in range(0,len(pas_to_get)):
    # A sensors
    paida = ids['PA_API_ID_A'][pas_to_get[xi]]
    pakeya = ids['PA_API_key_A'][pas_to_get[xi]]
    df_a.loc[xi,'id'] = paida
    df_a.loc[xi,'key'] = pakeya
    df_a.loc[xi,'name'] = pas_to_get[xi]+'_a'
    # B sensors
    paidb = ids['PA_API_ID_B'][pas_to_get[xi]]
    pakeyb = ids['PA_API_key_B'][pas_to_get[xi]]
    df_b.loc[xi,'id'] = paidb
    df_b.loc[xi,'key'] = pakeyb
    df_b.loc[xi,'name'] = pas_to_get[xi]+'_b'


# concatenate a and b sensor data and re-index df
df_a.index = df_a['name']
df_b.index = df_b['name']
df = pd.concat([df_a,df_b])
df.index = range(0,len(df))

sensors = []

for xi in range(0,len(df)):
    sensors.append(dict(df.loc[xi,:]))



# define function to clean up date string in YYYYmmddTHHMMSSZ format
def clean_logdates(date,single):
    if single == 'no':
        outlist = []
        for xi in range(0,len(date)):
            raw = re.sub('Z','',date[xi])
            raw = re.sub('T',' ',raw)
            outlist.append(raw)
        return(outlist)
    if single == 'yes':
        output = []
        raw = re.sub('Z','',str(date))
        raw = re.sub('T',' ',raw)
        output.append(raw)
    return(output)  


# define function to pull sensor data
def pull_data(sname,sid,skey):
    # Make master data objects
    data = {}
    fields = ['created_at'] # manually add created_at field for csv header mapping
    url = 'https://api.thingspeak.com/channels/{}/feeds.json'.format(sid)
    # Thingspeak API parameters: https://www.mathworks.com/help/thingspeak/readdata.html
    params = {
        'api_key': skey, # sensor API key
        'start': pd.to_datetime(str(sys.argv[1])+' '+str(sys.argv[2])), # start date w/ format YYYY-MM-DD%20HH:MM:SS
        'end': pd.to_datetime(str(sys.argv[3])+' '+str(sys.argv[4])), # end date w/ format YYYY-MM-DD%20HH:MM:SS
        'round': '3', # round decimal places
        'average': '10' # 10 minute averages
        }
    r = requests.get(url, params=params)
    data_raw = r.json()
    fields_sensor = {}
    data_sensor = []
    # name fields
    for d in data_raw['channel']:
        if d.startswith('field'):
            field_name = data_raw['channel'][d]
            # Add to field sensor mapping
            fields_sensor[d] = field_name
            # Add to master field list
            if field_name not in fields:
                fields.append(field_name)
    for i, row in enumerate(data_raw['feeds']):
        # Add object to data
        data_sensor.append({})
        for key in row:  
            # Add and rename
            if key in fields_sensor:        
                new_key = fields_sensor[key]
                data_sensor[i][new_key] = row[key]
            # Or just add
            else:
                data_sensor[i][key] = row[key]
    for row in data_sensor:
        created_at = row['created_at']
    # Make new timestamp object if needed
        if created_at not in data:   
            data[created_at] = {}# Add to timestamp object
            for key in row:
            # If key exists, append to value list
                if key in data[created_at]:
                    data[created_at][key].append(row[key])
            # Else make new value list
                else:    
                   data[created_at][key] = [row[key]]
    # convert dictionary fields to a list for DataFrame output
    data_txt = []
    for timestamp in data:
        row = data[timestamp].copy()
        for key in row:
            row[key] = row[key][0] 
        data_txt.append(row)
    #get current date and time for output filename
    dt = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
    # create output dataframe from list
    df_out = pd.DataFrame(data_txt, columns = ['created_at','entry_id', 'PM1.0 (ATM)' , 'PM2.5 (ATM)', 'PM10.0 (ATM)', 'Uptime','RSSI','Temperature','Humidity','PM2.5 (CF=1)'])
    for row in data_txt:
        empty = True
    # Check if empty row
        for key in row:
            if key != 'created_at' and row[key]:
                empty = False 
    # If not empty row add line of data to output
        if empty == False:
            df_out.append(list(row.values()))
    df_out[sname] = df_out['PM2.5 (ATM)']
    df_out.index = clean_logdates(df_out['created_at'],'no')
    dropcols = ['created_at','entry_id', 'PM1.0 (ATM)' , 'PM2.5 (ATM)', 'PM10.0 (ATM)', 'Uptime','RSSI','Temperature','Humidity','PM2.5 (CF=1)']
    df_out = df_out.drop(dropcols,axis=1)
    df_out.index = df_out.index.rename('datetime_UTC')
    df_out.to_csv(path_or_buf = sname+'_'+str(dt)+'.txt', sep = '\t', na_rep = 'NaN', float_format='%.4f')



# Iterate sensor list through pull_data()
for xi in range(0,len(sensors)):
    sensor_id = sensors[xi]['id']
    sensor_key = sensors[xi]['key']
    sensor_name = sensors[xi]['name']
    pull_data(sensor_name,sensor_id,sensor_key)
