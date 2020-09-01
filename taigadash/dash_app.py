import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


import pandas as pd
import psycopg2
from flask import Flask

SQL_ISSUES = '''
select p.id, s.name, i.subject, i.created_date, i.modified_date from issues_issue i 
inner join projects_project p on p.id = i.project_id
inner join projects_taskstatus s on s.id = i.status_id;
'''

con = psycopg2.connect(database='taiga', user='taiga_consulta')
df = pd.read_sql(SQL_ISSUES, con=con)

