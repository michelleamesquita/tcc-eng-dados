import os
import sys
import glob
from pathlib import Path
import pandas as pd

# sys.path.insert(0, './')

from db_data import conect

def get_gitlab_data():
    for x in open("./project_id_gitlab.txt", "r"):
    
        print("project_id: "+x)
        project_id = x

        os.system(f'python3 ./gitlab-extract-data.py {project_id}')
        
        print('finished')
        
        
def get_snyk_data():
    
    for x in open("./project_id_snyk.txt", "r"):
    
        print("project_id: "+x)
        project_id = x
        project_id=project_id.strip()
        
        print(project_id.strip() == '5e157f37-dace-4d41-91ba-3c3430cc8f5a')

        if project_id == '5e157f37-dace-4d41-91ba-3c3430cc8f5a':
            issues = '3ff95689-df12-442d-8c53-b2fd99a99e4b'
            print(f'python3 ./snyk-extract-data.py {project_id} {issues}')
          
            
        else:
            
            issues = 'cfa40f5e-8d01-41eb-8b64-f465832e9afc'
        
        print(f'python3 ./snyk-extract-data.py {project_id} {issues}')
        
        os.system(f'python3 ./snyk-extract-data.py {project_id} {issues}')
        
        
      
        
def get_github_data():
    for x in open("./repository.txt", "r"):
        
        print("repository: "+x)
        repository = x

        os.system(f'python3 ./github-extract-data.py {repository}')
        
        print('finished')
        
        
def generate_csv_data():
    file_list = list(Path("./").glob("*.csv"))
    li = []

    for filename in file_list:
        df = pd.read_csv(filename, index_col=0, header=0)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    df['month_beggining'] = df['date_created'].str[:7]
    df['month_end'] = df['date_end'].str[:7]
    df['index'] = range(len(df))
    
    df = df.rename(columns={'index': 'id_vulnerability','squad': 'nm_squad', 'title': 'ds_title' , 'repository':'nm_repository', 'criticity':'in_criticity', 'date_created':'dt_created', 'date_end':'dt_closed', 'status':'st_vulnerability', 'deadline':'in_deadline', 'url_issue':'ds_url_issue', 'source_data':'nm_source_data', 'month_beggining':'cd_month_start', 'month_end':'cd_month_end'})
    
    df.to_csv('./final_csv.csv')
    
    print('finished')
    
    
def add_db_data():
    
    df_current = pd.read_csv('./final_csv.csv', index_col=0, header=0)
    df_current.id_vulnerability=df_current.id_vulnerability.astype("object")
    
    query= f"""SELECT * FROM mydatabase.security;"""
    
    df_db=[]
    
    df_db = connect(query,df_db)
    
   

    
#     df_diff = pd.concat([df_current,df_db]).drop_duplicates(subset=["ds_url_issue","id_vulnerability"],keep=False).reset_index()
#     mask = df_diff['st_vulnerability'].isin(['open', 'new'])
#     df_diff1 = df_diff[mask]
    
#     mask = df_diff['st_vulnerability'].isin(['fixed', 'closed','reopened'])
#     df_diff2 = df_diff[mask]
    
    
#     df_diff1.reset_index(inplace=True)
#     df_diff1.index  = df_diff.index + len(df_db)
#     df_diff1.id_vulnerability = df_diff.index 
#     df_diff1.id_vulnerability=df_diff.id_vulnerability.astype("object")
    
#     df_diff2.reset_index(inplace=True)
#     df_diff2.index  = df_diff.index + len(df_db)
#     df_diff2.id_vulnerability = df_diff.index 
#     df_diff2.id_vulnerability=df_diff.id_vulnerability.astype("object")
    
#     # Insert new itens on DB
    
#     if len(df_diff1)>0:
#         query= "INSERT INTO bidm_vulnerability.ct_vulnerability (id_vulnerability, dh_inserted, nm_squad, ds_title, nm_repository, in_criticity, dt_created, dt_closed, st_vulnerability, in_deadline, ds_url_issue, nm_source_data, tool,cd_month_start, cd_month_end) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

#         print('hello')
#         print(df_diff1)
        
#         df_final=df_diff1

#         os.system(f'python3 ./db_data.py {query} {df_final}')
        
    
#     # Update db
    
#     if len(df_diff2)>0:
#         query2 = f"""UPDATE mydatabase.security set st_vulnerability = '{row['st_vulnerability'][index]}',dh_updated='{datetime.now()}' where ds_title = '{row['ds_title'][index]}' and nm_repository = '{row['nm_repository'][index]}'""" 

#         for index, row in df_diff2.iterrows():
#             if len(df_diff2) >0:
#                 df_final=df_diff2
#                 os.system(f'python3 ./db_data.py {query} {df_final}')
    
#     # Remove old file
#     file_exists = os.path.exists('./final_csv.csv')

#     if file_exists :
#         os.remove('./*.csv')
        
#     return df_diff1,df_diff2
        
        
        
# get_gitlab_data()
# get_github_data()
# get_snyk_data()
# generate_csv_data()
add_db_data()