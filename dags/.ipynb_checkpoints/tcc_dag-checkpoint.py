from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
import os
import pandas as pd
import glob
from pathlib import Path
import sys
import mysql.connector
import config
from configparser import ConfigParser
import pandas as pd
from datetime import datetime as dt
from sqlalchemy import create_engine
import json
import requests
from datetime import datetime, timedelta


default_args = {
   'owner': 'Michelle Mesquita',
   'depends_on_past': False,
   'start_date': datetime(2022, 9, 9),
   'retries': 0,
    'schedule_interval':'@monthly'
   }


dag = DAG(
    "tcc_dag",
    description="TCC", 
    catchup=False,
    default_args=default_args
)

def get_snyk_data():
    
    for x in open("./dags/project_id_snyk.txt", "r"):
    
        print("project_id: "+x)
        project_id = x
        project_id=project_id.strip()


        if project_id == '5e157f37-dace-4d41-91ba-3c3430cc8f5a':
            
            issues = '3ff95689-df12-442d-8c53-b2fd99a99e4b'

        else:
             issues = 'cfa40f5e-8d01-41eb-8b64-f465832e9afc'

        os.system(f'python3 ./dags/snyk-extract-data.py {project_id} {issues}')
        

    
    
def get_gitlab_data():
    for x in open("./dags/project_id_gitlab.txt", "r"):
    
        print("project_id: "+x)
        project_id = x

        os.system(f'python3 ./dags/gitlab-extract-data.py {project_id}')
        

    
def get_github_data():
    for x in open("./dags/repository.txt", "r"):
        
        print("repository: "+x)
        repository = x

        os.system(f'python3 ./dags/github-extract-data.py {repository}')
        

    
def generate_csv_data():
    file_list = list(Path("./dags/").glob("*.csv"))
    li = []

    for filename in file_list:
        df = pd.read_csv(filename, index_col=0, header=0)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    df['month_beggining'] = df['date_created'].str[:7]
    df['month_end'] = df['date_end'].str[:7]
    df['index'] = range(len(df))
    
    df = df.rename(columns={'index': 'id_vulnerability','squad': 'nm_squad', 'title': 'ds_title' , 'repository':'nm_repository', 'criticity':'in_criticity', 'date_created':'dt_created', 'date_end':'dt_closed', 'status':'st_vulnerability', 'deadline':'in_deadline', 'url_issue':'ds_url_issue', 'source_data':'nm_source_data', 'month_beggining':'cd_month_start', 'month_end':'cd_month_end'})
    
    df.to_csv('./dags/final_csv.csv')
    
    print('finished')
    
    
def add_db_data():
    
    df_current = pd.read_csv('./dags/final_csv.csv', index_col=0, header=0)
    df_current.id_vulnerability=df_current.id_vulnerability.astype("object")
    
    query= f"""SELECT * FROM mydatabase.security;"""
    
    df_db=[]
    
    df_db = connect(query,df_db)
    
    
    df_diff = pd.concat([df_current,df_db]).drop_duplicates(subset=["ds_url_issue","ds_title"],keep=False).reset_index()
    mask = df_diff['st_vulnerability'].isin(['open', 'new'])
    
    
    df_diff1 = df_diff[mask]
    
    
    mask = df_diff['st_vulnerability'].isin(['fixed', 'closed','reopened'])
    df_diff2 = df_diff[mask]
    
    
    # df_diff1.reset_index(inplace=True)
    df_diff1.index  = df_diff1.index + len(df_db)
    df_diff1.id_vulnerability = df_diff1.index 
    df_diff1.id_vulnerability=df_diff1.id_vulnerability.astype("object")
    
    # df_diff2.reset_index(inplace=True)
    df_diff2.index  = df_diff2.index + len(df_db)
    df_diff2.id_vulnerability = df_diff2.index 
    df_diff2.id_vulnerability=df_diff2.id_vulnerability.astype("object")
    
    
    
    # Insert new itens on DB
    
    if not df_diff1.empty:
        if not pd.isna(df_diff1['ds_title'].iloc[0]):
            query= "INSERT INTO mydatabase.security (id_vulnerability, dt_added, nm_squad, ds_title, nm_repository, in_criticity, dt_created, dt_closed, st_vulnerability, in_deadline, ds_url_issue, nm_source_data, tool, cd_month_start, cd_month_end) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            df_diff1_tmp = connect(query,df_diff1)
            df_diff1.to_csv('./dags/tmp.csv')

    
    # Update db
    
    if not df_diff2.empty:
        if not pd.isna(df_diff2['ds_title'].iloc[0]):
            for index in range(len(df_diff2)):
                    query2 = f"""UPDATE mydatabase.security set st_vulnerability = '{df_diff2['st_vulnerability'].iloc[index]}',dt_added='{datetime.now()}' where ds_title = '{df_diff2['ds_title'].iloc[index]}'""" 
                    df_diff2_tmp = connect(query2,df_diff2)
                    df_diff2.to_csv('./dags/tmp2.csv')
  
    
    # Remove old file
    file_exists = os.path.exists('./dags/final_csv.csv')

    if file_exists :
        
        file_list = list(Path("./dags/").glob("out_*.csv"))
        os.remove('./dags/final_csv.csv')
        for filename in file_list:
            os.remove(filename)
        
        
    
