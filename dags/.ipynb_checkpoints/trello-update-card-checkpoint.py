import json
import os
import pandas as pd
from datetime import datetime, timedelta
import requests


pd.options.mode.chained_assignment = None

df_diff = pd.read_csv('./dags/tmp2.csv')

file_exists = os.path.exists('./dags/tmp2.csv')

if file_exists :
    os.remove("./dags/tmp2.csv")

f = open('./dags/trello_token.json')
trello_info = json.load(f)

trello_key = trello_info['key']
trello_token = trello_info['token']
trello_id = trello_info['id3']

url= f'https://api.trello.com/1/boards/{trello_id}/cards/open?key={trello_key}&token={trello_token}'

data= requests.get(url)
data=data.json()


for index in range(len(data)):
    if data[index]['idList'] == '631d67c73c8eb60052696c7a':
        cardID=data[index]['id']
        listID='631d67cf4f59e60164d26286'
        url2 = f'https://api.trello.com/1/cards/{cardID}?idList={listID}&key={trello_key}&token={trello_token}'
        requests.put(url2)