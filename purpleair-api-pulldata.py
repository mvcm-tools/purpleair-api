# python script to pull 10-min data from PurpleAir website using their API
# pulls from data from the #ofdays before todays date to todays date
# based on code from https://blocks.roadtolarissa.com/ekerstein/56757f993a7a8d17eabbca5a8562f5cc
# modified data output for cleaner output file

import requests # for url requests
import json # for json reading/writing
import time # for epoch timestamp
import pandas as pd # for writing csv files
import datetime
import re 
import sys

# #daystoget = the amount of days prior to the current date to pull
print('Usage: '+sys.argv[0]+' #daystoget')

#################################################
#           Configure user settings             # 
#################################################


# list sensor API information here for A and B sensors

sensors = [
    # PurpleAir A sensors on RAMS-trailer during winter, powered off during summer
    # 3m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '872114',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'OCRK8BNKBJL92NOX',
        'column_name':'pa_e530_lvl1_pm2_5_atm_a'
    },
    # 6m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '873152',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'MUGUNCMC43IWEU66',
        'column_name':'pa_7a6c_lvl2_pm2_5_atm_a'
    },
    # 9m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '871129',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'PZRQP9GYFMKM8SBG',
        'column_name':'pa_e3a5_lvl3_pm2_5_atm_a'
    },
    # 11m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '872138',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'GJ3AHFZTM26MLP0O',
        'column_name':'pa_e4b7_lvl4_pm2_5_atm_a'
    },
    # PurpleAir B sensors on RAMS-trailer during winter, powered off during summer
    # 3m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '872116',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'PBWRBKY00X7EDUGE',
        'column_name':'pa_e530_lvl1_pm2_5_atm_b'
    },
    # 6m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '873155',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'NG4R4VN01NOGQN1F',
        'column_name':'pa_7a6c_lvl2_pm2_5_atm_b'
    },
    # 9m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '871131',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'EW6PW2IZHN0SZQLO',
        'column_name':'pa_e3a5_lvl3_pm2_5_atm_b'
    },
    # 11m sensor
    {
        'THINGSPEAK_PRIMARY_ID': '872141',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'ACO9N6LSZ7NFJKGT',
        'column_name':'pa_e4b7_lvl4_pm2_5_atm_b'
    },
    # "CTC Building" A and B sensors, at 20m AGL during winter, off during summer
    {
        'THINGSPEAK_PRIMARY_ID': '697980',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'WTITHS0ZRT6G293L',
        'column_name':'CTC_pa_roof_pm2_5_atm_a'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '697982',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '4VFPCHW3QNXO2J67',
        'column_name':'CTC_pa_roof_pm2_5_atm_b'
    },
    # "CTCTrailer#1" A and B sensors, at ground level during winter, off during summer
    {
        'THINGSPEAK_PRIMARY_ID': '874052',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '29H8UGV23MSYTI9W',
        'column_name':'CTC_pa_ground_pm2_5_atm_a'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '874054',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'LW43AJKBUZR7TE5J',
        'column_name':'CTC_pa_ground_pm2_5_atm_b'
    },
    # NCORE sensors, assorted, usually on at all times
    {
        'THINGSPEAK_PRIMARY_ID': '873031',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '71ULQ63TQKG2ELW7',
        'column_name':'NCORE3_pa_pm2_5_atm_a'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '873033',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'AZTSCXJRZJN5BFND',
        'column_name':'NCORE3_pa_pm2_5_atm_b'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '873027',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'GF0WBYEO5FCP281N',
        'column_name':'NCORE4_pa_pm2_5_atm_a'

    },
    {
        'THINGSPEAK_PRIMARY_ID': '873029',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '05J64WSWPR0EBE7M',
        'column_name':'NCORE4_pa_pm2_5_atm_b'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '583421',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '7R04SXXFCMA698ZS',
        'column_name':'NCORE4-2_pa_pm2_5_atm_a'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '583425',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '3G49SNHIGWCTQDU6',
        'column_name':'NCORE4-2_pa_pm2_5_atm_b'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '677633',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': '504V26DA09IG9XZA',
        'column_name':'NCORE-ADEC1_pa_pm2_5_atm_a'
    },
    {
        'THINGSPEAK_PRIMARY_ID': '677635',
        'THINGSPEAK_PRIMARY_ID_READ_KEY': 'SN2MPVF1GWGPPZK5',
        'column_name':'NCORE-ADEC1_pa_pm2_5_atm_b'
    }


]

# define function to clean up date string in YYYYmmddTHHMMSSZ format
def clean_datetime(date,single):
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
        'days': str(sys.argv[1]), # days of data to get
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
    df_out.index = clean_datetime(df_out['created_at'],'no')
    dropcols = ['created_at','entry_id', 'PM1.0 (ATM)' , 'PM2.5 (ATM)', 'PM10.0 (ATM)', 'Uptime','RSSI','Temperature','Humidity','PM2.5 (CF=1)']
    df_out = df_out.drop(dropcols,axis=1)
    df_out.index = df_out.index.rename('datetime_UTC')
    df_out.to_csv(path_or_buf = sname+'_'+str(dt)+'.txt', sep = '\t', na_rep = 'NaN', float_format='%.4f')



# pull data from each sensor in sensor list
for xi in range(0,len(sensors)):
    sensor_id = sensors[xi]['THINGSPEAK_PRIMARY_ID']
    sensor_key = sensors[xi]['THINGSPEAK_PRIMARY_ID_READ_KEY']
    sensor_name = sensors[xi]['column_name']
    pull_data(sensor_name,sensor_id,sensor_key)