def generate_card_trello():
    
    file_exists = os.path.exists('./dags/tmp.csv')

    if file_exists :
        
        df1 = pd.read_csv('./dags/tmp.csv')
        if not df1.empty >0:
            df1.to_csv('./dags/tmp.csv')
            os.system(f'python3 ./dags/trello-generate-card.py')
        
    file_exists2 = os.path.exists('./dags/tmp2.csv')


    if file_exists2 :
        df2 = pd.read_csv('./dags/tmp2.csv')
        if not df2.empty >0:
                            df2.to_csv('./dags/tmp2.csv')
                            os.system(f'python3 ./dags/trello-update-card.py')
               
    
                            
                            
                            
def config(filename='./dags/database.ini', section='mysql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def connect(query,df_current):
    """ Connect to the MySQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the MySQL server
        print('Connecting to the MySQL database...')
        conn = mysql.connector.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
    
        
        if "SELECT" in query:
            df_mysql = pd.read_sql_query(query, con=conn)
            cur.close()
            
            
            return df_mysql
        
        elif "INSERT" in query:
            
            start=int(df_current['id_vulnerability'].iloc[0])
          
            for i in range(start ,len(df_current)+start): 
                
                values=(df_current['id_vulnerability'][i],dt.now(),df_current['nm_squad'][i],df_current['ds_title'][i],df_current['nm_repository'][i],df_current['in_criticity'][i],df_current['dt_created'][i],df_current['dt_closed'][i],df_current['st_vulnerability'][i],df_current['in_deadline'][i],df_current['ds_url_issue'][i],df_current['nm_source_data'][i],df_current['tool'][i],df_current['cd_month_start'][i],df_current['cd_month_end'][i])

                cur.execute(query,
                            values)

            conn.commit()
            cur.close()
            
        else:
            

            cur.execute(query)

            conn.commit()
            
            cur.close()
            
    except (Exception, mysql.connector.Error) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
            
    
    
##### TASKS AIRFLOW ######
    

t1 = PythonOperator(
   task_id='snyk-sast-data',
   python_callable=get_snyk_data,
   dag=dag
)

t2 = PythonOperator(
   task_id='gitlab-dast-data',
   python_callable=get_gitlab_data,
   dag=dag
)

t3 = PythonOperator(
   task_id='github-sca-data',
   python_callable=get_github_data,
   dag=dag
)

t4 = PythonOperator(
   task_id='generate-csv-data',
   python_callable=generate_csv_data,
   dag=dag
)

t5 = PythonOperator(
   task_id='add-db-data',
   python_callable=add_db_data,
   dag=dag
)

t6 = PythonOperator(
   task_id='generate-card-trello',
   python_callable=generate_card_trello,
   dag=dag
)



# Tarefas
[t1,t2,t3] >> t4 >> t5 >> t6

