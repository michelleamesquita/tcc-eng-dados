import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import sys

pd.options.mode.chained_assignment = None

project_id=sys.argv[1]

data_json=[]

url = f'https://gitlab.com/api/v4/projects/{project_id}/jobs/artifacts/main/raw/report_json.json?job=owasp'
print(url)
data = requests.get(url)
data_json.append(data.json())


data_json2=[]

url = f'https://gitlab.com/api/v4/projects/{project_id}/jobs/artifacts/main/raw/safety-results.json?job=dependencycheck'
print(url)
data = requests.get(url)
data_json2.append(data.json())


data_json3=[]

url = f'https://gitlab.com/api/v4/projects/{project_id}/jobs/artifacts/main/raw/bandit-output.json?job=bandit'
print(url)
data = requests.get(url)
data_json3.append(data.json())


status_gitlab=[]
url_gitlab=[]
title_gitlab=[] 
repository_url_gitlab=[]
created_at_gitlab=[]
criticity_at_gitlab=[]
end_at_gitlab=[]
deadline_gitlab=[]
squad_list=[]
source_list=[]
tool=[]

for k in range(len(data_json[0]['site'][0])):  
            status_gitlab.append('')
            url_gitlab.append(data_json[0]['site'][0]['alerts'][k]['instances'][0]['uri'])
            title_gitlab.append(data_json[0]['site'][0]['alerts'][k]['name'])
            repository_url_gitlab.append(url)
            criticity_at_gitlab.append(data_json[0]['site'][0]['alerts'][k]['riskdesc'])
            created_at_gitlab.append(data_json[0]['@generated'])
            end_at_gitlab.append('')
            deadline_gitlab.append('')
            squad_list.append('')
            source_list.append('DAST')
            tool.append('Owasp Zap API')
            
            
for k in range(len(data_json2[0]['report_meta'])):  
            status_gitlab.append('')
            url_gitlab.append(data_json2[0]['report_meta']['scanned'][0])
            title_gitlab.append(data_json2[0]['vulnerabilities'])
            repository_url_gitlab.append(url)
            criticity_at_gitlab.append(data_json2[0]['affected_packages'])
            created_at_gitlab.append(data_json2[0]['report_meta']['timestamp'])
            end_at_gitlab.append('')
            deadline_gitlab.append('')
            squad_list.append('')
            source_list.append('SCA')
            tool.append('Dependenc Check')
            

for k in range(len(data_json3[0])):  
            status_gitlab.append('')
            url_gitlab.append(data_json3[0]['results'][0]['filename'])
            title_gitlab.append(data_json3[0]['results'][0]['test_name'])
            repository_url_gitlab.append(url)
            criticity_at_gitlab.append(data_json3[0]['results'][0]['issue_severity'])
            created_at_gitlab.append(data_json3[0]['generated_at'])
            end_at_gitlab.append('')
            deadline_gitlab.append('')
            squad_list.append('')
            source_list.append('SAST')
            tool.append('Bandit')
            
            
data_gitlab={'squad':squad_list,'title':title_gitlab,'repository':repository_url_gitlab,'criticity':criticity_at_gitlab,'date_created':created_at_gitlab,'date_end':end_at_gitlab,'status':status_gitlab,'deadline':deadline_gitlab,'url_issue':url_gitlab,'source_data':source_list,'tool':tool}

df_gitlab = pd.DataFrame(data_gitlab)

df_gitlab=df_gitlab.drop(df_gitlab[(df_gitlab.title).map(lambda d: len(d)) < 1].index).reset_index(drop=True)

df_gitlab['date_created']=pd.to_datetime(df_gitlab['date_created']).apply(lambda x: x.strftime('%Y-%m-%d'))

df_gitlab['criticity']=[x[0].strip().capitalize() for x in df_gitlab['criticity'].str.split('(')]

df_gitlab['squad']='michelleamesquita'

df_gitlab['status']='open'

for i in range(len(df_gitlab)):
    if df_gitlab['criticity'][i] == 'High':
        df_gitlab['date_end'][i] = pd.to_datetime(df_gitlab['date_created'][i])+ pd.DateOffset(days=30)
    elif df_gitlab['criticity'][i] == 'Medium':
        df_gitlab['date_end'][i] = pd.to_datetime(df_gitlab['date_created'][i])+ pd.DateOffset(days=90)
    elif df_gitlab['criticity'][i] == 'Low':
        df_gitlab['date_end'][i] = pd.to_datetime(df_gitlab['date_created'][i])+ pd.DateOffset(days=180)
    elif df_gitlab['criticity'][i] == 'Critical':
        df_gitlab['date_end'][i] = pd.to_datetime(df_gitlab['date_created'][i])+ pd.DateOffset(days=4)
        
for i in range(len(df_gitlab)):
        if df_gitlab['date_end'][i] < datetime.today() and df_gitlab['status'][i] == 'open':
            df_gitlab['deadline'][i] = 'passed!'
        elif df_gitlab['date_end'][i] >= datetime.today() or df_gitlab['status'][i] == 'closed' or df_gitlab['status'][i] == None:
            if df_gitlab['status'][i] == None:
                df_gitlab['status'][i] = 'open'
            df_gitlab['deadline'][i] = 'good :) ' 
            

df_gitlab['date_end'] = pd.to_datetime(df_gitlab['date_end']).apply(lambda x: x.date())

df_gitlab.to_csv(f'./dags/out_{project_id}.csv')

print('hello :)')