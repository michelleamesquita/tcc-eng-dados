import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import sys

pd.options.mode.chained_assignment = None

repository=sys.argv[1]

repository=repository.replace("\n",'')

url = f'https://api.github.com/repos/{repository}/issues?page=1&state=all'
data = requests.get(url)

data_json=[]
i=0
while data.text!='[]':
    i+=1
    url = f'https://api.github.com/repos/{repository}/issues?page={i}&state=all'
    # print(url)
    data = requests.get(url)
    data_json.append(data.json())
    

status_gh=[]
url_gh=[]
title_gh=[] 
repository_url_gh=[]
user_gh=[]
created_at_gh=[]
criticity_at_gh=[]
end_at_gh=[]
deadline_gh=[]
squad_list=[]
source_list=[]

for k in range(len(data_json[0])):  
        status_gh.append(data_json[0][k]['state'])
        url_gh.append(data_json[0][k]['url'])
        title_gh.append(data_json[0][k]['title'])
        repository_url_gh.append(data_json[0][k]['repository_url'])
        user_gh.append(data_json[0][k]['user'])
        created_at_gh.append(data_json[0][k]['created_at'])
        criticity_at_gh.append(data_json[0][k]['body'])
        end_at_gh.append('')
        deadline_gh.append('')
        squad_list.append('')
        source_list.append('')
        
data_gh= {'squad':squad_list,'title':title_gh,'repository':repository_url_gh,'criticity':criticity_at_gh,'date_created':created_at_gh,'date_end':end_at_gh,'status':status_gh,'deadline':deadline_gh,'url_issue':url_gh,'source_data':source_list}

df_gh = pd.DataFrame(data_gh)

df_gh['repository']=["https://github.com/michelleamesquita/"+x[5] for x in df_gh['repository'].str.split('/')]

df_gh['date_created']=df_gh['date_created'].str[:10]

df_gh=df_gh[(df_gh.criticity).map(lambda d: d!=None)]

df_gh=df_gh.loc[df_gh.status=='open']

for x in range(len(df_gh['criticity'])):
    if df_gh['criticity'][x] != None:
        if 'High' in df_gh['criticity'][x]:
            df_gh['criticity'][x]='High'
        elif 'Medium' in df_gh['criticity'][x]:
             df_gh['criticity'][x]='Medium'
        else:
             df_gh['criticity'][x]='Low'
                
                
df_gh['squad']=[x[4] for x in df_gh['url_issue'].str.split('/')]

df_gh['url_issue']=[f"https://github.com/{repository}/issues/"+x[7] for x in df_gh['url_issue'].str.split('/')]

for i in range(len(df_gh)):
    if df_gh['criticity'][i] == 'High':
        df_gh['date_end'][i] = pd.to_datetime(df_gh['date_created'][i])+ pd.DateOffset(days=30)
    elif df_gh['criticity'][i] == 'Medium':
        df_gh['date_end'][i] = pd.to_datetime(df_gh['date_created'][i])+ pd.DateOffset(days=90)
    elif df_gh['criticity'][i] == 'Low':
        df_gh['date_end'][i] = pd.to_datetime(df_gh['date_created'][i])+ pd.DateOffset(days=180)
    elif df_gh['criticity'][i] == 'Critical':
        df_gh['date_end'][i] = pd.to_datetime(df_gh['date_created'][i])+ pd.DateOffset(days=4)
        
        
for i in range(len(df_gh)):
    if df_gh['date_end'][i] < datetime.today() and df_gh['status'][i] == 'open':
        df_gh['deadline'][i] = 'passed!'
    elif df_gh['date_end'][i] > datetime.today() or df_gh['status'][i] == 'closed':
        df_gh['deadline'][i] = 'good :) ' 
        
df_gh['date_end'] = pd.to_datetime(df_gh['date_end']).apply(lambda x: x.date())

df_gh['source_data'] = 'SCA'
df_gh['tool'] = 'White Source'
repository=repository.replace('/','_')
df_gh.to_csv(f'./dags/out_{repository}.csv')

print('hello :)')