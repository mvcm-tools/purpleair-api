
# python script to pull 10-min data from PurpleAir website using their API
# updated version of "pa-api-pulldata.py" with updated user configuration
# based on code from https://blocks.roadtolarissa.com/ekerstein/56757f993a7a8d17eabbca5a8562f5cc
# modified data output for cleaner output file

import requests # for url requests
import json # for json reading/writing
import time # for epoch timestamp
import pandas as pd # for writing csv files
import datetime
import re 
import sys

print(' ')
print('Usage: '+sys.argv[0]+' startdate enddate ids.csv')
print(' ')
print('startdate and enddate should be in YYYY-MM-DD HH:MM:SS')
print(' ')
print('ids.csv contains A and B PurpleAir API keys and IDs')
print(' ')
print('data reported in 10 minute intervals')
print(' ')


# load dataframe of PA IDs and API keys
ids = pd.read_csv(str(sys.argv[5]), delimiter = ',')
ids.index = ids['PA_column_name']
names  = ids['PA_column_name']

# create empty dictionary to hold PA API information
df_a = pd.DataFrame(index=range(0,len(names)),columns = ['id','key','name'])
df_b = pd.DataFrame(index=range(0,len(names)),columns = ['id','key','name'])

# grab data for list of PA sensors in "ids['PA_column_name']"
for xi in range(0,len(names)):
    # A sensors
    paida = ids['PA_API_ID_A'][names[xi]]
    pakeya = ids['PA_API_key_A'][names[xi]]
    df_a.loc[xi,'id'] = paida
    df_a.loc[xi,'key'] = pakeya
    df_a.loc[xi,'name'] = names[xi]+'_a'
    # B sensors
    paidb = ids['PA_API_ID_B'][names[xi]]
    pakeyb = ids['PA_API_key_B'][names[xi]]
    df_b.loc[xi,'id'] = paidb
    df_b.loc[xi,'key'] = pakeyb
    df_b.loc[xi,'name'] = names[xi]+'_b'


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
    #dropcols = ['entry_id', 'PM1.0 (ATM)' , 'PM2.5 (ATM)', 'PM10.0 (ATM)', 'Uptime','RSSI','Temperature','Humidity','PM2.5 (CF=1)']
    df_out = df_out.drop(dropcols,axis=1)
    df_out.index = df_out.index.rename('datetime_UTC')
    df_out.to_csv(path_or_buf = sname+'_'+str(dt)+'.txt', sep = '\t', na_rep = 'NaN', float_format='%.4f')
    print('wrote data to file: '+sname+'_'+str(dt)+'.txt')


# Iterate sensor list through pull_data()
for xi in range(0,len(sensors)):
    sensor_id = sensors[xi]['id']
    sensor_key = sensors[xi]['key']
    sensor_name = sensors[xi]['name']
    pull_data(sensor_name,sensor_id,sensor_key)
