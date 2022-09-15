#!/bin/python3

import json
import os
import pandas as pd
from datetime import datetime, timedelta
import requests

pd.options.mode.chained_assignment = None

df_diff = pd.read_csv('./dags/tmp.csv')

file_exists = os.path.exists('./dags/tmp.csv')

if file_exists :
    os.remove("./dags/tmp.csv")


f = open('./dags/trello_token.json')


trello_info = json.load(f)

trello_key = trello_info['key']

trello_token = trello_info['token']

trello_id = trello_info['id2']

url = f'https://api.trello.com/1/cards?idList={trello_id}&key={trello_key}&token={trello_token}'


for index in range(len(df_diff)):
    
    data = {
   'name': df_diff['ds_title'].iloc[index]+" "+df_diff['nm_repository'].iloc[index],
    'due': df_diff['dt_closed'].iloc[index],
    'desc': df_diff['in_criticity'].iloc[index]
    } 
    
    
    requests.post(url,data=data)