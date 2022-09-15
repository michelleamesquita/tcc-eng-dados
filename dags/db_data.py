import os
import sys

# os.system(f'pip install sqlalchemy')
# os.system(f'pip install config')
# os.system(f'pip install mysql-connector-python')

import mysql.connector
import config
from configparser import ConfigParser
import pandas as pd
from datetime import datetime as dt
from sqlalchemy import create_engine

pd.options.mode.chained_assignment = None

query=sys.argv[0]

df_final=sys.argv[0]



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
            
            start=int(df_current['id_vulnerability'][0])
            # print(start)
            for i in range(start ,len(df_current)+start): 
            # for i in range(0 ,len(df_diff),20):
                values=(df_current['id_vulnerability'][i],dt.now(),df_current['nm_squad'][i],df_current['ds_title'][i],df_current['nm_repository'][i],df_current['in_criticity'][i],df_current['dt_created'][i],df_current['dt_closed'][i],df_current['st_vulnerability'][i],df_current['in_deadline'][i],df_current['ds_url_issue'][i],df_current['nm_source_data'][i],df_current['tool'][i],df_current['cd_month_start'][i],df_current['cd_month_end'][i])
#                 records = df_diff[i:i+20].to_records(index=False)

#                 result = list(records)
                
#                 print(result)
                
#                 cur.executemany(query,
#                             result)
                cur.execute(query,
                            values)

            conn.commit()
            cur.close()
            
        else:
            

            cur.execute(query)

            conn.commit()
            
            cur.close()
            
       
	# close the communication with the PostgreSQL
        # return df_postgrees
        # cur.close()
    except (Exception, mysql.connector.Error) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
            
            
df_db = connect(query,df_final)