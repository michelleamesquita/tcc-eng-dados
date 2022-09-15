import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import sys

pd.options.mode.chained_assignment = None

f = open('./dags/snyk_token.json')

snyk_token = json.load(f)

project_id=sys.argv[1]

issues=sys.argv[2]


project_id=project_id.replace("\n",'')
issues=issues.replace("\n",'').replace(":",'')

data_json=[]

url = f'https://app.snyk.io/org/michelleamesquita-bgy/project/{project_id}/sast-issues/{issues}'
print(url)
data = requests.get(url, headers=snyk_token)
data_json.append(data.json())

status_snyk=[]
url_snyk=[]
title_snyk=[] 
repository_url_snyk=[]
created_at_snyk=[]
criticity_at_snyk=[]
end_at_snyk=[]
deadline_snyk=[]
squad_list=[]
source_list=[]
tool=[]

for k in range(len(data_json[0]['sastData'])):  
            status_snyk.append(data_json[0]['sastData'][k]['snippet']['status'])
            url_snyk.append(data_json[0]['sastData'][k]['metadata']['primaryFilePath'])
            title_snyk.append(data_json[0]['sastData'][k]['metadata']['name'])
            repository_url_snyk.append(data_json[0]['sastData'][k]['metadata']['fileBaseUrl'])
            criticity_at_snyk.append(data_json[0]['sastData'][k]['metadata']['severity'])
            created_at_snyk.append('')
            end_at_snyk.append('')
            deadline_snyk.append('')
            squad_list.append('')
            source_list.append('')
            tool.append('')
            
            
data_snyk= {'squad':squad_list,'title':title_snyk,'repository':repository_url_snyk,'criticity':criticity_at_snyk,'date_created':created_at_snyk,'date_end':end_at_snyk,'status':status_snyk,'deadline':deadline_snyk,'url_issue':url_snyk,'source_data':source_list,'tool':tool}

df_snyk = pd.DataFrame(data_snyk)

df_snyk['date_created']=pd.to_datetime(datetime.today()).strftime("%Y-%m-%d")
df_snyk['criticity']=[x.capitalize() for x in df_snyk['criticity']]
df_snyk['squad']=[x[3] for x in df_snyk['repository'].str.split('/')][0]

for i in range(len(df_snyk)):
    if df_snyk['criticity'][i] == 'High':
        df_snyk['date_end'][i] = pd.to_datetime(df_snyk['date_created'][i])+ pd.DateOffset(days=30)
    elif df_snyk['criticity'][i] == 'Medium':
        df_snyk['date_end'][i] = pd.to_datetime(df_snyk['date_created'][i])+ pd.DateOffset(days=90)
    elif df_snyk['criticity'][i] == 'Low':
        df_snyk['date_end'][i] = pd.to_datetime(df_snyk['date_created'][i])+ pd.DateOffset(days=180)
    elif df_snyk['criticity'][i] == 'Critical':
        df_snyk['date_end'][i] = pd.to_datetime(df_snyk['date_created'][i])+ pd.DateOffset(days=4)
        
for i in range(len(df_snyk)):
        if df_snyk['date_end'][i] < datetime.today() and df_snyk['status'][i] == 'open':
            df_snyk['deadline'][i] = 'passed!'
        elif df_snyk['date_end'][i] >= datetime.today() or df_snyk['status'][i] == 'closed' or df_snyk['status'][i] == None:
            if df_snyk['status'][i] == None:
                df_snyk['status'][i] = 'open'
            df_snyk['deadline'][i] = 'good :) ' 

df_snyk['date_end'] = pd.to_datetime(df_snyk['date_end']).apply(lambda x: x.date())
df_snyk['source_data'] = 'SAST'
df_snyk['tool'] = 'Snyk'

df_snyk.to_csv(f'./dags/out_{project_id}.csv')

print('hello :)')